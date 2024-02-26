import os
import requests
from flask import Flask, render_template, request
from dotenv import load_dotenv
from prometheus_client import Counter, generate_latest


load_dotenv()

app = Flask(__name__)

REQUESTS = Counter("web_requests_total", "HTTP requests since web app was started.")

DATA_ANALYZER_SERVICE_ENDPOINT = (
    f"http://{os.getenv('DATA_ANALYZER_SERVICE_HOST')}:{os.getenv('DATA_ANALYZER_SERVICE_PORT')}"
)

@app.before_request
def before_request():
    REQUESTS.inc()


@app.route('/health', methods=['GET'])
def health():
    return "success", 200


@app.route('/metrics', methods=['GET'])
def metrics():
    return generate_latest()


@app.route('/', methods=['GET', 'POST'])
def index():
    """Render the index.html template with stock data."""
    if request.method == 'POST':
        symbol = request.form['dropdown']
        stock_data = requests.get(
            DATA_ANALYZER_SERVICE_ENDPOINT
            + f"/get-stock-info?symbol={symbol}"
        ).json()
    else:
        stock_data = []
        symbol = ""

    return render_template('index.html',
                           stock_data=stock_data,
                           selected_option=symbol)


if __name__ == '__main__':
    app.run()
