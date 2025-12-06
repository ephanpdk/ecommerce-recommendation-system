from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from fastapi.encoders import jsonable_encoder
import joblib
import pandas as pd
import numpy as np
import json
import os
import random
from app.database import get_db
from app.models.product import Product
from app.models.log import PredictionLog
from app.models.user import User
from app.schemas.recommend import PredictionRequest
from app.routers.auth import get_current_user

router = APIRouter(prefix="/recommend", tags=["Recommendation"])

BASE_DIR = "/code/app/ml"
METRICS_FILE = f"{BASE_DIR}/model_metrics.json"

# Global Cache
models = {"scaler": None, "kmeans": None, "topN": {}, "meta": {}}

def load_models():
    try:
        models["scaler"] = joblib.load(f"{BASE_DIR}/scaler_preproc.joblib")
        models["kmeans"] = joblib.load(f"{BASE_DIR}/kmeans_k2.joblib")
        models["topN"] = joblib.load(f"{BASE_DIR}/topN_by_cluster.joblib")
        if os.path.exists(METRICS_FILE):
            with open(METRICS_FILE, "r") as f:
                models["meta"] = json.load(f)
        print("✅ Models loaded successfully")
    except Exception as e:
        print(f"⚠️ Model loading warning: {e}")

load_models()

@router.post("/user")
def recommend_user(
    data: PredictionRequest, 
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    # Reload safety check
    if not models["scaler"] or not models["kmeans"]:
        load_models()
        if not models["scaler"]:
            raise HTTPException(status_code=500, detail="Model AI belum siap.")

    input_data = data.dict()
    df = pd.DataFrame([input_data])
    df["Monetary_Log"] = np.log1p(df["Monetary"])

    use_cols = [
        "Recency", "Frequency", "Monetary_Log", "Avg_Items",
        "Unique_Products", "Wishlist_Count", "Add_to_Cart_Count", "Page_Views"
    ]

    try:
        # 1. AI Processing
        X_scaled = models["scaler"].transform(df[use_cols])
        cluster = int(models["kmeans"].predict(X_scaled)[0])
        
        # 2. Distance & Confidence
        centroids = models["kmeans"].cluster_centers_
        # Pakai Euclidean Distance manual yg lebih stabil daripada transform
        distances = []
        for i, center in enumerate(centroids):
            dist = np.linalg.norm(X_scaled[0] - center)
            distances.append({"cluster": i, "distance": round(float(dist), 4)})
        
        distances.sort(key=lambda x: x['distance'])
        nearest = distances[0]
        second = distances[1] if len(distances) > 1 else None
        
        # Confidence calc
        margin = (second['distance'] - nearest['distance']) if second else 0
        confidence = min(100, max(50, (margin * 50) + 50))

        # 3. Explainability
        readable_cols = models["meta"].get("feature_readable", use_cols)
        z_scores = X_scaled[0]
        drivers = []
        
        for i, val in enumerate(z_scores):
            score = float(val)
            if abs(score) < 0.8: continue # Filter noise
            
            drivers.append({
                "feature": readable_cols[i] if i < len(readable_cols) else use_cols[i],
                "score": round(score, 2),
                "description": "High" if score > 0 else "Low",
                "sentiment": "positive" if score > 0 else "negative",
                "impact": abs(score)
            })
        
        drivers.sort(key=lambda x: x['impact'], reverse=True)

        # 4. Products
        raw_recs = models["topN"].get(cluster, [])
        # Handle format list of dicts vs list of ints
        product_ids = []
        if raw_recs:
            if isinstance(raw_recs[0], dict):
                product_ids = [item['product_id'] for item in raw_recs]
            else:
                product_ids = [int(x) for x in raw_recs]

        final_recs = []
        if product_ids:
            db_products = db.query(Product).filter(Product.product_id.in_(product_ids)).all()
            price_base = {0: 15, 1: 50, 2: 150, 3: 800}.get(cluster, 50)
            
            for prod in db_products:
                random.seed(prod.product_id)
                final_recs.append({
                    "product_id": prod.product_id,
                    "name": prod.name,
                    "category": prod.category,
                    "price": round(price_base * random.uniform(0.8, 1.2), 2),
                    "rating": round(random.uniform(4.0, 5.0), 1)
                })

        if not final_recs:
             final_recs = [{"product_id": 0, "name": "No Recommendations", "category": "General", "price": 0, "rating": 0}]

        recs_clean = jsonable_encoder(final_recs)

        # 5. Logging
        try:
            log = PredictionLog(user_id=current_user.user_id, predicted_cluster=cluster, recommended_items=recs_clean)
            db.add(log)
            db.commit()
        except:
            db.rollback()

        # RETURN RESPONSE (PASTIKAN STRUKTUR INI SAMA DENGAN UI)
        return {
            "cluster": cluster,
            "metrics": {
                "confidence_score": round(confidence, 1),
                "distance_to_centroid": nearest['distance'],
                "feature_drivers": drivers[:3],
                "all_distances": distances
            },
            "recommendations": recs_clean
        }

    except Exception as e:
        print(f"🔥 ERROR DI BACKEND: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Internal Error: {str(e)}")