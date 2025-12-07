import pandas as pd
import numpy as np
import random
from faker import Faker
import os

fake = Faker()

NUM_USERS = 1000 
NUM_PRODUCTS = 100

REAL_PRODUCTS = {
    "Electronics": {
        "Budget": ["USB-C Cable 1m", "Basic Wired Earphones", "Phone Case Silicone", "Screen Protector", "AA Batteries (4-Pack)"],
        "Standard": ["Wireless Earbuds Basic", "Powerbank 10000mAh", "Bluetooth Speaker", "Smart Band Watch", "Fast Charger 30W"],
        "Premium": ["Noise Cancelling Headphones", "Tablet Android 10-inch", "Smart Watch Series 7", "Mechanical Keyboard RGB", "Monitor 24-inch IPS"],
        "Luxury": ["MacBook Pro M3 Max", "iPhone 15 Pro Max", "Sony Alpha A7 IV Camera", "Gaming PC RTX 4090", "8K OLED TV 65-inch"]
    },
    "Fashion": {
        "Budget": ["Cotton T-Shirt Plain", "Ankle Socks (3-Pair)", "Canvas Tote Bag", "Baseball Cap", "Flip Flops"],
        "Standard": ["Denim Jacket Classic", "Running Shoes Daily", "Slim Fit Chinos", "Oxford Shirt", "Backpack Water Resistant"],
        "Premium": ["Leather Chelsea Boots", "Designer Sunglasses", "Merino Wool Sweater", "Automatic Watch Seiko", "Silk Scarf"],
        "Luxury": ["Limited Edition Sneakers", "Italian Leather Handbag", "Cashmere Trench Coat", "Swiss Luxury Watch", "Diamond Stud Earrings"]
    },
    "Home & Living": {
        "Budget": ["Microfiber Cloth", "Plastic Food Container", "Desk Organizer", "Scented Candle Small", "Kitchen Towel Set"],
        "Standard": ["Memory Foam Pillow", "Non-Stick Frying Pan", "Desk Lamp LED", "Bath Towel Premium", "Succulent Pot Set"],
        "Premium": ["Robot Vacuum Cleaner", "Air Purifier HEPA", "Espresso Machine", "Ergonomic Office Chair", "Smart Door Lock"],
        "Luxury": ["Designer Lounge Chair", "Smart Refrigerator Hub", "Home Theater System", "Persian Rug Hand-Woven", "Massage Chair Zero-G"]
    },
    "Skincare": {
        "Budget": ["Facial Cleanser Foam", "Sheet Mask Aloe", "Lip Balm Moisturizing", "Cotton Pads", "Hand Cream Mini"],
        "Standard": ["Sunscreen SPF 50", "Toner Hydrating", "Vitamin C Serum", "Clay Mask", "Daily Moisturizer"],
        "Premium": ["Retinol Night Cream", "Eye Cream Advanced", "Essence Fermented", "Electric Face Cleanser", "Hair Loss Tonic"],
        "Luxury": ["La Mer Moisturizing Cream", "SK-II Facial Treatment", "Dyson Hair Wrap", "LED Light Therapy Mask", "Luxury Perfume 100ml"]
    }
}

TIER_PRICING = {
    "Budget": (5, 40),
    "Standard": (50, 150),
    "Premium": (200, 800),
    "Luxury": (1000, 5000)
}

products = []
categories = list(REAL_PRODUCTS.keys())

for i in range(NUM_PRODUCTS):
    cat = random.choice(categories)
    tier_name = random.choices(["Budget", "Standard", "Premium", "Luxury"], weights=[40, 30, 20, 10], k=1)[0]
    
    prod_name = random.choice(REAL_PRODUCTS[cat][tier_name])
    price_range = TIER_PRICING[tier_name]
    price = random.randint(*price_range)
    
    final_name = f"{prod_name}" if random.random() > 0.5 else f"{prod_name} - {fake.word().capitalize()} Edition"
    
    complexity = (price / 5000) * 10 
    
    products.append({
        "product_id": i + 100,
        "name": final_name,
        "category": cat,
        "price": price,
        "tier": tier_name,
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

print("Real Product Data Generated")