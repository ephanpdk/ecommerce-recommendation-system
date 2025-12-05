from sqlalchemy import Column, Integer, String, Float
from app.database import Base

class User(Base):
    __tablename__ = "users"

    user_id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=True)
    hashed_password = Column(String, nullable=True)
    
    name = Column(String, nullable=True)
    preferred_category = Column(String, nullable=True)
    second_category = Column(String, nullable=True)
    preferred_style = Column(String, nullable=True)
    recency = Column(Integer, default=0)
    frequency = Column(Integer, default=0)
    monetary = Column(Integer, default=0)
    avg_items = Column(Float, default=0.0)
    unique_products = Column(Integer, default=0)
    wishlist_count = Column(Integer, default=0)
    add_to_cart_count = Column(Integer, default=0)
    page_views = Column(Integer, default=0)
    cluster_id = Column(Integer, nullable=True)