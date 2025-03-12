import io
import random
from datetime import datetime, timedelta
import os

import requests
from flask import Flask, render_template, send_file
from matplotlib import pyplot as plt
from dotenv import load_dotenv

load_dotenv()  
api_key = os.getenv("COINAPI_KEY") 

app = Flask(__name__)


# Generate 30 random prices
def generate_random_prices():
    min_price = 100
    max_price = 100000
    return [round(random.uniform(min_price, max_price), 2) for _ in range(30)]


# Function to generate dates for the last 30 days
def generate_dates():
    end_date = datetime.now()
    start_date = end_date - timedelta(days=30)
    return [start_date + timedelta(days=i) for i in range(30)]


class Cryptocurrency:
    def __init__(self, name, symbol, market_cap):
        self.name = name
        self.symbol = symbol
        self.prices = generate_random_prices()
        self.market_cap = market_cap

    def __str__(self):
        return f"{self.name} ({self.symbol}): Price - ${self.prices[len(self.prices) - 1]}, Market Cap - ${self.market_cap}"

    def set_prices(self, prices):
        self.prices = prices


# Sample data
cryptocurrencies = [
    Cryptocurrency(name="Bitcoin", symbol="BTC", market_cap=1.1e12),
    Cryptocurrency(name="Ethereum", symbol="ETH", market_cap=300e9),
    # Cryptocurrency(name="Binance Coin", symbol="BNB", market_cap=90e9),
    Cryptocurrency(name="Cardano", symbol="ADA", market_cap=60e9),
    Cryptocurrency(name="Solana", symbol="SOL", market_cap=50e9),
    Cryptocurrency(name="XRP", symbol="XRP", market_cap=45e9),
    Cryptocurrency(name="Polkadot", symbol="DOT", market_cap=40e9),
    Cryptocurrency(name="Dogecoin", symbol="DOGE", market_cap=30e9),
    Cryptocurrency(name="Avalanche", symbol="AVAX", market_cap=20e9),
    Cryptocurrency(name="Chainlink", symbol="LINK", market_cap=15e9),
    Cryptocurrency(name="Litecoin", symbol="LTC", market_cap=10e9),
    Cryptocurrency(name="Stellar", symbol="XLM", market_cap=8e9),
    # Cryptocurrency(name="Terra", symbol="LUNA", market_cap=7e9),
    Cryptocurrency(name="Uniswap", symbol="UNI", market_cap=6e9),
    Cryptocurrency(name="Bitcoin Cash", symbol="BCH", market_cap=5e9),
    # Cryptocurrency(name="VeChain", symbol="VET", market_cap=4e9),
    Cryptocurrency(name="Algorand", symbol="ALGO", market_cap=3e9),
    # Cryptocurrency(name="Cosmos", symbol="ATOM", market_cap=2e9),
    # Cryptocurrency(name="Filecoin", symbol="FIL", market_cap=1e9),
    # Cryptocurrency(name="Tron", symbol="TRX", market_cap=0.9e9)
]


@app.route('/')
def home():
    return render_template('index.html', cryptocurrencies=cryptocurrencies)


@app.route('/crypto/<name>')
def price(name):
    for crypto in cryptocurrencies:
        if crypto.name.lower() == name.lower():
            return render_template('crypto.html', cryptocurrency=crypto)
    return "Cryptocurrency not found"


# Route to generate and serve the price graph image
@app.route('/plot/<name>')
def plot_price(name):
    # Find the cryptocurrency object by symbol
    for crypto in cryptocurrencies:
        if crypto.name.lower() == name.lower():
            cryptocurrency = crypto
            break
    else:
        return "Cryptocurrency not found", 404

    # Generate dates and prices for the last 30 days
    dates = generate_dates()
    prices = cryptocurrency.prices

    # Plot prices
    plt.figure(figsize=(10, 6))
    plt.plot(dates, prices, marker='o', linestyle='-')
    plt.title(f'Price of {cryptocurrency.name} over the last 30 days')
    plt.xlabel('Date')
    plt.ylabel('Price ($)')
    plt.xticks(rotation=45)
    plt.grid(True)
    plt.tight_layout()

    # Save the plot to a BytesIO object
    img_buf = io.BytesIO()
    plt.savefig(img_buf, format='png')
    img_buf.seek(0)

    # Clear the plot to avoid memory leaks
    plt.close()

    # Serve the plot image
    return send_file(img_buf, mimetype='image/png')


def calculate_percentage_change(prices, num_days):
    # Check if prices data is available
    if len(prices) < num_days:
        return "Insufficient data"

    # Calculate percentage change
    last_price = prices[-1]
    first_price = prices[-num_days]
    percentage_change = ((last_price - first_price) / first_price) * 100
    formatted = "{:,.2f}".format(percentage_change)
    return f"{formatted}%"


@app.route('/currencies')
def currencies_table():
    cryptocurrencies_with_change = [
        {'crypto': crypto,
         'percentage_change_1day': calculate_percentage_change(crypto.prices, 2),
         'percentage_change_7days': calculate_percentage_change(crypto.prices, 7),
         'percentage_change_30days': calculate_percentage_change(crypto.prices, 30)
         } for crypto in cryptocurrencies]
    return render_template('currencies.html', cryptocurrencies=cryptocurrencies_with_change)


def load_currencies():
    current_time = (datetime.now() - timedelta(days=30)).strftime('%Y-%m-%dT%H:%M:%S')

    for currency in cryptocurrencies:
        try:
            url = f"https://rest.coinapi.io/v1/ohlcv/BITSTAMP_SPOT_{currency.symbol}_USD/history?apikey={api_key}&period_id=1DAY&time_start={current_time}&limit=360"
            response = requests.get(url)
            data = response.json()
            currency.set_prices([item['price_close'] for item in data])
        except Exception:
            print(f"Error for {currency.name}")


if __name__ == '__main__':
    load_currencies()
    app.run(debug=True)
