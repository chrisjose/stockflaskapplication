import datetime
import os
import pika
import psycopg2
import requests

from datetime import datetime, timezone
from dotenv import load_dotenv
from models.stockinfo import StockInfo

load_dotenv()

DATABASE_URL = os.environ.get("DATABASE_URL")
STOCK_API_BASE_URL = os.environ.get("STOCK_API_BASE_URL")
STOCK_API_KEY = os.environ.get("STOCK_API_KEY")


def create_db():
    conn = psycopg2.connect(DATABASE_URL, sslmode='require')
    cursor = conn.cursor()
    try:
        cursor.execute("CREATE TABLE IF NOT EXISTS stockinfo (id bigserial primary key,"
                       "symbol text NOT NULL,"
                       "company text NOT NULL,"
                       "price_open float,"
                       "price_close float,"
                       "price_high float,"
                       "price_low float,"
                       "volume int,"
                       "last_updated timestamp default NULL,"
                       "change_percentage float,"
                       "change_difference float);")
        conn.commit()
    except:
        print("Error creating database table")
    finally:
        conn.close()
        cursor.close()

def populate_defaults_db(stockInfo):
    conn = psycopg2.connect(DATABASE_URL, sslmode='require')
    cursor = conn.cursor()

    # Update
    try:
        insert_query = (
            "INSERT INTO stockinfo ("
            "symbol, "
            "company, "
            "price_open, "
            "price_close, "
            "price_high, "
            "price_low, "
            "volume, "
            "last_updated, "
            "change_percentage, "
            "change_difference"
            ") SELECT "
            "%s, %s, %s, %s, %s, %s, %s, %s, %s, %s "
            "WHERE NOT EXISTS (SELECT 1 FROM stockinfo WHERE symbol = %s)"
        )

        cursor.execute(
            insert_query,
            (
                stockInfo.symbol,
                stockInfo.company,
                stockInfo.open,
                stockInfo.close,
                stockInfo.high,
                stockInfo.low,
                stockInfo.volume,
                stockInfo.last_updated,
                stockInfo.change_percentage,
                stockInfo.change_difference,
                stockInfo.symbol
            )
        )
    except Exception as e:
        print(f"Error updating the table for {stockInfo.symbol}: {e}")
    finally:
        conn.commit()
        cursor.close()
        conn.close()


def fetch_data_stock_api(stockInfo):
    """ Fetch and stock data from REST API """
    url = (f'{STOCK_API_BASE_URL}&symbol={stockInfo.symbol}&apikey={STOCK_API_KEY}')
    response = requests.get(url, timeout=30)
    return response.json()


def store_stock_info(stockInfo, api_data):
    """ Store stock information into the database """
    if api_data is not None:
        if "Time Series (Daily)" not in api_data.keys():
            print(f"Invalid data from api for {stockInfo.symbol}")
            return

        timeSeries = api_data["Time Series (Daily)"]
        hasValidData = False

        # We are only getting the last published data
        for date, prices in timeSeries.items():
            stockInfo.open = float(prices['1. open'])
            stockInfo.high = float(prices['2. high'])
            stockInfo.low = float(prices['3. low'])
            stockInfo.close = float(prices['4. close'])
            stockInfo.volume = int(prices['5. volume'])

            # Parse date in format '2024-02-23'
            stockInfo.last_updated = parse_date_from_json(date)

            # Calculate the difference in price
            stockInfo.change_difference = calculate_difference(stockInfo.open, stockInfo.close)

            # Calculate the percentage
            stockInfo.change_percentage = calculate_difference_percentage(stockInfo.open, stockInfo.close)

            hasValidData = True  # we found valid data
            break

        if hasValidData:
            conn = psycopg2.connect(DATABASE_URL, sslmode='require')
            cursor = conn.cursor()

            # Update
            try:
                insert_query = (
                    "UPDATE stockinfo SET "
                    "price_open = %s, "
                    "price_close = %s, "
                    "price_high = %s, "
                    "price_low = %s, "
                    "volume = %s, "
                    "last_updated = %s, "
                    "change_percentage = %s, "
                    "change_difference = %s "
                    "WHERE symbol = %s"
                )

                cursor.execute(
                    insert_query,
                    (
                        stockInfo.open,
                        stockInfo.close,
                        stockInfo.high,
                        stockInfo.low,
                        stockInfo.volume,
                        stockInfo.last_updated,
                        stockInfo.change_percentage,
                        stockInfo.change_difference,
                        stockInfo.symbol
                    )
                )
            except Exception as e:
                print(f"Error updating the table for {stockInfo.symbol}: {e}")
            finally:
                conn.commit()
                cursor.close()
                conn.close()


def parse_date_from_json(date_str: str):
    parsed_date = datetime.strptime(date_str, '%Y-%m-%d')
    return parsed_date


def calculate_difference(price_open: float, price_close: float):
    difference = price_close - price_open
    return difference


def calculate_difference_percentage(price_open: float, price_close: float):
    change_difference = calculate_difference(price_open, price_close)
    change_percentage = float((change_difference / price_open) * 100.0)
    return change_percentage


def main():
    # Create the db if it doesn't exist
    create_db()

    # Access the CLOUDAMQP_URL environment variable and parse it (fallback to localhost)
    url = os.environ.get('CLOUDAMQP_URL')
    params = pika.URLParameters(url)
    connection = pika.BlockingConnection(params)
    channel = connection.channel()  # start a channel
    channel.queue_declare(queue='stockinfoqueue')  # Declare a queue

    # Create a default list of stocks we want to fetch data for
    stocks = [
        StockInfo("IBM", "International Business Machines Corp", 0.0, 0.0, 0.0, 0.0, 0, datetime.now(timezone.utc), 0.0, 0.0),
        StockInfo("MSFT", "Microsoft Corp", 0.0, 0.0, 0.0, 0.0, 0, datetime.now(timezone.utc), 0.0, 0.0),
        # StockInfo("AAPL", "Apple Inc.", 0.0, 0.0, 0.0, 0.0, 0, datetime.now(timezone.utc), 0.0, 0.0),
        # StockInfo("NVDA", "Nvidia Corp", 0.0, 0.0, 0.0, 0.0, 0, datetime.now(timezone.utc), 0.0, 0.0),
        # StockInfo("AMZN", "Amazon.com Inc", 0.0, 0.0, 0.0, 0.0, 0, datetime.now(timezone.utc), 0.0, 0.0),
        # StockInfo("META", "Meta Platforms, Inc. Class A", 0.0, 0.0, 0.0, 0.0, 0, datetime.now(timezone.utc), 0.0, 0.0),
        # StockInfo("GOOGL", "Alphabet Inc. Class A", 0.0, 0.0, 0.0, 0.0, 0, datetime.now(timezone.utc), 0.0, 0.0),
        # StockInfo("BRK.B", "Berkshire Hathaway Class B", 0.0, 0.0, 0.0, 0.0, 0, datetime.now(timezone.utc), 0.0, 0.0),
        # StockInfo("GOOG", "Alphabet Inc. Class C", 0.0, 0.0, 0.0, 0.0, 0, datetime.now(timezone.utc), 0.0, 0.0),
        # StockInfo("TSLA", "Tesla, Inc.", 0.0, 0.0, 0.0, 0.0, 0, datetime.now(timezone.utc), 0.0, 0.0),
        # StockInfo("JPM", "JPMorgan Chase & Co", 0.0, 0.0, 0.0, 0.0, 0, datetime.now(timezone.utc), 0.0, 0.0)
    ]

    for stockInfo in stocks:
        populate_defaults_db(stockInfo) # Populate the default

    for stockInfo in stocks:
        stock_api_data = fetch_data_stock_api(stockInfo)  # Fetch data
        store_stock_info(stockInfo, stock_api_data)  # Store the fetched data into database

        # Send message to the analyzer for processing information
        channel.basic_publish(exchange='',
                              routing_key='stockinfoqueue',
                              body="calculate")
        print(f"Sent to message queue for {stockInfo.symbol}")

    connection.close()
    print('Complete')


if __name__ == "__main__":
    main()
