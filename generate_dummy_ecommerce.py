import pandas as pd
import numpy as np
from faker import Faker
fake = Faker()

np.random.seed(42)

N = 800  # total data
clusters = np.random.choice([0,1,2], size=N, p=[0.30, 0.35, 0.35])

data = []

for c in clusters:
    if c == 0:
        # Budget Shopper
        recency = np.random.randint(30, 120)
        frequency = np.random.randint(1, 4)
        monetary = np.random.randint(30, 120)
        avg_items = np.random.uniform(1, 2)
        unique_products = np.random.randint(1, 4)
        wishlist = np.random.randint(0, 5)
        cart_count = np.random.randint(0, 3)
        page_views = np.random.randint(3, 10)
        pref_cat = np.random.choice(["serbaguna", "fashion", "gadget"], p=[0.5, 0.35, 0.15])
        second_cat = np.random.choice(["beauty", "dekor", "fashion"], p=[0.25,0.45,0.30])
        style = np.random.choice(["minimalis", "sporty"], p=[0.6,0.4])

    elif c == 1:
        # Trend Enthusiast
        recency = np.random.randint(10, 50)
        frequency = np.random.randint(3, 8)
        monetary = np.random.randint(80, 200)
        avg_items = np.random.uniform(1, 3)
        unique_products = np.random.randint(2, 6)
        wishlist = np.random.randint(6, 15)
        cart_count = np.random.randint(3, 8)
        page_views = np.random.randint(12, 30)
        pref_cat = np.random.choice(["fashion", "beauty", "serbaguna"], p=[0.45,0.35,0.20])
        second_cat = np.random.choice(["beauty", "fashion", "dekor"], p=[0.50,0.35,0.15])
        style = np.random.choice(["kawaii","minimalis","sporty"], p=[0.45,0.35,0.20])

    else:
        # High-Value Gadget Buyer
        recency = np.random.randint(5, 40)
        frequency = np.random.randint(4, 10)
        monetary = np.random.randint(200, 800)
        avg_items = np.random.uniform(1, 4)
        unique_products = np.random.randint(2, 7)
        wishlist = np.random.randint(2, 8)
        cart_count = np.random.randint(2, 6)
        page_views = np.random.randint(10, 20)
        pref_cat = np.random.choice(["gadget", "serbaguna"], p=[0.75,0.25])
        second_cat = np.random.choice(["gadget", "fashion", "serbaguna"], p=[0.50,0.30,0.20])
        style = np.random.choice(["sporty","streetwear","minimalis"], p=[0.50,0.30,0.20])
    
    data.append([
        recency, frequency, monetary, avg_items, unique_products,
        wishlist, cart_count, page_views, pref_cat, second_cat, style, c
    ])

df = pd.DataFrame(data, columns=[
    "Recency","Frequency","Monetary","Avg_Items","Unique_Products",
    "Wishlist_Count","Add_to_Cart_Count","Page_Views",
    "Preferred_Category","Second_Category","Preferred_Style","True_Cluster"
])

df.to_csv("dummy_ecommerce_clustered.csv", index=False)
df.head()
