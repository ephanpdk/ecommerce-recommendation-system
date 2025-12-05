from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional
from app.database import get_db
from app.models.product import Product
from pydantic import BaseModel

router = APIRouter(prefix="/products", tags=["Products"])

class ProductResponse(BaseModel):
    product_id: int
    name: str
    category: str
    style: Optional[str] = None

    class Config:
        from_attributes = True

@router.get("/", response_model=List[ProductResponse])
def get_all_products(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    products = db.query(Product).offset(skip).limit(limit).all()
    return products

@router.get("/{pid}", response_model=ProductResponse)
def get_product_detail(pid: int, db: Session = Depends(get_db)):
    product = db.query(Product).filter(Product.product_id == pid).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    return product