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
from app.models.log import PredictionLog
from app.models.user import User
from app.schemas.recommend import PredictionRequest
from app.routers.auth import get_current_user

router = APIRouter(prefix="/recommend", tags=["Recommendation"])

BASE_DIR = "/code/app/ml"
METRICS_FILE = f"{BASE_DIR}/model_metrics.json"

# Global Model Cache
models = {"scaler": None, "kmeans": None, "topN": {}, "meta": {}}

def load_models():
    try:
        # Pastikan path ini sesuai dengan container Docker lo
        models["scaler"] = joblib.load(f"{BASE_DIR}/scaler_preproc.joblib")
        models["kmeans"] = joblib.load(f"{BASE_DIR}/kmeans_k2.joblib")
        models["topN"] = joblib.load(f"{BASE_DIR}/topN_by_cluster.joblib")
        
        if os.path.exists(METRICS_FILE):
            with open(METRICS_FILE, "r") as f:
                models["meta"] = json.load(f)
        print("✅ Models loaded in Router")
    except Exception as e:
        print(f"⚠️ Warning load model: {e}")

# Load saat startup (atau worker pertama kali jalan)
load_models()

@router.post("/user")
def recommend_user(data: PredictionRequest, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    # 1. Safety Check (Lazy Loading)
    if not models["scaler"] or not models["kmeans"]:
        load_models()
        if not models["scaler"]:
            raise HTTPException(status_code=503, detail="AI Models not ready. Please check backend logs.")

    try:
        # 2. Prepare Data
        # Mapping input Pydantic ke DataFrame
        input_data = data.dict()
        df = pd.DataFrame([input_data])
        
        # Feature Engineering (Wajib sama dengan Training!)
        df["Monetary_Log"] = np.log1p(df["Monetary"])
        
        use_cols = ["Recency", "Frequency", "Monetary_Log", "Avg_Items", "Unique_Products", "Wishlist_Count", "Add_to_Cart_Count", "Page_Views"]
        
        # 3. Predict Cluster
        X_scaled = models["scaler"].transform(df[use_cols])
        cluster = int(models["kmeans"].predict(X_scaled)[0])
        
        # 4. Distance & Confidence Calculation
        centroids = models["kmeans"].cluster_centers_
        # Hitung jarak user ke semua centroid
        dist_vec = np.linalg.norm(X_scaled[0] - centroids, axis=1)
        
        nearest_dist = dist_vec[cluster]
        # Cari jarak terdekat kedua untuk margin confidence
        sorted_dist = np.sort(dist_vec)
        second_dist = sorted_dist[1] if len(sorted_dist) > 1 else nearest_dist + 1
        
        # Rumus Confidence: Semakin jauh selisih juara 1 dan 2, semakin yakin.
        margin = second_dist - nearest_dist
        confidence = min(99.9, max(50.0, 50 + (margin * 40)))

        # 5. BUSINESS LOGIC & EXPLAINABILITY
        readable_cols = models["meta"].get("feature_readable", use_cols)
        z_scores = X_scaled[0]
        
        # Cari Driver (Penyebab User masuk cluster ini)
        drivers = []
        for i, val in enumerate(z_scores):
            score = float(val)
            # Hanya ambil fitur yang menonjol (Z-score > 0.8 atau < -0.8)
            if abs(score) < 0.6: continue 
            
            drivers.append({
                "feature": readable_cols[i] if i < len(readable_cols) else use_cols[i],
                "score": round(score, 2),
                "description": "High" if score > 0 else "Low",
                "sentiment": "positive" if score > 0 else "negative",
                "impact": abs(score) # Untuk sorting
            })
        
        # Urutkan berdasarkan impact terbesar
        drivers.sort(key=lambda x: x['impact'], reverse=True)
        top_drivers = drivers[:3]

        # Generate Narrative (Explainability)
        cluster_names = models["meta"].get("cluster_names", ["Newbie", "Window Shopper", "Loyalist", "Sultan"])
        current_name = cluster_names[cluster]
        
        # Why
        why_text = f"User fits the {current_name} profile."
        if top_drivers:
            why_text = f"Classified as {current_name} mainly due to {top_drivers[0]['description']} {top_drivers[0]['feature']}."
            
        # Compare
        compare_text = "Distinct behavior pattern."
        if len(sorted_dist) > 1:
            # Cari index cluster terdekat kedua
            second_cluster_idx = np.where(dist_vec == second_dist)[0][0]
            compare_text = f"Close to {cluster_names[second_cluster_idx]} profile (Margin: {round(margin, 2)})."

        # Anomaly / Action
        anomaly_text = "Behavior is consistent."
        # Contoh Logic Anomaly: High Spend tapi Low Visit (Impulsive)
        if data.Monetary > 1000 and data.Page_Views < 5:
            anomaly_text = "Action: Impulsive Buyer! Show 'Buy Now' buttons prominently."
        elif data.Recency > 60 and cluster == 3: # Sultan yang mau pergi
            anomaly_text = "URGENT: VIP Churn Risk. Trigger personal assistance."

        # 6. RECOMMENDATIONS (FIXED: TRUST THE AI)
        # Ambil langsung dari Joblib yang sudah dihitung pakai Cosine Similarity
        # Perhatikan: Key di joblib mungkin string atau int, kita handle dua-duanya
        recs_list = models["topN"].get(cluster, [])
        if not recs_list:
            recs_list = models["topN"].get(str(cluster), [])
            
        # Jika masih kosong (fallback), return dummy structure
        if not recs_list:
             recs_list = [{"product_id": 0, "name": "General Item", "category": "General", "price": 10.0, "reason": "Fallback"}]

        # Pastikan format JSON safe
        final_recs = jsonable_encoder(recs_list)

        # 7. LOGGING (Async capable)
        # Jangan sampai logging error bikin user gagal dapat rekomendasi
        try:
            log_entry = PredictionLog(
                user_id=current_user.user_id,
                predicted_cluster=cluster,
                recommended_items=final_recs # Simpan JSON hasil rekomendasi
            )
            db.add(log_entry)
            db.commit()
        except Exception as log_err:
            print(f"Logging Failed: {log_err}")
            db.rollback()

        # 8. FINAL RESPONSE
        return {
            "cluster": cluster,
            "metrics": {
                "confidence_score": round(confidence, 1),
                "distance_to_centroid": round(float(nearest_dist), 4),
                "feature_drivers": top_drivers,
                "explanations": {
                    "why": why_text,
                    "compare": compare_text,
                    "anomaly": anomaly_text
                }
            },
            "recommendations": final_recs
        }

    except Exception as e:
        print(f"Prediction Error: {e}")
        # Return 500 biar frontend tau ada yang salah, jangan 200 tapi isinya error text
        raise HTTPException(status_code=500, detail=f"Internal Logic Error: {str(e)}")