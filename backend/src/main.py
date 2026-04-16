import os
import json
import httpx
import asyncio
from fastapi import FastAPI
from pydantic import ValidationError
from schemas import ExtractedFeatures, PredictionResponse
from ml_pipeline import predict_price, TRAINING_STATS
from prompts import STAGE1_PROMPT_V1, STAGE1_PROMPT_V2, STAGE2_PROMPT
from dotenv import load_dotenv
load_dotenv()


app = FastAPI()

GROQ_API_KEY = os.getenv("GROQ_API_KEY")
MODEL = "llama-3.3-70b-versatile" 
print(f"GROQ API KEY loaded: {bool(GROQ_API_KEY)}")

# ── LLM call helper ────────────────────────────────────────────────────────
async def call_llm(prompt: str) -> str:
    async with httpx.AsyncClient(timeout=30) as client:
        response = await client.post(
            "https://api.groq.com/openai/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {GROQ_API_KEY}",
                "Content-Type": "application/json",
            },
            json={
                "model": MODEL,
                "max_tokens": 1024,
                "messages": [{"role": "user", "content": prompt}]
            }
        )
        return response.json()["choices"][0]["message"]["content"]


# ── Stage 1 — Extract features ─────────────────────────────────────────────
async def run_stage1(user_query: str) -> ExtractedFeatures:
    prompt_v1 = STAGE1_PROMPT_V1.replace("{{user_query}}", user_query)
    
    raw_v1 = await call_llm(prompt_v1)
    print(f"V1 OUTPUT: {raw_v1}")

    try:
        data_v1 = json.loads(raw_v1)
    except json.JSONDecodeError:
        data_v1 = {}

    fields = [
        "overall_qual", "gr_liv_area", "garage_cars", "total_bsmt_sf",
         "first_flr_sf", "year_built", "year_remod_add",
        "full_bath", "neighborhood", "kitchen_qual", "bsmt_qual"
    ]

    missing = [f for f in fields if data_v1.get(f) is None]
    total_found = len(fields) - len(missing)
    confidence = "high" if total_found >= 9 else "medium" if total_found >= 5 else "low"

    data_v1["missing_fields"] = missing
    data_v1["confidence"] = confidence
    print(f"V1 RESULT: {data_v1}")

    try:
        return ExtractedFeatures(**data_v1)
    except ValidationError:
        return ExtractedFeatures(missing_fields=fields, confidence="low")

async def run_stage2(features: ExtractedFeatures, predicted_price: float) -> str:
    prompt = STAGE2_PROMPT.format(
        features=features.model_dump(),
        predicted_price=predicted_price,
        **TRAINING_STATS
    )
    return await call_llm(prompt)
@app.post("/predict")
async def predict(query: dict) -> PredictionResponse:
    user_query = query.get("query", "")

    try:
        features = await run_stage1(user_query)

        if len(features.missing_fields) > 8:
            return PredictionResponse(
                extracted_features=features,
                error="Too many missing fields. Please provide more details."
            )

        price = predict_price(features.model_dump())
        interpretation = await run_stage2(features, price)

        return PredictionResponse(
            extracted_features=features,
            predicted_price=price,
            interpretation=interpretation
        )

    except Exception as e:
        return PredictionResponse(
            extracted_features=ExtractedFeatures(),
            error=str(e)
        )


@app.get("/health")
def health():
    return {"status": "ok"}

@app.post("/predict/complete")
async def predict_complete(query: dict) -> PredictionResponse:
    extracted = query.get("extracted_features", {})
    filled    = query.get("filled_features", {})

    try:
        # Merge extracted + filled
        merged = {**extracted, **filled}
        merged["missing_fields"] = []
        merged["confidence"] = "high"

        features = ExtractedFeatures(**merged)
        price = predict_price(features.model_dump())
        interpretation = await run_stage2(features, price)

        return PredictionResponse(
            extracted_features=features,
            predicted_price=price,
            interpretation=interpretation
        )

    except Exception as e:
        return PredictionResponse(
            extracted_features=ExtractedFeatures(),
            error=str(e)
        )