import pandas as pd
import numpy as np
import random
from faker import Faker
import os

fake = Faker()

NUM_USERS = 1000 
NUM_PRODUCTS = 100

product_tiers = [
    {"tier": "Budget", "price_range": (5, 40), "tags": ["Essential", "Promo", "Best Value"]},
    {"tier": "Standard", "price_range": (50, 150), "tags": ["Popular", "Trending", "Daily"]},
    {"tier": "Premium", "price_range": (200, 800), "tags": ["High Quality", "Limited", "Bundle"]},
    {"tier": "Luxury", "price_range": (1000, 5000), "tags": ["Exclusive", "VIP", "Collector"]}
]

categories = ['Electronics', 'Fashion', 'Home & Living', 'Skincare', 'Automotive']
products = []

for i in range(NUM_PRODUCTS):
    tier_choice = random.choices(product_tiers, weights=[40, 30, 20, 10], k=1)[0]
    
    price = random.randint(*tier_choice["price_range"])
    cat = random.choice(categories)
    complexity = (price / 5000) * 10 
    
    products.append({
        "product_id": i + 100,
        "product_name": f"{tier_choice['tier']} {cat} - {fake.word().capitalize()}",
        "category": cat,
        "price": price,
        "tier": tier_choice["tier"],
        "complexity_score": round(complexity, 2),
        "popularity_score": random.uniform(0, 10)
    })

df_products = pd.DataFrame(products)

data = []
for i in range(NUM_USERS):
    mode = i % 4 
    
    if mode == 0: 
        recency = random.randint(30, 90)
        freq = random.randint(1, 3)
        monetary = random.randint(10, 50)
        views = random.randint(1, 10)
        
    elif mode == 1:
        recency = random.randint(7, 30)
        freq = random.randint(3, 8)
        monetary = random.randint(60, 200)
        views = random.randint(50, 150)
        
    elif mode == 2:
        recency = random.randint(1, 14)
        freq = random.randint(15, 40)
        monetary = random.randint(300, 1500)
        views = random.randint(20, 60)
        
    else:
        recency = random.randint(1, 7)
        freq = random.randint(10, 50)
        monetary = random.randint(3000, 10000)
        views = random.randint(30, 100)

    data.append({
        "user_id": i + 1,
        "Recency": recency,
        "Frequency": freq,
        "Monetary": monetary,
        "Avg_Items": round(random.uniform(1, 5), 1),
        "Unique_Products": random.randint(1, freq) if freq > 0 else 0,
        "Wishlist_Count": random.randint(0, 10),
        "Add_to_Cart_Count": freq + random.randint(0, 5),
        "Page_Views": views
    })

df_users = pd.DataFrame(data)

os.makedirs("app/ml", exist_ok=True)
df_users.to_csv("app/ml/dummy_ecommerce_clustered.csv", index=False)
df_products.to_csv("app/ml/products_dummy.csv", index=False)

print("Data Generation Complete")