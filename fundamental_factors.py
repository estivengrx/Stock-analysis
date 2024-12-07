import requests
import json
import pandas as pd
import plotly.graph_objects as go
import plotly.io as pio

from numpy import nan

# Open the file and load the keys
with open('api_keys.json', 'r') as f:
    api_keys = json.load(f)

# Now api_keys is a dictionary with the keys
alphavantage_key = api_keys['alphavantage']
newsapi_key = api_keys['newsapi']

def get_earnings_data(stock):
    url = f'https://www.alphavantage.co/query?function=EARNINGS&symbol={stock}&apikey={alphavantage_key}'
    response = requests.get(url)
    data = response.json()
    data = pd.DataFrame(data['quarterlyEarnings'])
    return data

def get_news_data(stock):
    url = f'https://newsapi.org/v2/everything?q={stock}&apiKey={newsapi_key}'
    response = requests.get(url)
    data = response.json()
    return data

def analyze_earnings(stock):
    data = get_earnings_data(stock)
    print(f'DATA: {data}')
    # Convert the 'reportedDate' column to datetime format
    data['reportedDate'] = pd.to_datetime(data['reportedDate'])
    data.replace('None', nan, inplace=True)


    # Convert 'reportedEPS', 'estimatedEPS', 'surprise', and 'surprisePercentage' to float
    for col in ['reportedEPS', 'estimatedEPS', 'surprise', 'surprisePercentage']:
        data[col] = pd.to_numeric(data[col], errors='coerce').fillna(0.0)

    # Plot the 'reportedEPS' and 'estimatedEPS' over time
    fig1 = go.Figure()
    fig1.add_trace(go.Scatter(x=data['reportedDate'], y=data['reportedEPS'], mode='lines', name='Reported EPS'))
    fig1.add_trace(go.Scatter(x=data['reportedDate'], y=data['estimatedEPS'], mode='lines', name='Estimated EPS'))
    fig1.update_layout(title='Reported vs Estimated EPS over time', xaxis_title='Date', yaxis_title='EPS')
    pio.write_html(fig1, file=f'static/visualizations/fundamental_factors/{stock}_eps.html', auto_open=False)

    # Plot the 'surprisePercentage' over time
    fig2 = go.Figure()
    fig2.add_trace(go.Scatter(x=data['reportedDate'], y=data['surprisePercentage'], mode='lines', name='Surprise Percentage'))
    fig2.update_layout(title='Surprise Percentage over time', xaxis_title='Date', yaxis_title='Surprise Percentage')
    pio.write_html(fig2, file=f'static/visualizations/fundamental_factors/{stock}_surprise.html', auto_open=False)