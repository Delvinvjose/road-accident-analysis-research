from pathlib import Path
import joblib, pandas as pd, numpy as np
import math

BASE_DIR = Path(__file__).resolve().parent.parent
MODEL_PATH = BASE_DIR / "models" / "accident_model.pkl"

# 28 columns
RAW_ALL = [
    'snowfall','towing_and_articulation','precipitation','driver_home_area_type',
    'relative_humidity_2m','time_group','vehicle_type','rain','surface_pressure',
    'temperature_2m','driver_distance_banding','windgusts_10m','driver_imd_decile',
    'apparent_temperature','cloudcover','cloudcover_low','sex_of_driver',
    'winddirection_10m','windspeed_10m','journey_purpose_of_driver','cloudcover_high',
    'cloudcover_mid','day_of_week','dewpoint_2m','age_of_vehicle','engine_capacity_cc',
    'age_of_driver','age_band_of_driver'
]

_model = None
_expected = None

def _maybe_expected(m):
    names = None
    if hasattr(m, "feature_names_in_"):  # sklearn API
        names = list(m.feature_names_in_)
    elif hasattr(m, "feature_name_") and m.feature_name_:
        names = list(m.feature_name_)
    elif hasattr(m, "get_booster"):
        try:
            b = m.get_booster()
            if getattr(b, "feature_names", None):
                names = list(b.feature_names)
        except Exception:
            pass
    return names or RAW_ALL

def load_model():
    global _model, _expected
    if _model is None:
        if not MODEL_PATH.exists():
            raise FileNotFoundError(f"Model not found at {MODEL_PATH}")
        _model = joblib.load(MODEL_PATH)
        _expected = _maybe_expected(_model)

        # guard against pre-encoded matrices (hundreds of features)
        n_in = int(getattr(_model, "n_features_in_", 0)) if hasattr(_model, "n_features_in_") else 0
        if (n_in and n_in > 60) or (not n_in and len(_expected) > 60):
            raise RuntimeError(
                f"Model expects {n_in or len(_expected)} features (likely pre-encoded). "
                "Retrain/export on the 28 raw columns, or save a scikit-learn Pipeline."
            )
    return _model

def _row_df(feat: dict) -> pd.DataFrame:
    m = load_model()
    cols = _expected if set(_expected) == set(RAW_ALL) else RAW_ALL
    row = {}
    for c in cols:
        v = feat.get(c, None)
        try: row[c] = float(v) if v not in (None, "") else np.nan
        except Exception: row[c] = np.nan
    X = pd.DataFrame([row], columns=cols).fillna(-1)
    return X

def _sigmoid(x):
    try: return 1.0 / (1.0 + math.exp(-float(x)))
    except Exception: return None

def predict(features: dict):
    model = load_model()
    X = _row_df(features)
    y = model.predict(X)[0]
    proba = None
    if hasattr(model, "predict_proba"):
        try: proba = float(model.predict_proba(X)[0][-1])
        except Exception: pass
    elif hasattr(model, "decision_function"):
        try: proba = _sigmoid(model.decision_function(X)[0])
        except Exception: pass
    return float(y), proba
