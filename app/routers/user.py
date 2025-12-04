from fastapi import APIRouter, HTTPException
import joblib
import pandas as pd
import numpy as np
from app.schemas.recommend import PredictionRequest

router = APIRouter(prefix="/cluster", tags=["Cluster"])

try:
    scaler = joblib.load("app/ml/scaler_preproc.joblib")
    kmeans = joblib.load("app/ml/kmeans_k2.joblib")
except Exception as e:
    print(f"Error loading models: {e}")

@router.post("/predict")
def predict_cluster(data: PredictionRequest):
    input_data = data.dict()
    df = pd.DataFrame([input_data])
    
    df["Monetary_Log"] = np.log1p(df["Monetary"])
    
    use_cols = [
        "Recency","Frequency","Monetary_Log","Avg_Items",
        "Unique_Products","Wishlist_Count","Add_to_Cart_Count","Page_Views"
    ]
    
    try:
        X = scaler.transform(df[use_cols])
        cluster = int(kmeans.predict(X)[0])
        return {"cluster": cluster}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))