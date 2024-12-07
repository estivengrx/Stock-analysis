import pandas as pd
from scipy.signal import find_peaks

def moving_average_crossover(data, stock):
    """
    Identifies the dates when the 50-day moving average crosses above the 200-day moving average for a given stock.

    Parameters:
    data (pandas.DataFrame): A DataFrame containing moving average data for various stocks.
                             Expected to have columns named '{stock}_50_day_ma' and '{stock}_200_day_ma'.
    stock (str): The stock symbol to analyze.

    Returns:
    list: A list of dates (as contained in the 'date' column of the DataFrame) when the 50-day moving average
          crosses above the 200-day moving average.
    """

    # Extract the 50-day moving average for the given stock
    fifty_ma = data[f'{stock}_50_day_ma']

    # Extract the 200-day moving average for the given stock
    two_hundred_ma = data[f'{stock}_200_day_ma']

    # Identify where the 50-day MA is greater than the 200-day MA
    # and the previous day it was less than the 200-day MA
    crossover = (fifty_ma > two_hundred_ma) & (fifty_ma.shift(1) < two_hundred_ma.shift(1))

    # Return the list of dates where the crossover condition is met
    return data.loc[crossover, 'date'].tolist()

def rsi_oversold(data, stock, threshold=30):
    """
    Identifies the dates when the RSI (Relative Strength Index) of a given stock falls below a specified threshold.

    Parameters:
    data (pandas.DataFrame): A DataFrame containing RSI data for various stocks.
                             Expected to have a column named '{stock}_rsi'.
    stock (str): The stock symbol to analyze.
    threshold (int): The RSI threshold to identify oversold conditions. Default is 30.
    20-25 to reduce false signals
    35-40 to detect more signals

    Returns:
    list: A list of dates (as contained in the 'date' column of the DataFrame) when the RSI is below the threshold.
    """

    # Return the list of dates where the RSI is below the specified threshold
    return data.loc[data[f'{stock}_rsi'] < threshold, 'date'].tolist()

def volume_spikes(data, threshold=2):
    """
    Identifies the dates when the trading volume is significantly higher than the average volume.

    Parameters:
    data (pandas.DataFrame): A DataFrame containing stock data including 'volume' and 'close' prices.
    threshold (int): The multiplier to identify volume spikes. Default is 2.

    Returns:
    list: A list of dates (as contained in the 'date' column of the DataFrame) when the volume spikes.
    """

    # Calculate the rolling average volume over the past 50 days
    avg_volume = data['volume'].rolling(window=50, min_periods=1).mean()

    # Identify where the volume is greater than the threshold times the average volume
    # and the closing price is higher than the previous day's closing price
    volume_spike = (data['volume'] > threshold * avg_volume) & (data['close'] > data['close'].shift(1))

    # Return the list of dates where the volume spike condition is met
    return data.loc[volume_spike, 'date'].tolist()

def breakouts(data):
    """
    Identifies the dates when the closing price breaks above the highest high of the past 50 days.

    Parameters:
    data (pandas.DataFrame): A DataFrame containing stock data including 'high' and 'close' prices.

    Returns:
    list: A list of dates (as contained in the 'date' column of the DataFrame) when the breakout occurs.
    """

    # Calculate the highest high over the past 50 days
    data['high_max'] = data['high'].rolling(window=50, min_periods=1).max()

    # Identify where the closing price is higher than the previous day's highest high
    breakout = data['close'] > data['high_max'].shift(1)

    # Return the list of dates where the breakout condition is met
    return data.loc[breakout, 'date'].tolist()

def bollinger_bands(data, window=20, num_std=2):
    """
    Identifies the dates when the closing price crosses above the lower Bollinger Band
    and calculates the Bollinger Bands.

    Parameters:
    data (pandas.DataFrame): A DataFrame containing stock data including 'close' prices.
    window (int): The window size for calculating the moving average and standard deviation.
    num_std (int): The number of standard deviations for the Bollinger Bands. Default is 2.

    Returns:
    list: A list of dates when the closing price crosses above the lower Bollinger Band.
    pandas.Series: The upper Bollinger Band.
    pandas.Series: The lower Bollinger Band.
    """

    # Calculate the rolling mean and standard deviation
    rolling_mean = data['close'].rolling(window).mean()
    rolling_std = data['close'].rolling(window).std()

    # Calculate the upper and lower Bollinger Bands
    upper_band = rolling_mean + (rolling_std * num_std)
    lower_band = rolling_mean - (rolling_std * num_std)

    # Identify where the closing price crosses above the lower band
    bullish_signal = (data['close'] > lower_band) & (data['close'].shift(1) < lower_band.shift(1))

    # Return the list of dates where the bullish signal condition is met and the Bollinger Bands
    return data.loc[bullish_signal, 'date'].tolist(), upper_band, lower_band

def exponential_moving_average(data, span=20):
    """
    Identifies the dates when the closing price crosses above the Exponential Moving Average (EMA).

    Parameters:
    data (pandas.DataFrame): A DataFrame containing stock data including 'close' prices.
    span (int): The span for calculating the EMA. Default is 20.

    Returns:
    list: A list of dates (as contained in the 'date' column of the DataFrame) when the closing price
          crosses above the EMA.
    """

    # Calculate the Exponential Moving Average (EMA)
    ema = data['close'].ewm(span=span).mean()

    # Identify where the closing price crosses above the EMA
    bullish_signal = (data['close'] > ema) & (data['close'].shift(1) < ema.shift(1))

    # Return the list of dates where the bullish signal condition is met
    return data.loc[bullish_signal, 'date'].tolist()

def find_cup_and_handle(data, window=50):
    """
    Identifies potential 'Cup and Handle' patterns in the stock data.

    Parameters:
    data (pandas.DataFrame): A DataFrame containing stock data including 'close' prices.
    window (int): The minimum number of data points between peaks. Default is 50.

    Returns:
    tuple: A tuple containing two lists:
           1. A list of dates (as contained in the 'date' column of the DataFrame) when the pattern completes.
           2. A list of tuples with start and end dates (as contained in the 'date' column of the DataFrame)
              for each identified pattern.
    """

    patterns = []
    patterns_between = []
    close_prices = data['close'].values

    # Identify peaks in the closing prices
    peaks, _ = find_peaks(close_prices, distance=window)

    for i in range(len(peaks) - 2):
        left_peak, center_peak, right_peak = peaks[i], peaks[i+1], peaks[i+2]

        # Check if the pattern meets the 'Cup and Handle' criteria
        if close_prices[left_peak] < close_prices[center_peak] and close_prices[right_peak] < close_prices[center_peak]:
            cup_bottom = close_prices[left_peak:center_peak].min()
            handle_bottom = close_prices[center_peak:right_peak].min()

            if handle_bottom > cup_bottom and close_prices[right_peak] > close_prices[center_peak] * 0.95:
                patterns.append(data['date'].iloc[right_peak])
                patterns_between.append((data['date'].iloc[left_peak], data['date'].iloc[right_peak]))

    return patterns, patterns_between

def find_ascending_triangle(data, window=50):
    """
    Identifies potential 'Ascending Triangle' patterns in the stock data.

    Parameters:
    data (pandas.DataFrame): A DataFrame containing stock data including 'close' prices.
    window (int): The minimum number of data points between peaks and troughs. Default is 50.

    Returns:
    tuple: A tuple containing two lists:
           1. A list of dates (as contained in the 'date' column of the DataFrame) when the pattern completes.
           2. A list of tuples with start and end dates (as contained in the 'date' column of the DataFrame)
              for each identified pattern.
    """

    patterns = []
    patterns_between = []
    close_prices = data['close'].values

    # Identify peaks and troughs in the closing prices
    peaks, _ = find_peaks(close_prices, distance=window)
    troughs, _ = find_peaks(-close_prices, distance=window)

    for i in range(len(peaks) - 1):
        left_peak, right_peak = peaks[i], peaks[i+1]
        relevant_troughs = [t for t in troughs if left_peak < t < right_peak]

        if not relevant_troughs:
            continue

        min_trough = min(relevant_troughs, key=lambda x: close_prices[x])

        if close_prices[min_trough] > close_prices[left_peak] * 0.95:
            patterns.append(data['date'].iloc[right_peak])
            patterns_between.append((data['date'].iloc[left_peak], data['date'].iloc[right_peak]))

    return patterns, patterns_between

def find_inverse_head_and_shoulders(data, window=50):
    """
    Identifies potential 'Inverse Head and Shoulders' patterns in the stock data.

    Parameters:
    data (pandas.DataFrame): A DataFrame containing stock data including 'close' prices.
    window (int): The minimum number of data points between peaks. Default is 50.

    Returns:
    tuple: A tuple containing two lists:
           1. A list of dates (as contained in the 'date' column of the DataFrame) when the pattern completes.
           2. A list of tuples with start and end dates (as contained in the 'date' column of the DataFrame)
              for each identified pattern.
    """

    patterns = []
    patterns_between = []
    close_prices = data['close'].values

    # Identify peaks (inverted, as this is an inverse pattern) in the closing prices
    peaks, _ = find_peaks(-close_prices, distance=window)

    for i in range(len(peaks) - 2):
        left_shoulder, head, right_shoulder = peaks[i], peaks[i+1], peaks[i+2]

        # Check if the pattern meets the 'Inverse Head and Shoulders' criteria
        if close_prices[left_shoulder] > close_prices[head] and close_prices[right_shoulder] > close_prices[head]:
            patterns.append(data['date'].iloc[right_shoulder])
            patterns_between.append((data['date'].iloc[left_shoulder], data['date'].iloc[right_shoulder]))

    return patterns, patterns_between