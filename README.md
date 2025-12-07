
---

# 🧠 **SmartShop AI – Intelligent Retail Recommendation System**

**End-to-End Machine Learning + Web Application (FastAPI + Scikit-Learn)**

> Sistem rekomendasi e-commerce berbasis **Customer Segmentation (K-Means)** dan **Content-Based Product Recommendation (Cosine Similarity)**, lengkap dengan **Explainable AI (XAI)** serta implementasi web real-time.

![Tech Stack](https://img.shields.io/badge/Stack-FastAPI%20%7C%20Docker%20%7C%20Scikit--Learn%20%7C%20Pandas%20%7C%20Chart.js-blue)

---

## 📌 **Overview**

SmartShop AI adalah project machine learning end-to-end yang mensimulasikan pipeline retail modern:

* Membuat dataset perilaku user (synthetic but structured)
* Melatih model K-Means berbasis RFM & user-behavior features
* Menghasilkan rekomendasi produk berbasis cosine similarity
* Mengintegrasikan model ke API real-time menggunakan FastAPI
* Menampilkan visualisasi model, PCA, Elbow, Radar Chart melalui web dashboard
* Menyediakan Explainable AI: alasan matematis kenapa user masuk cluster tertentu

Sistem ini dirancang supaya **siap presentasi**, **anti-bantai**, dan **bercita rasa industri**.

---

## 🏗️ **Arsitektur Sistem (End-to-End ML Pipeline)**

1. **Data Generator (1_generate_data.py)**
   ✦ Membuat 1000 user dengan pola perilaku ekstrem (Newbie, Window Shopper, Loyalist, Sultan)
   ✦ Membuat product dataset 50 items
   ✦ Menyimpan sebagai CSV untuk training

2. **Model Training (2_train_model.py)**
   ✦ Preprocessing

   * Log transform Monetary
   * StandardScaler (Z-score)
     ✦ Clustering
   * K-Means++ (k=4 ditentukan via Elbow Method)
     ✦ Product Recommendation
   * Cosine similarity → Top-N tiap cluster
     ✦ Saves:
   * `scaler_preproc.joblib`
   * `kmeans_k2.joblib`
   * `topN_by_cluster.joblib`
   * `model_metrics.json`

3. **Backend FastAPI**
   ✦ Endpoint:

   * `/auth/*` → JWT Authentication
   * `/cluster/metrics` → Model insight
   * `/recommend/user` → Prediksi cluster + rekomendasi produk
     ✦ Logging hasil prediction ke database

4. **Frontend Web Dashboard**
   ✦ Form input simulasi user
   ✦ Hasil prediksi
   ✦ Feature contribution (Z-score)
   ✦ Confidence score
   ✦ Visualisasi: PCA, Elbow, Radar, Cluster Dist.
   ✦ Semua logic di `scripts.html`

---

## 🚀 **Fitur Utama**

### 🎯 **1. Real-Time Segmentation**

Model memetakan user ke 4 persona:

* **Newbie** – Spending rendah, recency tinggi
* **Window Shopper** – Page view tinggi, transaksi rendah
* **Loyalist** – Sering beli, stabil
* **Sultan** – High spender, high lifetime value

### 🧠 **2. Explainable AI (XAI)**

Sistem menjelaskan:

* fitur apa yang dominan (z-score)
* kenapa user masuk cluster itu
* bandingannya dengan cluster lain
* anomaly detection (misal VIP mau churn)

### 🛒 **3. Product Recommendation (Cosine Similarity)**

Top-N produk berdasarkan:

* kedekatan user-feature vs product-feature
* cluster persona
* product embedding hasil preprocessing

### 📊 **4. Complete Model Visualization**

* Elbow curve
* Silhouette score
* PCA 2D
* Radar chart centroid
* Cluster distribution

### 🔐 **5. Security & Logging**

* JWT Auth
* Database logging setiap prediksi
* Fail-safe model loader

---

## 📁 **Struktur Folder (Ringkas)**

```
app/
 ├── ml/
 │    ├── 1_generate_data.py
 │    ├── 2_train_model.py
 │    ├── dummy_ecommerce_clustered.csv
 │    ├── products_dummy.csv
 │    ├── scaler_preproc.joblib
 │    ├── kmeans_k2.joblib
 │    ├── topN_by_cluster.joblib
 │    └── model_metrics.json
 ├── routers/
 ├── models/
 ├── schemas/
 ├── database.py
 ├── main.py
templates/
 ├── dashboard.html
 ├── scripts.html
```

---

## 🛠️ **Cara Menjalankan (Docker Recommended)**

Pastikan Docker Desktop sudah berjalan.

```bash
# 1. Clone Repository
git clone https://github.com/USERNAME/gayadouze.git
cd gayadouze

# 2. Build & Run Container
docker compose up --build

# 3. (Opsional) Generate ulang dataset + training
docker compose exec web python app/ml/1_generate_data.py
docker compose exec web python app/ml/2_train_model.py
```

Akses Web Dashboard:
👉 `http://localhost:8000`

Akses Docs (Swagger):
👉 `http://localhost:8000/docs`

---

## 🧪 **Endpoint Utama**

### 🔍 Predict + Recommend

```
POST /recommend/user
```

### 📊 Model Metrics

```
GET /cluster/metrics
```

### 🔑 Authentication

```
POST /auth/login
POST /auth/register
```

---

## 📚 **Teknologi yang Digunakan**

* Python 3.11
* FastAPI
* Scikit-Learn
* Pandas / NumPy
* Joblib
* Uvicorn
* PostgreSQL
* SQLAlchemy
* JWT Auth
* TailwindCSS
* Chart.js

---

