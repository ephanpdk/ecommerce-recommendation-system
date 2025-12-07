
-----

# 🧠 **Intelligent Retail Segmentation & Recommendation Engine**

**End-to-End Machine Learning System (FastAPI + Scikit-Learn + Docker)**

> Sistem kecerdasan ritel yang menggabungkan **Unsupervised Learning (K-Means++)** untuk segmentasi pelanggan dan **Content-Based Filtering (Cosine Similarity)** untuk rekomendasi produk. Dilengkapi dengan dashboard interaktif untuk simulasi strategi bisnis secara real-time.

-----

## 📌 **Overview**

Web ini bukan sekadar model prediksi, melainkan sebuah **Sistem Pendukung Keputusan (DSS)** yang mensimulasikan alur kerja data science di industri *e-commerce*:

1.  **Data Ingestion:** Mengolah data transaksi sintetik yang meniru pola dunia nyata (Log-transformed & Scaled).
2.  **User Profiling:** Mengelompokkan user ke dalam 4 persona perilaku (*Newbie, Window Shopper, Loyalist, Sultan*).
3.  **Recommendation Engine:** Mencocokkan profil user dengan database produk nyata (Electronics, Fashion, Skincare) menggunakan vektor kesamaan.
4.  **Business Intelligence:** Menampilkan risiko *churn*, potensi *upgrade* segmen, dan metrik evaluasi model dalam satu dashboard.

Sistem ini dirancang dengan arsitektur **Microservices (Dockerized)** agar mudah di-deploy dan dipresentasikan.

-----

## 🏗️ **Arsitektur Sistem (ML Pipeline)**

### 1\. Data Generator & Preprocessing

  * **Dataset:** 1.000 User & 100 Produk Nyata (e.g., iPhone 15, SK-II, Nike Air Jordan).
  * **Feature Engineering:** Menggunakan 8 fitur utama:
      * *Transactional:* Monetary (Log Transformed), Frequency, Recency.
      * *Behavioral:* Avg Items/Order, Unique Products.
      * *Engagement:* Page Views, Add to Cart, Wishlist.
  * **Normalization:** StandardScaler (Z-Score) untuk Clustering, MinMaxScaler untuk Visualisasi Radar.

### 2\. Machine Learning Core

  * **Clustering:** Algoritma **K-Means++** dengan $k=4$ (ditentukan via Elbow Method).
  * **Recommendation:** **Cosine Similarity** antara vektor Centroid User dan vektor Atribut Produk (Harga & Kompleksitas).
  * **Explainability:** Menghitung *Feature Importance* global untuk mengetahui faktor penentu segmen.

### 3\. Backend & Serving

  * **Framework:** FastAPI (Asynchronous).
  * **Endpoints:** REST API untuk prediksi real-time dan autentikasi (JWT).
  * **Storage:** Menyimpan model (`.joblib`) dan metrik visualisasi (`.json`) untuk performa tinggi (tanpa training ulang saat request).

### 4\. Frontend Dashboard

  * **Stack:** HTML5, TailwindCSS, Chart.js.
  * **Fitur:** Simulator Input Slider, Radar Chart (Normalized), Risk Gauge, dan Session Logging.

-----

## 🚀 **Fitur Utama**

### 🎯 **1. 8-Parameter Real-Time Simulation**

Dashboard memungkinkan simulasi profil user dengan mengubah 8 variabel input secara langsung:

  * `Total Spend`, `Frequency`, `Recency`
  * `Avg Items`, `Unique Products`
  * `Views`, `Add to Cart`, `Wishlist`

### 🧠 **2. Web Segmentation & Persona**

Model memetakan user ke 4 segmen strategi:

  * 🔵 **Newbie:** Butuh edukasi & diskon akuisisi.
  * 🔵 **Window Shopper:** Butuh *retargeting* (banyak lihat, jarang beli).
  * 🟢 **Loyalist:** Butuh *reward points* (belanja rutin).
  * 🟠 **Sultan:** Butuh layanan VIP (spending & engagement tinggi).

### 📈 **3. Advanced Analytics & Insights**

  * **Migration Risk:** Bar indikator peluang user turun kelas (*Downgrade*).
  * **Upgrade Potential:** Bar indikator peluang user naik kelas (*Upgrade*).
  * **Visualisasi Validasi:**
      * *Elbow Curve* & *Silhouette Score* (Validasi K).
      * *PCA Scatter Plot* (2D Projection).
      * *Radar Chart* (DNA Cluster - Normalized 0-1).

### 🛒 **4. Context-Aware Recommendations**

Produk direkomendasikan berdasarkan **Tier Matching**:

  * User *Sultan* → Produk *Luxury* (e.g., MacBook Pro).
  * User *Newbie* → Produk *Budget* (e.g., USB Cable).

-----

## 📁 **Struktur Direktori**

```text
ecommerce-recommendation-system/
├── app/
│   ├── ml/                     # OTAK SISTEM (Machine Learning)
│   │   ├── 1_generate_data.py  # Script generate data dummy + real products
│   │   ├── 2_train_model.py    # Training K-Means, PCA, & Cosine Sim
│   │   ├── model_metrics.json  # Data untuk visualisasi frontend
│   │   └── *.joblib            # Model yang sudah dilatih
│   ├── routers/                # API Endpoints (Auth, Recommend)
│   ├── templates/              # Frontend Files
│   │   ├── dashboard.html      # Main Layout
│   │   └── partials/           # Modular HTML (Simulator, Results, Analytics)
│   └── main.py                 # Entry Point FastAPI
├── docker-compose.yml          # Orchestration
├── Dockerfile                  # Image Config
└── requirements.txt            # Python Dependencies
```

-----

## 🛠️ **Instalasi & Cara Menjalankan**

Disarankan menggunakan **Docker** agar lingkungan berjalan stabil tanpa konflik dependensi.

### Langkah 1: Clone Repository

```bash
git clone https://github.com/USERNAME/ecommerce-recommendation-system.git
cd ecommerce-recommendation-system
```

### Langkah 2: Jalankan Container

```bash
docker-compose up -d --build
```

### Langkah 3: Generate Data & Latih Model (PENTING\!)

Lakukan ini pertama kali untuk memastikan data produk dan metrik visualisasi terbentuk.

```bash
# Generate Dataset (Produk Nyata & User Dummy)
docker-compose exec backend python app/ml/1_generate_data.py

# Train Model & Hitung Metrik Visualisasi
docker-compose exec backend python app/ml/2_train_model.py

# Restart Service untuk memuat model baru
docker-compose restart backend
```

-----

## 🖥️ **Akses Aplikasi**

| Layanan | URL | Keterangan |
| :--- | :--- | :--- |
| **Web Dashboard** | `http://localhost:8000` | UI Utama untuk simulasi & analisis |
| **API Documentation** | `http://localhost:8000/docs` | Swagger UI untuk testing API |
| **Database Metrics** | `http://localhost:8000/cluster/metrics` | JSON Output statistik model |

-----

## 🧪 **Contoh Skenario Uji Coba**

1.  Buka Dashboard.
2.  Masuk ke menu **Simulator**.
3.  Set **Total Spend** ke `$4000` dan **Frequency** ke `40` dan **Monthly Page View** ke `55`.
4.  Klik **Predict Persona**.
5.  **Hasil:** User terdeteksi sebagai **Sultan**. Rekomendasi produk akan menampilkan barang mahal (Luxury).
6.  Geser **Recency** menjadi `90 days` (jarang aktif).
7.  **Hasil:** Bar **Migration Risk** akan meningkat merah (Indikasi Churn).

-----

## 📚 **Tech Stack Detail**

  * **Language:** Python 3.10+
  * **ML Libraries:** Scikit-Learn (KMeans, PCA, Preprocessing), Pandas, NumPy.
  * **Backend:** FastAPI, Uvicorn, Pydantic.
  * **Frontend:** Jinja2 Templates, TailwindCSS (CDN), Chart.js (Visualisasi).
  * **Containerization:** Docker & Docker Compose.

-----

**Copyright © 2025 Analytica Solutions.**
*Project ini dibuat untuk tujuan demonstrasi akademis dan purwarupa sistem rekomendasi ritel.*
