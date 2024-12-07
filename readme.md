# Stock Analysis Application 📈

This application is designed to analyze stocks based on user input and provide visualizations for specific stocks. It also includes a backtesting module to evaluate the performance of the app's predictions over historical data.

## Features

- **Stock Analysis**: Analyze stocks based on various technical indicators.
- **Visualizations**: Generate visualizations for stock data and patterns.
- **Backtesting**: Evaluate the performance of trading strategies over historical data.
- **News and Earnings Data**: Retrieve and display the latest news and earnings data for stocks.

## Project Structure

```
.
├── __pycache__/
├── api_keys.json
├── app.py
├── backtest_strategy.py
├── bullish_signals_indicators.py
├── fundamental_factors.py
├── preprocessed_data/
├── readme.md
├── requirements.txt
├── static/
│   ├── javascript.js
│   ├── main.css
│   └── visualizations/
├── stock_functions.py
├── technical_analysis/
│   └── bullish_stocks_report.csv
├── templates/
│   ├── backtest.html
│   ├── index.html
│   ├── layout.html
│   ├── report.html
│   ├── stock_analysis.html
│   └── visualization.html
├── venv/
```

## Getting Started

These instructions will get you a copy of the project up and running on your local machine for development and testing purposes.

### Prerequisites

- Python 3.7 or higher 🐍
- Flask 🌶️
- pandas 🐼

You can install the required packages using pip:

```sh
pip install -r requirements.txt
```

### Creating a Python Virtual Environment

1. Open your terminal and navigate to the project directory:

```sh
cd path/to/stock_analysis_app
```

2. Create a new virtual environment. You can name it anything you like, but in this example, we'll call it `venv`:

```sh
python -m venv venv
```

3. Activate the virtual environment. The command to do this will depend on your operating system:

- On Windows:

```sh
venv\Scripts\activate
```

- On Unix or MacOS:

```sh
source venv/bin/activate
```

You'll know the virtual environment is activated because the name of it (in this case, `venv`) will be prepended to your command prompt.

### Running the Application

*IMPORTANT*: You will need to retrieve API keys for the NewsAPI and AlphaVantage APIs. Add these keys to the `api_keys.json` file in the project, replacing the placeholder text with the corresponding keys.

To run the application, navigate to the project directory and run the `app.py` script:

```sh
python app.py
```

The application will start a local server, usually on `http://127.0.0.1:5000/`.

## Using the Application

1. Open your web browser and go to `http://127.0.0.1:5000/`.
2. You will see the index page of the application. Follow the instructions on the page to input your stock preferences.
3. Click on the 'Analyze' button to analyze the stocks based on your input. The results will be saved in a session and you will be redirected to the report page.
4. On the report page, you can view the analysis results.
5. You can also view visualizations for a specific stock by navigating to `http://127.0.0.1:5000/visualization/<stock>`, replacing `<stock>` with the stock symbol.

## Built With

- [Flask](http://flask.pocoo.org/) - The web framework used 🌶️
- [pandas](https://pandas.pydata.org/) - Data analysis library 🐼
- [yfinance](https://github.com/ranaroussi/yfinance) - Stock data retrieving library 📈
- [newsapi](https://newsapi.org/) - API to retrieve news for the stocks 📰
- [alphavantage](https://www.alphavantage.co/) - API to retrieve fundamental factors for the stocks 📊

## Contributing

1. Fork the repository.
2. Create your feature branch (`git checkout -b feature/your-feature`).
3. Commit your changes (`git commit -am 'Add some feature'`).
4. Push to the branch (`git push origin feature/your-feature`).
5. Create a new Pull Request.

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- Special thanks to the developers of the libraries and APIs used in this project.
- Thanks to the contributors who helped improve this project.

## Contact

For any inquiries or feedback, please contact [your-email@example.com].