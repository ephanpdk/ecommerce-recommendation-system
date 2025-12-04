from sqlalchemy import Column, Integer, String, Float
from app.database import Base

class User(Base):
    __tablename__ = "users"

    user_id = Column(Integer, primary_key=True, index=True)
    name = Column(String)
    preferred_category = Column(String)
    second_category = Column(String)
    preferred_style = Column(String)
    recency = Column(Integer)
    frequency = Column(Integer)
    monetary = Column(Integer)
    avg_items = Column(Float)
    unique_products = Column(Integer)
    wishlist_count = Column(Integer)
    add_to_cart_count = Column(Integer)
    page_views = Column(Integer)
    cluster_id = Column(Integer)