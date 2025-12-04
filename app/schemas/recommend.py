from pydantic import BaseModel
from typing import List, Optional

class PredictionRequest(BaseModel):
    Recency: int
    Frequency: int
    Monetary: float
    Avg_Items: float
    Unique_Products: int
    Wishlist_Count: int
    Add_to_Cart_Count: int
    Page_Views: int

class RecommendationResponse(BaseModel):
    cluster: int
    recommendations: List[dict]