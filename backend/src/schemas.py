from pydantic import BaseModel, Field
from typing import Optional

# Schema 1 — What Stage 1 LLM extracts from user text
class ExtractedFeatures(BaseModel):
    overall_qual: Optional[int] = Field(None, ge=1, le=10)
    gr_liv_area: Optional[float] = Field(None, gt=0)
    garage_cars: Optional[int] = Field(None, ge=0)
    total_bsmt_sf: Optional[float] = Field(None, ge=0)
    first_flr_sf: Optional[float] = Field(None, ge=0)
    year_built: Optional[int] = Field(None, ge=1800, le=2025)
    year_remod_add: Optional[int] = Field(None, ge=100, le=2025)
    full_bath: Optional[int] = Field(None, ge=0)
    neighborhood: Optional[str] = None
    kitchen_qual: Optional[str] = None
    bsmt_qual: Optional[str] = None

    missing_fields: list[str] = []
    confidence: str = "low"


# Schema 2 — Final response to the user
class PredictionResponse(BaseModel):
    extracted_features: ExtractedFeatures
    predicted_price: Optional[float] = None
    interpretation: Optional[str] = None
    error: Optional[str] = None