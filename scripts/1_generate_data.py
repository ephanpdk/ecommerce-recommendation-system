import pandas as pd
import numpy as np
import random
from faker import Faker
import os

fake = Faker()

# Konfigurasi
NUM_USERS = 1000 # Kita perbanyak sample biar akurat
NUM_PRODUCTS = 50

# 1. Generate Products
categories = ['Electronics', 'Fashion', 'Home & Living', 'Skincare']
products = []
for i in range(NUM_PRODUCTS):
    cat = random.choice(categories)
    products.append({
        "product_id": i + 100,
        "product_name": f"{cat} Item {fake.word().capitalize()}",
        "category": cat,
        "style": "General"
    })
df_products = pd.DataFrame(products)

# 2. Generate User Behavior (SANGAT KONTRAS)
data = []
for i in range(NUM_USERS):
    # Paksa distribusi rata (0, 1, 2, 3 berulang)
    mode = i % 4 
    
    if mode == 0: 
        # TIPE 1: NEWBIE (Sangat Hemat)
        # Ciri: Transaksi dikit, Uang dikit, Recency lama
        recency = random.randint(30, 90)
        freq = random.randint(1, 3)
        monetary = random.randint(10, 50) # Max $50
        views = random.randint(1, 10)
        
    elif mode == 1:
        # TIPE 2: WINDOW SHOPPER (Suka Liat, Jarang Beli)
        # Ciri: Views TINGGI, tapi Frequency RENDAH
        recency = random.randint(7, 30)
        freq = random.randint(3, 8)
        monetary = random.randint(60, 200) # $60 - $200
        views = random.randint(50, 150) # Sering liat-liat
        
    elif mode == 2:
        # TIPE 3: LOYALIST (Rutin)
        # Ciri: Frequency TINGGI, Monetary Menengah
        recency = random.randint(1, 14)
        freq = random.randint(15, 40)
        monetary = random.randint(300, 1500) # $300 - $1500
        views = random.randint(20, 60)
        
    else:
        # TIPE 4: SULTAN (High Spender)
        # Ciri: Monetary SANGAT TINGGI
        recency = random.randint(1, 7)
        freq = random.randint(10, 50)
        monetary = random.randint(3000, 10000) # Min $3000
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

# Simpan
os.makedirs("app/ml", exist_ok=True)
df_users.to_csv("app/ml/dummy_ecommerce_clustered.csv", index=False)
df_products.to_csv("app/ml/products_dummy.csv", index=False)

print("✅ Data Dummy KONTRAS Berhasil Dibuat!")