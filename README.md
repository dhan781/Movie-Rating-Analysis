# 🎬 Movie Analytics Dashboard

An interactive web application built with **Python**, **Plotly Dash**, and **Bootstrap** to visualize and analyze the **MovieLens** dataset. This dashboard explores movie ratings, genre distributions, popularity trends, and user-generated tagging behavior.

### 🚀 [Launch the Live Dashboard](https://da2402-project.onrender.com)
> **Note:** As this is hosted on a free Render server, the initial load may take **30–60 seconds** while the server "wakes up".

---

## 📂 Repository Structure

The project is organized into modular directories to separate data preprocessing from the final visualization application.

```text
DA2402-PROJECT/
├── DataPreProcessing/
│   ├── PreProcessedData/
│   │   ├── cleaned_data.csv
│   │   └── movie_level_data.csv
│   ├── Data_preprocessing.ipynb
│   ├── imputation.py
│   └── missing_data_tests.py
|
├── DataSets/
│   ├── links.csv
│   ├── movies.csv
│   ├── ratings.csv
│   └── tags.csv
|
├── Visualization/
│   ├── Visualization_dashboard.py
│   ├── Visualization.ipynb
│   ├── requirements.txt
│   └── Procfile
|
├── Dashboard.html
└── README.md
