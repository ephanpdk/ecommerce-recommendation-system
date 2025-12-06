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

models = {"scaler": None, "kmeans": None, "topN": {}, "meta": {}}

def load_ml_components():
    try:
        models["scaler"] = joblib.load(f"{BASE_DIR}/scaler_preproc.joblib")
        models["kmeans"] = joblib.load(f"{BASE_DIR}/kmeans_k2.joblib")
        models["topN"] = joblib.load(f"{BASE_DIR}/topN_by_cluster.joblib")
        if os.path.exists(METRICS_FILE):
            with open(METRICS_FILE, "r") as f:
                models["meta"] = json.load(f)
    except Exception as e:
        print(f"Warning: {e}")

load_ml_components()

@router.post("/user")
def recommend_user(
    data: PredictionRequest, 
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if not models["scaler"] or not models["kmeans"]:
        load_ml_components()
        if not models["scaler"]:
            raise HTTPException(status_code=500, detail="AI Model not ready")

    input_data = data.dict()
    df = pd.DataFrame([input_data])
    df["Monetary_Log"] = np.log1p(df["Monetary"])

    use_cols = [
        "Recency", "Frequency", "Monetary_Log", "Avg_Items",
        "Unique_Products", "Wishlist_Count", "Add_to_Cart_Count", "Page_Views"
    ]
    readable_cols = models["meta"].get("feature_readable", use_cols)
    cluster_names = ["Newbie", "Window Shopper", "Loyalist", "Sultan"]

    try:
        X_scaled = models["scaler"].transform(df[use_cols])
        cluster = int(models["kmeans"].predict(X_scaled)[0])
        
        dist_matrix = models["kmeans"].transform(X_scaled)[0]
        
        distances = []
        for i, dist in enumerate(dist_matrix):
            distances.append({"cluster": i, "distance": round(float(dist), 4)})
        
        distances.sort(key=lambda x: x['distance'])
        nearest = distances[0]
        second = distances[1] if len(distances) > 1 else None
        
        margin = second['distance'] - nearest['distance'] if second else 0
        confidence = min(100, max(50, (margin * 50) + 50))

        z_scores = X_scaled[0]
        drivers = []
        anomalies = []
        
        for i, val in enumerate(z_scores):
            score = float(val)
            impact = abs(score)
            
            if impact > 2.0:
                anomalies.append(f"{readable_cols[i]} is unusually {'high' if score > 0 else 'low'}")
            
            if impact < 0.5: continue
            
            drivers.append({
                "feature": readable_cols[i],
                "score": round(score, 2),
                "description": "High" if score > 0 else "Low",
                "sentiment": "positive" if score > 0 else "negative",
                "impact": impact
            })
        
        drivers.sort(key=lambda x: x['impact'], reverse=True)
        
        explanations = {
            "why": f"Classified as {cluster_names[cluster]} primarily due to {drivers[0]['feature'] if drivers else 'balanced traits'}.",
            "compare": f"Nearest alternative is {cluster_names[second['cluster']]} (Dist: {second['distance']})" if second else "No close alternative.",
            "anomaly": anomalies[0] if anomalies else "Behavior is within normal distribution."
        }

        raw_recs = models["topN"].get(cluster, [])
        product_ids = [item['product_id'] for item in raw_recs] if raw_recs and isinstance(raw_recs[0], dict) else []
        
        final_recs = []
        if product_ids:
            db_products = db.query(Product).filter(Product.product_id.in_(product_ids)).all()
            base_mult = {0: 10, 1: 50, 2: 150, 3: 500}
            
            for prod in db_products:
                random.seed(prod.product_id)
                final_recs.append({
                    "product_id": prod.product_id,
                    "name": prod.name,
                    "category": prod.category,
                    "price": round(base_mult.get(cluster, 50) * random.uniform(0.8, 1.2), 2),
                    "rating": round(random.uniform(3.5, 5.0), 1)
                })

        if not final_recs:
             final_recs = [{"product_id": 0, "name": "Item", "category": "General", "price": 0, "rating": 0}]

        recs_clean = jsonable_encoder(final_recs)

        try:
            log = PredictionLog(user_id=current_user.user_id, predicted_cluster=cluster, recommended_items=recs_clean)
            db.add(log)
            db.commit()
        except:
            db.rollback()

        return {
            "cluster": cluster,
            "metrics": {
                "confidence_score": round(confidence, 1),
                "distance_to_centroid": nearest['distance'],
                "feature_drivers": drivers[:3],
                "explanations": explanations,
                "all_distances": distances
            },
            "recommendations": recs_clean
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))