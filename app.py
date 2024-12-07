from flask import Flask, render_template, request, redirect, url_for, session
from stock_functions import run_analysis
from backtest_strategy import moving_average_crossover_backtest
from fundamental_factors import get_news_data, analyze_earnings
from json import loads
import pandas as pd

# Initialize Flask application
app = Flask(__name__)
app.secret_key = 'key'  # Important to change if the app is deployed

@app.route('/')
def index():
    """Render the index page."""
    return render_template('index.html')

@app.route('/analyze', methods=['POST'])
def analyze():
    """
    Analyze the stocks based on user input and save the results in a session.
    Redirect to the report page after analysis.
    """
    # Get user inputs
    threshold = float(request.form['threshold'])
    days = int(request.form['days'])
    rsi_threshold = int(request.form['rsi_threshold'])
    stocks = request.form['stocks'].split(',')
    indicators = ['moving_average_crossover', 'rsi_oversold', 'volume_spikes', 'breakouts', 'bollinger_bands', 'exponential_moving_average', 'cup_and_handle', 'ascending_triangle', 'inverse_head_and_shoulders']
    initial_capital = float(request.form['initial_capital'])
    weights = {indicator: request.form.get('weights[' + indicator + ']') for indicator in indicators}

    # Convert weights to a dictionary
    weights_dict = {key: float(value)/100 for key, value in weights.items()}

    # Save user inputs in session
    session['threshold'] = threshold
    session['days'] = days
    session['rsi_threshold'] = rsi_threshold
    session['stocks'] = stocks
    session['initial_capital'] = initial_capital
    session['weights'] = weights_dict

    stock_analysis = []
    errors = []
    # Run analysis for each stock and save the results
    for stock in stocks:
        result = run_analysis(stock, threshold, days, rsi_threshold, weights_dict)
        if 'error' in result:
            errors.append(result['error'])
        else:
            stock_analysis.append(result)

    # Create a DataFrame from the results and save it as a CSV file
    if stock_analysis:
        report = pd.DataFrame(stock_analysis)
        report.to_csv('technical_analysis/bullish_stocks_report.csv', index=False)
        # Save the report in session
        session['report'] = report.to_dict('records')

    # Save errors in session
    session['errors'] = errors

    # Redirect to the report page
    return redirect(url_for('report'))

@app.route('/backtest/<stock>')
def backtest(stock):
    initial_capital = session.get('initial_capital')
    data = pd.read_csv(f'preprocessed_data/{stock}_data.csv', parse_dates=['date'])
    backtest_results = moving_average_crossover_backtest(data, stock, initial_capital)
    news_data = get_news_data(stock)
    analyze_earnings(stock)
    return render_template('backtest.html', backtest_results=backtest_results, stock=stock, news_data=news_data)

@app.route('/report')
def report():
    """
    Render the report page with the analysis results.
    """
    # Get the analysis results from session
    threshold = session.get('threshold')
    days = session.get('days')
    rsi_threshold = session.get('rsi_threshold')
    report = session.get('report')
    errors = session.get('errors', [])

    # Render the report page with the results
    return render_template('report.html', report=report, threshold=threshold, days=days, rsi_threshold=rsi_threshold, errors=errors)

@app.route('/visualization/<stock>')
def visualization(stock):
    """
    Render the visualization page for a specific stock.
    """
    # Render the visualization page with the user inputs from session
    return render_template('visualization.html', stock=stock, days=session.get('days'), threshold=session.get('threshold'), rsi_threshold=session.get('rsi_threshold'))

if __name__ == '__main__':
    # Run the Flask application
    app.run(debug=True)