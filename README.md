# Stock Application using Python/Flask

The **Stock Application** is a Python/Flask based web application 
that provides stock data by fetching it from AlphaVantage.co REST API.

Due to the limitations in the free REST API, we will only be providing 
historical data for limited number of stocks.

## Flowchart Diagram
![flowchart.png](images%2Fflowchart.png)

## Features

- Fetches the stock data from Alphavantage.co REST API
- Displays the previous day's open/close pricing
- Calculates the growth on these stocks by providing a percentage
- Shows the metrics data by connecting to Prometheus
- Utilizes RabbitMQ message queue system to communicate between applications
- A simple, but user-friendly web frontend using Flask

## Testing Instructions

1. Access the web application from `http://***.heroku.com`
3. Use the dropdown to select a stock you want to fetch data for
4. Click submit button 

Note: Due to the limitations in free REST API, we will only be providing
historical data for a limited number of stocks.

## Installation

1. Make sure to install all the dependencies
2. Setup and activate the virtual environment with `python3 -m venv venv` and `source venv/bin/activate`
3. Install the requirements using pip by `pip install -r requirements.txt`
4. Configure the environment variables in .env file (certain ones are private)
5. Proceed to running the microservices

## Usage

Run the microservices below:

- Data Collector: `python applications/data_collector/app.py`
- Data Analyzer: `python applications/data_analyzer/app.py`
- Web App: `python applications/web/app.py`

1. Once the web app is running, access from your browser by going to `http://localhost:5000`
3. Use the dropdown to select a stock you want to fetch data for
4. Click submit button 

## Endpoints

- `/health` - Endpoint to get the health check and returns 200 OK
- `/metrics` - For Prometheus metrics, this endpoint can be used

![prometheus.png](images%2Fprometheus.png)
