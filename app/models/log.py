from sqlalchemy import Column, Integer, JSON, DateTime
from sqlalchemy.sql import func
from app.database import Base

class PredictionLog(Base):
    __tablename__ = "prediction_logs"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer)
    predicted_cluster = Column(Integer)
    recommended_items = Column(JSON)
    created_at = Column(DateTime(timezone=True), server_default=func.now())