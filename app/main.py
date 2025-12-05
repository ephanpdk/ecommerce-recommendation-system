from fastapi import FastAPI
from app.routers import cluster, recommend, product
from app.database import Base, engine

Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="E-commerce Recommender API",
    version="1.0.0"
)

app.include_router(cluster.router)
app.include_router(recommend.router)
app.include_router(product.router)

@app.get("/")
def root():
    return {"message": "E-commerce Recommender API Running"}