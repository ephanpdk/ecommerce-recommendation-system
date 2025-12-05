from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from fastapi.encoders import jsonable_encoder
import joblib
import pandas as pd
import numpy as np
from app.database import get_db
from app.models.log import PredictionLog
from app.schemas.recommend import PredictionRequest, RecommendationResponse

router = APIRouter(prefix="/recommend", tags=["Recommendation"])

try:
    scaler = joblib.load("app/ml/scaler_preproc.joblib")
    kmeans = joblib.load("app/ml/kmeans_k2.joblib")
    topN = joblib.load("app/ml/topN_by_cluster.joblib")
except Exception as e:
    scaler, kmeans, topN = None, None, {}

@router.get("/by_cluster/{cid}")
def recommend_by_cluster(cid: int):
    return {"cluster": cid, "recommendations": topN.get(cid, [])}

@router.post("/user", response_model=RecommendationResponse)
def recommend_user(data: PredictionRequest, db: Session = Depends(get_db)):
    if not scaler or not kmeans:
        raise HTTPException(status_code=500, detail="ML Models not loaded")

    input_data = data.dict()
    df = pd.DataFrame([input_data])
    df["Monetary_Log"] = np.log1p(df["Monetary"])

    use_cols = [
        "Recency", "Frequency", "Monetary_Log", "Avg_Items",
        "Unique_Products", "Wishlist_Count", "Add_to_Cart_Count", "Page_Views"
    ]

    try:
        X = scaler.transform(df[use_cols])
        cluster_prediction = kmeans.predict(X)[0]
        cluster = int(cluster_prediction)
        
        raw_recs = topN.get(cluster, [])
        final_recs = []
        
        if raw_recs:
            first_item = raw_recs[0]
            
            if isinstance(first_item, (int, np.integer, float)):
                for pid in raw_recs:
                    final_recs.append({
                        "product_id": int(pid),
                        "name": f"Product Item ID {pid}"
                    })
            elif isinstance(first_item, dict):
                final_recs = raw_recs
            else:
                final_recs = []

        recs_clean = jsonable_encoder(final_recs)

        new_log = PredictionLog(
            user_id=0, 
            predicted_cluster=cluster,
            recommended_items=recs_clean
        )
        db.add(new_log)
        db.commit()

        return {
            "cluster": cluster,
            "recommendations": recs_clean
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))