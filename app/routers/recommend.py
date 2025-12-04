from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
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
    print(f"Error loading ML models: {e}")

@router.get("/by_cluster/{cid}")
def recommend_by_cluster(cid: int):
    cid = int(cid)
    if cid not in topN:
        raise HTTPException(status_code=404, detail="Cluster not found")

    return {
        "cluster": cid,
        "recommendations": topN[cid]
    }

@router.post("/user", response_model=RecommendationResponse)
def recommend_user(data: PredictionRequest, db: Session = Depends(get_db)):
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
        
        recs = topN.get(cluster, [])
        
        # Log to Database
        new_log = PredictionLog(
            user_id=0, 
            predicted_cluster=cluster,
            recommended_items=recs
        )
        db.add(new_log)
        db.commit()

        return {
            "cluster": cluster,
            "recommendations": recs
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))