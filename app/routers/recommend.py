from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from fastapi.encoders import jsonable_encoder
import joblib
import pandas as pd
import numpy as np
from app.database import get_db
from app.models.product import Product
from app.models.log import PredictionLog
from app.schemas.recommend import PredictionRequest, RecommendationResponse

router = APIRouter(prefix="/recommend", tags=["Recommendation"])

try:
    scaler = joblib.load("app/ml/scaler_preproc.joblib")
    kmeans = joblib.load("app/ml/kmeans_k2.joblib")
    topN = joblib.load("app/ml/topN_by_cluster.joblib")
except Exception:
    scaler, kmeans, topN = None, None, {}

@router.post("/user", response_model=RecommendationResponse)
def recommend_user(data: PredictionRequest, db: Session = Depends(get_db)):
    if not scaler or not kmeans:
        raise HTTPException(status_code=500, detail="Model ML belum dimuat")

    input_data = data.dict()
    df = pd.DataFrame([input_data])
    df["Monetary_Log"] = np.log1p(df["Monetary"])

    use_cols = [
        "Recency", "Frequency", "Monetary_Log", "Avg_Items",
        "Unique_Products", "Wishlist_Count", "Add_to_Cart_Count", "Page_Views"
    ]

    try:
        X = scaler.transform(df[use_cols])
        cluster = int(kmeans.predict(X)[0])
        
        raw_recs = topN.get(cluster, [])
        product_ids = []

        if raw_recs:
            if isinstance(raw_recs[0], dict):
                 product_ids = [item['product_id'] for item in raw_recs]
            elif isinstance(raw_recs[0], (int, np.integer, float)):
                 product_ids = [int(x) for x in raw_recs]
        
        final_recs = []
        
        if product_ids:
            db_products = db.query(Product).filter(Product.product_id.in_(product_ids)).all()
            for prod in db_products:
                final_recs.append({
                    "product_id": prod.product_id,
                    "name": prod.name,
                    "category": prod.category
                })
        
        if not final_recs:
             final_recs = [{"product_id": 0, "name": "Tidak ada rekomendasi spesifik"}]

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