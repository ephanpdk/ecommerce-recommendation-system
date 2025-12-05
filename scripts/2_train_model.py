import pandas as pd
import numpy as np
import joblib
from sklearn.preprocessing import StandardScaler
from sklearn.cluster import KMeans

df = pd.read_csv("app/ml/dummy_ecommerce_clustered.csv")
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

topN_dict = {}
topN_dict[0] = [{"product_id": 101}, {"product_id": 102}, {"product_id": 103}]
topN_dict[1] = [{"product_id": 104}, {"product_id": 105}, {"product_id": 106}]
topN_dict[2] = [{"product_id": 107}, {"product_id": 108}, {"product_id": 109}]
topN_dict[3] = [{"product_id": 110}, {"product_id": 111}, {"product_id": 112}]

joblib.dump(scaler, "app/ml/scaler_preproc.joblib")
joblib.dump(kmeans_final, "app/ml/kmeans_k2.joblib")
joblib.dump(topN_dict, "app/ml/topN_by_cluster.joblib")

print("Training Selesai. Cluster berhasil diurutkan.")