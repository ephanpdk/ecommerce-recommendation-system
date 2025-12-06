from fastapi import APIRouter, HTTPException
import json
import os

router = APIRouter(prefix="/cluster", tags=["Cluster"])

BASE_DIR = "/code/app/ml"
METRICS_FILE = f"{BASE_DIR}/model_metrics.json"

@router.get("/metrics")
def get_model_metrics():
    if not os.path.exists(METRICS_FILE):
        return {"error": "Metrics file not found"}
    try:
        with open(METRICS_FILE, "r") as f:
            return json.load(f)
    except Exception as e:
        return {"error": str(e)}