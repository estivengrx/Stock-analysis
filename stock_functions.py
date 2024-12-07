import os
import pandas as pd
import yfinance as yf
import matplotlib.pyplot as plt
import plotly.graph_objects as go
import plotly.io as pio
from ta.momentum import RSIIndicator
from warnings import filterwarnings
from backtest_strategy import calculate_score, moving_average_crossover_backtest
from bullish_signals_indicators import find_cup_and_handle, find_ascending_triangle, find_inverse_head_and_shoulders, bollinger_bands
import matplotlib
matplotlib.use('Agg')
# filterwarnings("ignore")

# Create directories if they don't exist
os.makedirs('preprocessed_data', exist_ok=True)
os.makedirs('static/visualizations', exist_ok=True)

def download_and_preprocess_stock_data(stock):
    """
    Download and preprocess stock data from Yahoo Finance.
    Calculate 50-day and 200-day moving averages and RSI.
    Save the preprocessed data as a CSV file.
    """
    try:
        # Download stock data
        data = yf.download(stock, period='max').reset_index()
        if data.empty or 'No timezone found, symbol may be delisted' in data.to_string():
            raise ValueError(f"The stock ticker symbol {stock} is not valid.")
        
        # Preprocess the data
        data.columns = data.columns.str.lower().str.replace(' ', '_')
        data.ffill(inplace=True)
        data.bfill(inplace=True)
        
        for col in data.columns:
            if data[col].dtype != 'datetime64[ns]':
                data[col] = pd.to_numeric(data[col], errors='coerce')
        
        # Calculate moving averages and RSI
        data[f'{stock}_50_day_ma'] = data['close'].rolling(window=50).mean()
        data[f'{stock}_200_day_ma'] = data['close'].rolling(window=200).mean()
        data[f'{stock}_rsi'] = RSIIndicator(close=data['close']).rsi()
        
        # Save the preprocessed data
        data.to_csv(f'preprocessed_data/{stock}_data.csv', index=False)
        return None  # Indicate success
    except Exception as e:
        return str(e)  # Return the error message

def visualize_stock(data, stock):
    """
    Visualize the stock data with Plotly.
    Plot the close price and the 50-day and 200-day moving averages.
    Save the plot as an HTML file.
    """
    filename = f'static/visualizations/bullish_signals/{stock}_chart.html'

    fig = go.Figure()

    # Add traces for the close price and the moving averages
    fig.add_trace(go.Scatter(x=data['date'], y=data['close'], mode='lines', name='Close Price'))
    fig.add_trace(go.Scatter(x=data['date'], y=data[f'{stock}_50_day_ma'], mode='lines', name='50-Day MA'))
    fig.add_trace(go.Scatter(x=data['date'], y=data[f'{stock}_200_day_ma'], mode='lines', name='200-Day MA'))

    # Update layout
    fig.update_layout(
        title=f"{stock} Stock Prices and Moving Averages (50 and 200 day)",
        xaxis_title="Date",
        yaxis_title="Price",
        legend_title="Legend",
    )

    # Save the plot
    pio.write_html(fig, file=filename, auto_open=False)

def visualize_stock_patterns(data, stock):
    """
    Visualize the stock data with Plotly.
    Plot the close price and the bullish patterns (Cup-and-Handle, Ascending Triangle, Inverse Head-and-Shoulders,
    Bollinger Bands, and RSI). Save the plots as HTML files.
    """
    _, cup_and_handle_patterns = find_cup_and_handle(data)
    _, ascending_triangle_patterns = find_ascending_triangle(data)
    _, inverse_head_and_shoulders_patterns = find_inverse_head_and_shoulders(data)

    # Cup-and-Handle patterns
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=data['date'], y=data['close'], mode='lines', name='Close Price'))
    for i, pattern in enumerate(cup_and_handle_patterns):
        pattern_data = data[(data['date'] >= pattern[0]) & (data['date'] <= pattern[1])]
        fig.add_trace(go.Scatter(x=pattern_data['date'], y=pattern_data['close'], mode='lines', name='Cup-and-Handle Pattern' if i == 0 else '', line=dict(color='red'), showlegend=i == 0))
    fig.update_layout(title='Stock Price with Cup-and-Handle Patterns', xaxis_title='Date', yaxis_title='Close Price')
    pio.write_html(fig, file=f'static/visualizations/bullish_signals/{stock}_cup_and_handle.html', auto_open=False)

    # Triangle patterns
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=data['date'], y=data['close'], mode='lines', name='Close Price'))
    for i, pattern in enumerate(ascending_triangle_patterns):
        pattern_data = data[(data['date'] >= pattern[0]) & (data['date'] <= pattern[1])]
        fig.add_trace(go.Scatter(x=pattern_data['date'], y=pattern_data['close'], mode='lines', name='Ascending Triangle Pattern' if i == 0 else '', line=dict(color='#FF4500'), showlegend=i == 0))
    fig.update_layout(title='Stock Price with Ascending Triangle Patterns', xaxis_title='Date', yaxis_title='Close Price')
    pio.write_html(fig, file=f'static/visualizations/bullish_signals/{stock}_ascending_triangle.html', auto_open=False)

    # Inverse Head-and-Shoulders patterns
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=data['date'], y=data['close'], mode='lines', name='Close Price'))
    for i, pattern in enumerate(inverse_head_and_shoulders_patterns):
        pattern_data = data[(data['date'] >= pattern[0]) & (data['date'] <= pattern[1])]
        fig.add_trace(go.Scatter(x=pattern_data['date'], y=pattern_data['close'], mode='lines', name='Inverse Head-and-Shoulders Pattern' if i == 0 else '', line=dict(color='blue'), showlegend=i == 0))
    fig.update_layout(title='Stock Price with Inverse Head-and-Shoulders Patterns', xaxis_title='Date', yaxis_title='Close Price')
    pio.write_html(fig, file=f'static/visualizations/bullish_signals/{stock}_inverse_head_and_shoulders.html', auto_open=False)

    # Bollinger Bands visualization
    _, upper_band, lower_band = bollinger_bands(data)

    fig = go.Figure()
    fig.add_trace(go.Scatter(x=data['date'], y=data['close'], mode='lines', name='Close Price', line=dict(color='black'), line_width=0.5))
    fig.add_trace(go.Scatter(x=data['date'], y=upper_band, mode='lines', name='Upper Bollinger Band', line=dict(color='green'), line_width=0.6))
    fig.add_trace(go.Scatter(x=data['date'], y=lower_band, mode='lines', name='Lower Bollinger Band', line=dict(color='green'), line_width=0.6, fill='tonexty'))
    fig.update_layout(title='Stock Price with Bollinger Bands', xaxis_title='Date', yaxis_title='Close Price')
    pio.write_html(fig, file=f'static/visualizations/bullish_signals/{stock}_bollinger_bands.html', auto_open=False)

    # RSI visualization
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=data['date'], y=data[f'{stock}_rsi'], mode='lines', name='RSI'))
    # Add overbought level
    fig.add_shape(type="line", x0=data['date'].min(), x1=data['date'].max(), y0=70, y1=70, line=dict(color="Red", width=0.5, dash="dash"))
    fig.add_trace(go.Scatter(x=[data['date'].iloc[-1]], y=[70], mode='lines', line=dict(color="Red", width=0.5), showlegend=True, name='Overbought (70)'))

    # Add oversold level
    fig.add_shape(type="line", x0=data['date'].min(), x1=data['date'].max(), y0=30, y1=30, line=dict(color="Blue", width=0.5, dash="dash"))
    fig.add_trace(go.Scatter(x=[data['date'].iloc[-1]], y=[30], mode='lines', line=dict(color="Blue", width=0.5), showlegend=True, name='Oversold (30)'))
    fig.update_layout(title='RSI', xaxis_title='Date', yaxis_title='RSI')  # Add range slider
    pio.write_html(fig, file=f'static/visualizations/bullish_signals/{stock}_rsi.html', auto_open=False)

def run_analysis(stock, threshold=0.05, days=10, rsi_threshold=30, weights_dict=None):
    """
    Run the analysis for a specific stock.
    Download and preprocess the stock data if it doesn't exist.
    Calculate the score for the stock based on various indicators.
    Visualize the stock data and the bullish patterns.
    Return the analysis results.
    """
    preprocessed_file_path = f'preprocessed_data/{stock}_data.csv'
    
    if not os.path.exists(preprocessed_file_path):
        error = download_and_preprocess_stock_data(stock)
        if error:
            return {'stock': stock, 'error': error}
    
    data = pd.read_csv(preprocessed_file_path, parse_dates=['date'])

    score, individual_scores, _ = calculate_score(data, stock, days=days, threshold=threshold, rsi_threshold=rsi_threshold, weights=weights_dict)
    recommendation = "Trade" if score > 0.5 else "Don't Trade"

    visualize_stock_patterns(data, stock)
    visualize_stock(data, stock)
    result = {
        'stock': stock,
        'moving_average_crossover': individual_scores['moving_average_crossover'],
        'rsi_oversold': individual_scores['rsi_oversold'],
        'volume_spikes': individual_scores['volume_spikes'],
        'breakouts': individual_scores['breakouts'],
        'bollinger_bands': individual_scores['bollinger_bands'],
        'exponential_moving_average': individual_scores['exponential_moving_average'],
        'cup_and_handle': individual_scores['cup_and_handle'],
        'ascending_triangle': individual_scores['ascending_triangle'],
        'inverse_head_and_shoulders': individual_scores['inverse_head_and_shoulders'],
        'overall_score': score,
        'recommendation': recommendation
    }

    return result