# Road Accident Analysis Research

This repository contains the full research project **"Predicting Vehicle Accidents 
Based on Weather Conditions, Driver History, Vehicle Factors and Black Spots Using 
Machine Learning"**.

## 📂 Project Structure
- `accident_data_scrapping/` – Accident datasets with weather enrichment  
- `non_accident_data_scrapping/` – Non-accident data sampling and weather data  
- `HDBSAN_and_100m/` – Blackspot detection using HDBSCAN and 100m radius clustering  
- `data_prepration/` – Pre-processing scripts and feature engineering  
- `main_model/` – Machine learning models (XGBoost, LightGBM, CatBoost, LSTM, RandomForest)  
- `results/` – Evaluation metrics, visualizations, and comparisons  

## ⚙️ Methodology
1. **Data Collection**:  
   - Accident data from the UK Department for Transport (2005–2012)  
   - Weather data scraped via the Open-Meteo API  

2. **Data Preparation**:  
   - Merging accident and non-accident samples  
   - Feature engineering (driver demographics, vehicle attributes, weather)  
   - Balancing datasets with SMOTE  

3. **Blackspot Detection**:  
   - HDBSCAN clustering  
   - 100m radius rule for hotspot identification  

4. **Modeling**:  
   - RandomForest, XGBoost, LightGBM, CatBoost, LSTM  
   - Evaluation with ROC-AUC, PR-AUC, Accuracy, F1, Precision, Recall  

5. **Artefact**:  
   - Django-based web app for accident risk prediction (excluded here due to size)  

## 📊 Results
- Models achieved performance in the **71–73% accuracy** range  
- XGBoost and LightGBM performed best overall  
- Feature importance highlighted weather (rain, humidity, pressure) and driver attributes (age, IMD decile) as strong predictors  

## 🚀 Future Work
- Real-time weather integration  
- Larger-scale blackspot mapping  
- Deployable interactive dashboard  

## 👤 Author
**Delvin Vallooran Jose**  
MSc Data Analytics, Dublin Business School  
GitHub: [Delvinvjose](https://github.com/Delvinvjose)
