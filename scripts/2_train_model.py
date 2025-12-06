import pandas as pd
import numpy as np
import joblib
import json
import os
from sklearn.preprocessing import StandardScaler
from sklearn.cluster import KMeans
from sklearn.decomposition import PCA
from sklearn.metrics import silhouette_score

BASE_DIR = "/code/app/ml"
os.makedirs(BASE_DIR, exist_ok=True)

df = pd.read_csv(f"{BASE_DIR}/dummy_ecommerce_clustered.csv")
df["Monetary_Log"] = np.log1p(df["Monetary"])

features = [
    "Recency", "Frequency", "Monetary_Log", "Avg_Items",
    "Unique_Products", "Wishlist_Count", "Add_to_Cart_Count", "Page_Views"
]
feature_readable = ["Recency", "Frequency", "Monetary", "Avg Items", "Unique Prod", "Wishlist", "Add Cart", "Views"]

X = df[features]
scaler = StandardScaler()
X_scaled = scaler.fit_transform(X)

pca = PCA(n_components=2)
pca.fit(X_scaled)
pca_var = [round(v * 100, 2) for v in pca.explained_variance_ratio_]

elbow_curve = {}
for k in range(2, 10):
    km = KMeans(n_clusters=k, random_state=42, n_init=10)
    km.fit(X_scaled)
    elbow_curve[str(k)] = round(km.inertia_, 2)

kmeans = KMeans(n_clusters=4, random_state=42, n_init=10)
clusters = kmeans.fit_predict(X_scaled)

df["Temp"] = clusters
means = df.groupby("Temp")["Monetary_Log"].mean().sort_values()
mapping = {old: new for new, old in enumerate(means.index)}

sorted_centers = np.zeros_like(kmeans.cluster_centers_)
for old, new in mapping.items():
    sorted_centers[new] = kmeans.cluster_centers_[old]

kmeans_final = KMeans(n_clusters=4, init=sorted_centers, n_init=1, random_state=42)
kmeans_final.fit(X_scaled)
df["Cluster"] = df["Temp"].map(mapping)

centroids_real = scaler.inverse_transform(kmeans_final.cluster_centers_)
real_df = pd.DataFrame(centroids_real, columns=features)
real_df["Monetary"] = np.expm1(real_df["Monetary_Log"]) 
real_df = real_df.drop(columns=["Monetary_Log"])

metadata = {
    "silhouette_score": round(silhouette_score(X_scaled, kmeans_final.labels_), 4),
    "inertia": round(kmeans_final.inertia_, 2),
    "features": features,
    "feature_readable": feature_readable,
    "cluster_names": ["Newbie", "Window Shopper", "Loyalist", "Sultan"],
    "centroids_scaled": kmeans_final.cluster_centers_.tolist(),
    "centroids_real": real_df.to_dict(orient="records"),
    "cluster_counts": df["Cluster"].value_counts().sort_index().to_dict(),
    "pca_variance": pca_var,
    "elbow_curve": elbow_curve,
    "global_stats": {
        "mean": scaler.mean_.tolist(),
        "std": scaler.scale_.tolist()
    }
}

with open(f"{BASE_DIR}/model_metrics.json", "w") as f:
    json.dump(metadata, f)

joblib.dump(scaler, f"{BASE_DIR}/scaler_preproc.joblib")
joblib.dump(kmeans_final, f"{BASE_DIR}/kmeans_k2.joblib")

topN = {i: [{"product_id": 100+i, "name": "Item", "category": "General"}] for i in range(4)}
joblib.dump(topN, f"{BASE_DIR}/topN_by_cluster.joblib")

print("Training Complete")