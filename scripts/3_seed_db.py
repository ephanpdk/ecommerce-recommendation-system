import pandas as pd
from sqlalchemy import create_engine
import sys
import os

sys.path.append(os.getcwd())

from app.config import DATABASE_URL

def seed_products():
    csv_path = "app/ml/products_dummy.csv"
    if not os.path.exists(csv_path):
        return

    df = pd.read_csv(csv_path)
    df = df.rename(columns={"product_name": "name"})
    
    if "style" not in df.columns:
        df["style"] = "General"

    engine = create_engine(DATABASE_URL)
    
    try:
        df.to_sql('products', engine, if_exists='append', index=False)
        print("Seeding Berhasil")
    except Exception as e:
        print(e)

if __name__ == "__main__":
    seed_products()