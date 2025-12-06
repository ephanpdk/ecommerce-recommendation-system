import pandas as pd
import numpy as np
import joblib
import json
import os
from sklearn.preprocessing import StandardScaler
from sklearn.cluster import KMeans
from sklearn.metrics import silhouette_score

# --- FIX PATH (Gunakan Absolut Path di dalam Docker) ---
BASE_DIR = "/code/app/ml"
# Pastikan folder ada
os.makedirs(BASE_DIR, exist_ok=True)

# Load Data (Pastikan file CSV ada di folder yang benar)
df = pd.read_csv(f"{BASE_DIR}/dummy_ecommerce_clustered.csv")
df["Monetary_Log"] = np.log1p(df["Monetary"])

features = [
    "Recency", "Frequency", "Monetary_Log", "Avg_Items",
    "Unique_Products", "Wishlist_Count", "Add_to_Cart_Count", "Page_Views"
]

X = df[features]
scaler = StandardScaler()
X_scaled = scaler.fit_transform(X)

kmeans_raw = KMeans(n_clusters=4, random_state=42)
raw_clusters = kmeans_raw.fit_predict(X_scaled)

df["Temp_Cluster"] = raw_clusters
cluster_means = df.groupby("Temp_Cluster")["Monetary"].mean().sort_values()
mapping = {old_label: new_label for new_label, old_label in enumerate(cluster_means.index)}
df["Cluster"] = df["Temp_Cluster"].map(mapping)

sorted_centroids = np.zeros_like(kmeans_raw.cluster_centers_)
for old_lbl, new_lbl in mapping.items():
    sorted_centroids[new_lbl] = kmeans_raw.cluster_centers_[old_lbl]

kmeans_final = KMeans(n_clusters=4, init=sorted_centroids, n_init=1, random_state=42)
kmeans_final.fit(X_scaled)

# EXPLAINABILITY DATA
centroids_scaled = kmeans_final.cluster_centers_
centroids_real = scaler.inverse_transform(centroids_scaled)

real_df = pd.DataFrame(centroids_real, columns=features)
real_df["Monetary"] = np.expm1(real_df["Monetary_Log"]) 
real_df = real_df.drop(columns=["Monetary_Log"])

metadata = {
    "silhouette_score": round(silhouette_score(X_scaled, kmeans_final.labels_), 4),
    "inertia": round(kmeans_final.inertia_, 2),
    "features": features,
    "feature_readable": ["Recency", "Frequency", "Monetary (Log)", "Avg Items", "Unique Prod", "Wishlist", "Add Cart", "Views"],
    "cluster_names": ["Newbie", "Window Shopper", "Loyalist", "Sultan"],
    "centroids_scaled": centroids_scaled.tolist(),
    "centroids_real": real_df.to_dict(orient="records"), 
    "cluster_counts": df["Cluster"].value_counts().sort_index().to_dict()
}

# SIMPAN KE PATH ABSOLUT
metrics_path = os.path.join(BASE_DIR, "model_metrics.json")
with open(metrics_path, "w") as f:
    json.dump(metadata, f)

# Simpan Model Lainnya
joblib.dump(scaler, f"{BASE_DIR}/scaler_preproc.joblib")
joblib.dump(kmeans_final, f"{BASE_DIR}/kmeans_k2.joblib")

# Top N Dict (Dummy logic)
topN_dict = {}
topN_dict[0] = [{"product_id": 101}, {"product_id": 102}, {"product_id": 103}]
topN_dict[1] = [{"product_id": 104}, {"product_id": 105}, {"product_id": 106}]
topN_dict[2] = [{"product_id": 107}, {"product_id": 108}, {"product_id": 109}]
topN_dict[3] = [{"product_id": 110}, {"product_id": 111}, {"product_id": 112}]
joblib.dump(topN_dict, f"{BASE_DIR}/topN_by_cluster.joblib")

print(f"✅ Training Selesai. Metrics disimpan di: {metrics_path}")