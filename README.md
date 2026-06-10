# 📊 Sales Intelligence

A comprehensive Sales Intelligence platform built with **Python** and **Streamlit** that enables users to upload sales datasets, perform exploratory data analysis, preprocess data, train forecasting models, generate predictions, and visualize business insights through an interactive dashboard.

The application is designed to streamline the complete sales analytics workflow, from raw data ingestion to actionable business intelligence.

---

## 🚀 Features

### 📂 Data Upload

* Upload sales datasets in CSV format.
* Preview uploaded data before processing.
* Validate dataset structure and quality.

### 🧹 Data Preprocessing

* Handle missing values and duplicate records.
* Data cleaning and transformation.
* Feature preparation for machine learning models.

### 📈 Exploratory Data Analysis (EDA)

* Revenue and sales trend analysis.
* Product and category performance insights.
* Statistical summaries and visual exploration.
* Interactive charts and business metrics.

### 🤖 Model Training

* Train machine learning models on historical sales data.
* Evaluate model performance.
* Generate predictive insights for future sales.

### 🔮 Sales Forecasting

* Forecast future sales trends.
* Support demand planning and decision-making.
* Visualize predicted sales performance.

### 📊 Dashboard

* Interactive KPI monitoring.
* Real-time visual analytics.
* Business performance overview.

### 📄 Report Generation

* Generate analytical summaries.
* Export insights for stakeholders.
* Support business reporting and decision-making.

---

# 🏗️ Project Structure

```text
SALES_INTELLIGENCE/
│
├── .streamlit/
│
├── assets/
│   └── Static assets, images, and resources
│
├── modules/
│   ├── __init__.py
│   ├── dashboard.py
│   ├── data_upload.py
│   ├── eda.py
│   ├── forecasting.py
│   ├── model_training.py
│   ├── preprocessing.py
│   └── report_generator.py
│
├── sample_data/
│   └── sample_sales.csv
│
├── utils/
│   ├── __init__.py
│   ├── helpers.py
│   └── theme.py
│
├── app.py
├── requirements.txt
└── .gitignore
```

---

# ⚙️ Module Overview

| Module              | Description                                           |
| ------------------- | ----------------------------------------------------- |
| data_upload.py      | Handles CSV uploads and dataset validation            |
| preprocessing.py    | Cleans and transforms raw sales data                  |
| eda.py              | Performs exploratory data analysis and visualizations |
| model_training.py   | Trains machine learning models                        |
| forecasting.py      | Generates future sales forecasts                      |
| dashboard.py        | Displays KPIs and interactive charts                  |
| report_generator.py | Creates business intelligence reports                 |
| helpers.py          | Common utility functions                              |
| theme.py            | Application styling and UI customization              |

---

# 🛠️ Technology Stack

### Frontend

* Streamlit

### Backend

* Python

### Data Processing

* Pandas
* NumPy

### Visualization

* Plotly
* Matplotlib

### Machine Learning

* Scikit-Learn

### Forecasting

* Time-Series Forecasting Models

---

# 📥 Installation

## Clone the Repository

```bash
git clone https://github.com/Akhila1128/Project2-DA
cd Project2-DA
```

## Create Virtual Environment

```bash
python -m venv venv
```

## Activate Environment

### Windows

```bash
venv\Scripts\activate
```

### Linux/macOS

```bash
source venv/bin/activate
```

## Install Dependencies

```bash
pip install -r requirements.txt
```

---

# ▶️ Run the Application

```bash
streamlit run app.py
```

Open your browser at:

```text
http://localhost:8501
```

---

# 📊 Application Workflow

```text
Upload Dataset
       │
       ▼
Data Validation
       │
       ▼
Preprocessing
       │
       ▼
EDA Analysis
       │
       ▼
Model Training
       │
       ▼
Sales Forecasting
       │
       ▼
Dashboard Visualization
       │
       ▼
Report Generation
```

---

# 🎯 Business Benefits

* Faster sales analysis.
* Improved business visibility.
* Data-driven decision making.
* Automated forecasting.
* Reduced manual reporting effort.
* Interactive analytics dashboard.

---

# 🔮 Future Enhancements

* Database Integration
* User Authentication
* Multi-user Access
* Cloud Deployment
* Advanced Forecasting Models
* PDF Report Export
* AI-Based Recommendations

---
Developed as a Sales Intelligence solution for data analytics, forecasting, reporting, and business decision support.

⭐ Star this repository if you find it useful.
