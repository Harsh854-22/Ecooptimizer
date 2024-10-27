import dash
from dash import dcc, html
from dash.dependencies import Input, Output
import plotly.graph_objs as go
import pandas as pd
from datetime import datetime, timedelta
from celery_worker import generate_usage_data, optimize_load
from ml_model import predict_load

app = dash.Dash(__name__)

app.layout = html.Div([
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

@app.callback(Output('live-usage-graph', 'figure'),
              Input('interval-component', 'n_intervals'))
def update_usage_graph(n):
    try:
        data = generate_usage_data.delay().get(timeout=10)
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
    except Exception as e:
        print(f"Error in live-usage-graph callback: {e}")
        return {
            'data': [],
            'layout': go.Layout(
                title='Real-time Server Usage - Error',
                xaxis={'title': 'Time'},
                yaxis={'title': 'Usage'}
            )
        }

@app.callback(Output('optimization-graph', 'figure'),
              Input('interval-component', 'n_intervals'))
def update_optimization_graph(n):
    try:
        usage_data = generate_usage_data.delay().get(timeout=10)
        total_load = sum(d['usage'] for d in usage_data)
        optimized_data = optimize_load.delay(total_load).get(timeout=10)
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
    except Exception as e:
        print(f"Error in optimization-graph callback: {e}")
        return {
            'data': [],
            'layout': go.Layout(
                title='Load Optimization Results - Error',
                xaxis={'title': 'Server ID'},
                yaxis={'title': 'Load / Energy'}
            )
        }

@app.callback(Output('prediction-graph', 'figure'),
              Input('interval-component', 'n_intervals'))
def update_prediction_graph(n):
    try:
        current_time = datetime.now()
        future_times = [current_time + timedelta(hours=i) for i in range(1, 25)]
        
        # Generate predictions and check for valid data format
        predictions = []
        for t in future_times:
            pred = predict_load(t)
            if isinstance(pred, (int, float)):
                predictions.append(pred)
            else:
                print(f"Warning: Non-numeric prediction received at {t}: {pred}")
                predictions.append(0)  # or a default/fallback value
        
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
    except Exception as e:
        print(f"Error in prediction-graph callback: {e}")
        return {
            'data': [],
            'layout': go.Layout(
                title='24-Hour Load Prediction - Error',
                xaxis={'title': 'Time'},
                yaxis={'title': 'Predicted Load'}
            )
        }

if __name__ == '__main__':
    app.run_server(debug=True)
