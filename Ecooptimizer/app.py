from flask import Flask, jsonify, render_template
from flask_cors import CORS
from celery import Celery
import dash
from dash import dcc, html
from dash.dependencies import Input, Output
import plotly.graph_objs as go
import pandas as pd
from datetime import datetime, timedelta
import random
import joblib

app = Flask(__name__)
CORS(app)

# Celery configuration
celery = Celery('tasks', broker='redis://localhost:6379/0')

# Dash application
dash_app = dash.Dash(__name__, server=app, url_base_pathname='/dash/')

# Server configuration
servers = [
    {"id": 1, "capacity": 100, "efficiency": 0.8},
    {"id": 2, "capacity": 150, "efficiency": 0.7},
    {"id": 3, "capacity": 200, "efficiency": 0.9},
]

@celery.task
def generate_usage_data():
    current_time = datetime.now()
    data = []
    for server in servers:
        usage = random.randint(0, server["capacity"])
        data.append({
            "server_id": server["id"],
            "timestamp": current_time.isoformat(),
            "usage": usage,
            "energy_consumption": usage / server["efficiency"]
        })
    return data

@celery.task
def optimize_load(total_load):
    optimized_distribution = []
    remaining_load = total_load

    sorted_servers = sorted(servers, key=lambda x: x["efficiency"], reverse=True)

    for server in sorted_servers:
        if remaining_load > 0:
            allocated_load = min(remaining_load, server["capacity"])
            optimized_distribution.append({
                "server_id": server["id"],
                "allocated_load": allocated_load,
                "energy_consumption": allocated_load / server["efficiency"]
            })
            remaining_load -= allocated_load
        else:
            optimized_distribution.append({
                "server_id": server["id"],
                "allocated_load": 0,
                "energy_consumption": 0
            })

    return optimized_distribution

# Flask routes
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/usage_data')
def get_usage_data():
    return jsonify(generate_usage_data())

@app.route('/api/optimize')
def get_optimized_load():
    usage_data = generate_usage_data()
    total_load = sum(d['usage'] for d in usage_data)
    return jsonify(optimize_load(total_load))

@app.route('/api/predict_load')
def get_predicted_load():
    # For simplicity, we'll use a random prediction
    # In a real-world scenario, you'd use your trained model here
    future_timestamp = datetime.now() + timedelta(hours=1)
    predicted_load = random.randint(50, 300)
    return jsonify({'predicted_load': predicted_load})

@app.route('/api/train_model')
def train_ml_model():
    # In a real-world scenario, you'd implement your model training logic here
    # For this example, we'll just return a success message
    return jsonify({'message': 'Model trained successfully'})

# Dash layout
dash_app.layout = html.Div([
    html.H1('EcoOptimizer Dashboard'),
    dcc.Interval(
        id='interval-component',
        interval=5*1000,  # in milliseconds
        n_intervals=0
    ),
    dcc.Graph(id='live-usage-graph'),
    dcc.Graph(id='optimization-graph'),
    dcc.Graph(id='prediction-graph')
])

# Dash callbacks
@dash_app.callback(Output('live-usage-graph', 'figure'),
              Input('interval-component', 'n_intervals'))
def update_usage_graph(n):
    data = generate_usage_data()
    df = pd.DataFrame(data)
    
    traces = []
    for server_id in df['server_id'].unique():
        server_data = df[df['server_id'] == server_id]
        traces.append(go.Scatter(
            x=server_data['timestamp'],
            y=server_data['usage'],
            mode='lines+markers',
            name=f'Server {server_id}'
        ))
    
    return {
        'data': traces,
        'layout': go.Layout(
            title='Real-time Server Usage',
            xaxis={'title': 'Time'},
            yaxis={'title': 'Usage'}
        )
    }

@dash_app.callback(Output('optimization-graph', 'figure'),
              Input('interval-component', 'n_intervals'))
def update_optimization_graph(n):
    usage_data = generate_usage_data()
    total_load = sum(d['usage'] for d in usage_data)
    optimized_data = optimize_load(total_load)
    df = pd.DataFrame(optimized_data)
    
    return {
        'data': [
            go.Bar(x=df['server_id'], y=df['allocated_load'], name='Allocated Load'),
            go.Bar(x=df['server_id'], y=df['energy_consumption'], name='Energy Consumption')
        ],
        'layout': go.Layout(
            title='Load Optimization Results',
            xaxis={'title': 'Server ID'},
            yaxis={'title': 'Load / Energy'},
            barmode='group'
        )
    }

@dash_app.callback(Output('prediction-graph', 'figure'),
              Input('interval-component', 'n_intervals'))
def update_prediction_graph(n):
    current_time = datetime.now()
    future_times = [current_time + timedelta(hours=i) for i in range(1, 25)]
    predictions = [random.randint(50, 300) for _ in range(24)]  # Simplified prediction
    
    return {
        'data': [go.Scatter(
            x=future_times,
            y=predictions,
            mode='lines+markers',
            name='Predicted Load'
        )],
        'layout': go.Layout(
            title='24-Hour Load Prediction',
            xaxis={'title': 'Time'},
            yaxis={'title': 'Predicted Load'}
        )
    }

if __name__ == '__main__':
    app.run(debug=True)