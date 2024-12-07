import numpy as np
import pandas as pd
from datetime import datetime, timedelta
from bullish_signals_indicators import (moving_average_crossover, rsi_oversold, volume_spikes, breakouts,
                                        find_cup_and_handle, find_ascending_triangle, find_inverse_head_and_shoulders,
                                        bollinger_bands, exponential_moving_average)

def calculate_score(data, stock, days, threshold, rsi_threshold, weights: dict = None):
    """
    This function calculates a score for a given stock based on the appearance of bullish signals
    throughout a specific day range.

    Parameters:
    data (DataFrame): The stock data
    stock (str): The stock symbol
    days (int): The number of days over which to calculate the score
    threshold (float): The threshold for the volume spikes indicator
    rsi_threshold (float): The threshold for the RSI oversold indicator
    weights (dict): The weights for each indicator

    Returns:
    float: Percentage of the overall score
    dict: The scores for each indicator
    list: The dates where the signals were detected
    """
    # Calculate the signals for each indicator
    signals = {
        'moving_average_crossover': moving_average_crossover(data, stock),
        'rsi_oversold': rsi_oversold(data, stock, rsi_threshold),
        'volume_spikes': volume_spikes(data, threshold),
        'breakouts': breakouts(data),
        'bollinger_bands': bollinger_bands(data)[0],
        'exponential_moving_average': exponential_moving_average(data),
        'cup_and_handle': find_cup_and_handle(data)[0],
        'ascending_triangle': find_ascending_triangle(data)[0],
        'inverse_head_and_shoulders': find_inverse_head_and_shoulders(data)[0]
    }

    # Define the current date and the window for the signals
    current_date = datetime.today()
    signal_window = timedelta(days=days)
    
    # Initialize the overall score and the individual scores
    overall_score = 0
    if weights is None:
        weights = {signal: 1 for signal in signals}
    individual_scores = {}
    signal_dates = []
    
    # Calculate the scores for each signal
    for signal, dates in signals.items():
        score = [1 * weights[signal] if (current_date - date) <= signal_window else 0 for date in dates]
        if sum(score) != 0: # If there is at least one signal within the window
            individual_scores[signal] = 1 * weights[signal] # The individual score is 1
            signal_dates.extend(dates)
        else:
            individual_scores[signal] = 0 # If there is not a signal within the window, the individual score is 0
        overall_score += individual_scores[signal]  # Multiply by the weight

    # Normalize the overall score by the sum of the weights
    return overall_score / sum(weights.values()), individual_scores, sorted(signal_dates)

def moving_average_crossover_backtest(data, stock, initial_capital: float = 100000):
    """
    This function implements a simple moving average crossover backtest strategy.
    It generates trading signals based on the crossover of a short-term and a long-term moving average.
    It then calculates the portfolio value over time given these trading signals and an initial capital.
    Finally, it calculates some metrics about the trading strategy, such as ROI, accuracy, precision, and recall.

    Parameters:
    data (DataFrame): The stock price data.
    stock (str): The stock symbol.
    initial_capital (float): The initial capital for the backtest. Default is 100000.

    Returns:
    dict: A dictionary containing the final portfolio value, ROI, accuracy, precision, and recall.
    """

    # Initialize signals DataFrame with 0s
    signals = pd.DataFrame(index=data.index)
    signals['signal'] = 0.0

    # Generate trading signals based on moving average crossover
    signals['signal'] = np.where(data[f'{stock}_50_day_ma'] > data[f'{stock}_200_day_ma'], 1.0, 0.0)
    signals['positions'] = signals['signal'].diff()

    # Initialize the portfolio with the positions
    positions = pd.DataFrame(index=signals.index).fillna(0.0)
    positions[stock] = signals['signal']
    portfolio = pd.DataFrame(index=signals.index)
    pos_diff = positions.diff()

    # Calculate the holdings (stock value) and cash over time
    portfolio['holdings'] = (positions.multiply(data['close'], axis=0)).sum(axis=1)
    portfolio['cash'] = initial_capital - (pos_diff.multiply(data['close'], axis=0)).sum(axis=1).cumsum()

    # Calculate the total portfolio value and the returns
    portfolio['total'] = portfolio['cash'] + portfolio['holdings']
    portfolio['returns'] = portfolio['total'].pct_change()

    # Calculate metrics about the trades
    trades = signals[signals['positions'] != 0].copy()
    trades.loc[:, 'trade_return'] = trades['positions'] * data['close'].pct_change()

    # Calculate the number of true positives, false positives, false negatives, and true negatives
    true_positive = ((trades['trade_return'] > 0) & (trades['positions'] == 1.0)).sum()
    false_positive = ((trades['trade_return'] < 0) & (trades['positions'] == 1.0)).sum()
    false_negative = ((trades['trade_return'] > 0) & (trades['positions'] == -1.0)).sum()
    true_negative = ((trades['trade_return'] < 0) & (trades['positions'] == -1.0)).sum()

    # Calculate the total number of trades
    total_trades = true_positive + false_positive + false_negative + true_negative

    # Calculate accuracy, precision, recall, and ROI
    accuracy = (true_positive + true_negative) / total_trades if total_trades > 0 else 0
    precision = true_positive / (true_positive + false_positive) if (true_positive + false_positive) > 0 else 0
    recall = true_positive / (true_positive + false_negative) if (true_positive + false_negative) > 0 else 0
    roi = (portfolio['total'].iloc[-1] - initial_capital) / initial_capital

    # Return the results as a dictionary
    results = {
        'final_portfolio_value': portfolio['total'].iloc[-1],
        'roi': roi,
        'accuracy': accuracy,
        'precision': precision,
        'recall': recall
    }

    return results