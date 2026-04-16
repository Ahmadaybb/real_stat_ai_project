# AI Real Estate Agent

An AI-powered home price estimator that lets you describe a property in plain English and get an instant ML-backed price prediction.

## How It Works

The pipeline runs in three stages:

1. **Natural Language Input** — You describe a property in free-form text (e.g. *"3 bedroom house built in 1995 with excellent kitchen and 2 car garage in NridgHt"*).
2. **LLM Feature Extraction** — A Groq-hosted `llama-3.3-70b-versatile` model reads your description and extracts the 11 structured features the model needs (quality scores, square footage, year built, neighborhood, etc.).
3. **ML Price Prediction** — An XGBoost regression model trained on the Ames, Iowa housing dataset predicts the sale price. A second LLM call then generates a human-readable interpretation of the result in context of the broader market.

If the LLM cannot extract some fields, the UI surfaces a form so you can fill them in manually before re-running the prediction.

## Project Structure

```
ai-real-estate-agent/
├── backend/
│   ├── data/
│   │   └── final_dataset.csv       # Ames housing training data
│   ├── models/
│   │   └── best_model.joblib       # Trained XGBoost model
│   └── src/
│       ├── main.py                 # FastAPI app (endpoints)
│       ├── ml_pipeline.py          # Model loading & predict_price()
│       ├── prompts.py              # LLM prompt templates (Stage 1 & 2)
│       └── schemas.py              # Pydantic request/response models
├── frontend/
│   └── ui.py                       # Streamlit UI
├── Dockerfile                      # Container for the FastAPI backend
├── pyproject.toml                  # Python dependencies (uv)
└── .env                            # Environment variables (not committed)
```

## Tech Stack

| Layer | Technology |
|---|---|
| Frontend | Streamlit |
| Backend API | FastAPI + Uvicorn |
| LLM | Groq API (`llama-3.3-70b-versatile`) |
| ML Model | XGBoost (scikit-learn pipeline) |
| Data | Ames Housing Dataset |
| Packaging | uv / pyproject.toml |
| Deployment | Docker (backend), Render |

## Features Extracted by the LLM

| Field | Description |
|---|---|
| `overall_qual` | Overall quality rating (1–10) |
| `gr_liv_area` | Above-ground living area (sqft) |
| `garage_cars` | Garage capacity (number of cars) |
| `total_bsmt_sf` | Total basement area (sqft) |
| `first_flr_sf` | First floor area (sqft) |
| `year_built` | Year of construction |
| `year_remod_add` | Year of last remodel |
| `full_bath` | Number of full bathrooms |
| `neighborhood` | Ames neighborhood code |
| `kitchen_qual` | Kitchen quality (Po/Fa/TA/Gd/Ex) |
| `bsmt_qual` | Basement quality (Po/Fa/TA/Gd/Ex) |

## API Endpoints

| Method | Path | Description |
|---|---|---|
| `POST` | `/predict` | Extract features from text, predict price |
| `POST` | `/predict/complete` | Predict using pre-extracted + manually filled features |
| `GET` | `/health` | Health check |

## Setup

### Prerequisites

- Python 3.12+
- [uv](https://github.com/astral-sh/uv) package manager
- A [Groq API key](https://console.groq.com/)

### Local Development

```bash
# 1. Clone the repo
git clone <repo-url>
cd ai-real-estate-agent

# 2. Install dependencies
uv sync

# 3. Set environment variables
echo "GROQ_API_KEY=your_key_here" > .env

# 4. Start the backend
uv run uvicorn backend.src.main:app --host 0.0.0.0 --port 8000 --reload

# 5. In a separate terminal, start the frontend
uv run streamlit run frontend/ui.py
```

The UI will be available at `http://localhost:8501` and the API at `http://localhost:8000`.

### Docker (Backend Only)

```bash
docker build -t ai-real-estate-backend .
docker run -p 8000:8000 -e GROQ_API_KEY=your_key_here ai-real-estate-backend
```

## Live Demo

The backend is deployed on Render: `https://real-stat-ai-project.onrender.com`
