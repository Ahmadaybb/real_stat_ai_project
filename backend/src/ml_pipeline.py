import joblib
import numpy as np
import pandas as pd
import os
from pathlib import Path

# Load model once at startup
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
model = joblib.load(os.path.join(BASE_DIR, "models", "best_model.joblib"))
#MODEL_PATH = Path(__file__).parent.parent / "models" / "best_model.joblib"
#model = joblib.load(MODEL_PATH)



# These are the exact column names the model was trained on
FEATURE_COLUMNS = [
    'Overall Qual',
    'Gr Liv Area',
    'Garage Cars',
    'Total Bsmt SF',
    '1st Flr SF',
    'Year Built',
    'Year Remod/Add',
    'Full Bath',
    'Neighborhood',
    'Kitchen Qual',
    'Bsmt Qual',
]

# Training data stats for Stage 2 context
TRAINING_STATS = {
    'median_price': 160099,
    'mean_price':   179194,
    'min_price':    12788,
    'max_price':    754999,
    'p25':          129424,
    'p75':          210000,
}

def predict_price(features: dict) -> float:
    # Default values for missing fields (use median/most common from training)
    defaults = {
    'Overall Qual':  6.0,
    'Gr Liv Area':   1440.0,
    'Garage Cars':   2.0,
    'Total Bsmt SF': 984.0,
    '1st Flr SF':    1082.0,
    'Year Built':    1972.0,
    'Year Remod/Add': 1992.0,
    'Full Bath':     2.0,
    'Neighborhood':  'NAmes',
    'Kitchen Qual':  'TA',
    'Bsmt Qual':     'TA',
    }
    
    row = {
        'Overall Qual':  features.get('overall_qual'),
        'Gr Liv Area':   features.get('gr_liv_area'),
        'Garage Cars':   features.get('garage_cars'),
        'Total Bsmt SF': features.get('total_bsmt_sf'),
        '1st Flr SF':    features.get('first_flr_sf'),
        'Year Built':    features.get('year_built'),
        'Year Remod/Add':features.get('year_remod_add'),
        'Full Bath':  features.get('full_bath'),
        'Neighborhood':  features.get('neighborhood'),
        'Kitchen Qual':  features.get('kitchen_qual'),
        'Bsmt Qual':     features.get('bsmt_qual'),
    }

    # Fill None values with defaults
    for key in row:
        if row[key] is None:
            row[key] = defaults[key]

    df = pd.DataFrame([row])
    log_price = model.predict(df)[0]
    return float(np.exp(log_price))