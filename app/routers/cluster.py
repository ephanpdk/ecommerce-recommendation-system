from fastapi import APIRouter
import joblib
import pandas as pd
import numpy as np

router = APIRouter(prefix="/cluster", tags=["Cluster"])

scaler = joblib.load("app/ml/scaler_preproc.joblib")
kmeans = joblib.load("app/ml/kmeans_k2.joblib")

@router.post("/predict")
def predict_cluster(data: dict):
    df = pd.DataFrame([data])

    df["Monetary_Log"] = np.log1p(df["Monetary"])

    use_cols = [
        "Recency","Frequency","Monetary_Log","Avg_Items",
        "Unique_Products","Wishlist_Count","Add_to_Cart_Count","Page_Views"
    ]

    X = scaler.transform(df[use_cols])
    cluster = int(kmeans.predict(X)[0])

    return {"cluster": cluster}
