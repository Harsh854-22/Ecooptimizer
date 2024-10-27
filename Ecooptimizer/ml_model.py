import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_squared_error
import joblib

def create_features(df):
    df = df.copy()
    df['hour'] = df.index.hour
    df['dayofweek'] = df.index.dayofweek
    df['quarter'] = df.index.quarter
    df['month'] = df.index.month
    df['year'] = df.index.year
    df['dayofyear'] = df.index.dayofyear
    return df

def train_model(data):
    # Prepare the data
    df = pd.DataFrame(data)
    df['timestamp'] = pd.to_datetime(df['timestamp'])
    df = df.set_index('timestamp')
    df = df.resample('H').sum()  # Resample to hourly data
    
    # Create features
    df = create_features(df)
    
    # Prepare features and target
    features = ['hour', 'dayofweek', 'quarter', 'month', 'year', 'dayofyear']
    X = df[features]
    y = df['usage']
    
    # Split the data
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    
    # Scale the features
    scaler = StandardScaler()
    X_train_scaled = scaler.fit_transform(X_train)
    X_test_scaled = scaler.transform(X_test)
    
    # Train the model
    model = RandomForestRegressor(n_estimators=100, random_state=42)
    model.fit(X_train_scaled, y_train)
    
    # Evaluate the model
    y_pred = model.predict(X_test_scaled)
    mse = mean_squared_error(y_test, y_pred)
    print(f"Mean Squared Error: {mse}")
    
    # Save the model and scaler
    joblib.dump(model, 'load_prediction_model.joblib')
    joblib.dump(scaler, 'load_prediction_scaler.joblib')

def predict_load(timestamp):
    # Load the model and scaler
    model = joblib.load('load_prediction_model.joblib')
    scaler = joblib.load('load_prediction_scaler.joblib')
    
    # Prepare the input data
    df = pd.DataFrame({'timestamp': [timestamp]})
    df = df.set_index('timestamp')
    df = create_features(df)
    
    # Scale the features
    X = scaler.transform(df[['hour', 'dayofweek', 'quarter', 'month', 'year', 'dayofyear']])
    
    # Make prediction
    prediction = model.predict(X)
    return prediction[0]