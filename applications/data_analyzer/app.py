# The data analyzer application is triggered by RabbitMQ message queue
# Runs on the existing collection of data
# Calculates the change in stock prices and the growth percentage
import asyncio
import json
import os
import pika
import psycopg2
import uvicorn

from dotenv import load_dotenv
from models.stockinfo import StockInfo
from datetime import datetime
from flask import Flask, request, Response

load_dotenv()

DATABASE_URL = os.environ.get("DATABASE_URL")

app = Flask(__name__)

@app.route("/get-stock-info", methods=['GET'])
def get_stock_info_from_db():
    symbol = request.args.get('symbol')

    conn = psycopg2.connect(DATABASE_URL, sslmode='require')
    cursor = conn.cursor()
    stockInfo = []

    try:
        if symbol is not None and symbol != "":
            fetch_query = f"SELECT * FROM stockinfo " \
                          f"WHERE symbol = '{symbol}'"

            cursor.execute(fetch_query)
        else:
            fetch_query = ("SELECT * FROM stockinfo")
            cursor.execute(fetch_query)

        db_stocks = cursor.fetchall()

        # Process the fetched rows
        for item in db_stocks:
            stockInfo.append(
                StockInfo(item[1], item[2], item[3], item[4], item[5], item[6], item[7], item[8], item[9], item[10]))

    except Exception as e:
        print(f"Error updating the table for {symbol}: {e}")
    finally:
        conn.commit()
        cursor.close()
        conn.close()

    dict_list = [obj.__dict__ for obj in stockInfo]
    json_string = json.dumps(dict_list, indent=4, sort_keys=True, default=str)

    return Response(response=json_string, status=200, mimetype="application/json")


def analyze_data_on_call():
    """
        We analyze the data that is present in DB
        Once we get a notification from the message queue
    """
    conn = psycopg2.connect(DATABASE_URL, sslmode='require')
    cursor = conn.cursor()
    stockInfo = []

    try:
        fetch_query = ("SELECT * FROM stockinfo")
        cursor.execute(fetch_query)

        db_stocks = cursor.fetchall()

        # Process the fetched rows
        for item in db_stocks:
            stockInfo.append(
                StockInfo(item[1], item[2], item[3], item[4], item[5], item[6], item[7], item[8], item[9], item[10]))

        for item in stockInfo:
            # Calculate the difference in price
            item.change_difference = calculate_difference(item.open, item.close)

            # Calculate the percentage
            item.change_percentage = calculate_difference_percentage(item.open, item.close)

            # Update
            try:
                update_query = (
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
                    update_query,
                    (
                        item.open,
                        item.close,
                        item.high,
                        item.low,
                        item.volume,
                        item.last_updated,
                        item.change_percentage,
                        item.change_difference,
                        item.symbol
                    )
                )
            except Exception as e:
                print(f"Error updating the table for {item.symbol}: {e}")
            finally:
                conn.commit()
    except Exception as e:
        print(f"Error analyzing stock info: {e}")
    finally:
        cursor.close()
        conn.close()

    return True


def calculate_difference(price_open: float, price_close: float):
    difference = price_close - price_open
    return difference


def calculate_difference_percentage(price_open: float, price_close: float):
    change_difference = calculate_difference(price_open, price_close)
    change_percentage = float((change_difference / price_open) * 100.0)
    return change_percentage


async def consume_message_queue():
    # Access the CLOUDAMQP_URL environment variable and parse it (fallback to localhost)
    url = os.environ.get('CLOUDAMQP_URL')
    params = pika.URLParameters(url)
    connection = pika.BlockingConnection(params)
    channel = connection.channel()  # start a channel
    channel.queue_declare(queue='stockinfoqueue')  # Declare a queue

    def callback(ch, method, properties, body):
        print("Received message: " + str(body))
        analyze_data_on_call()  # Analyze the stock information in database

    channel.basic_consume('stockinfoqueue',
                          callback,
                          auto_ack=True)

    print(' [*] Waiting for messages:')
    channel.start_consuming()
    connection.close()


if __name__ == '__main__':
    app.run()
