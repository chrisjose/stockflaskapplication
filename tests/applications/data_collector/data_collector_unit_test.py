import unittest
from datetime import datetime, timezone
from unittest.mock import patch, Mock

from applications.data_collector.app import store_stock_info, fetch_data_stock_api
from models.stockinfo import StockInfo


class TestDataCollectorApp(unittest.TestCase):

    @patch("requests.get")
    def test_fetch_data_stock_api(self, mock_get):
        mock_response = Mock()
        mock_response.json.return_value = {
            "Time Series (Daily)": {
                "2024-02-23": {
                    "1. open": "184.9000",
                    "2. high": "186.4550",
                    "3. low": "184.5700",
                    "4. close": "185.7200",
                    "5. volume": "3433800"
                }
            }
        }

        mock_get.return_value = mock_response

        stock_data = StockInfo("IBM", "International Business Machines Corp", 0.0, 0.0, 0.0, 0.0, 0, datetime.now(timezone.utc), 0.0, 0.0)
        response = fetch_data_stock_api(stock_data)
        self.assertTrue("Time Series (Daily)" in response.keys())

        timeSeries = response["Time Series (Daily)"]
        for date, prices in timeSeries.items():
            self.assertEqual(float(prices['1. open']), 184.9000)
            self.assertEqual(float(prices['4. close']), 185.7200)
            self.assertEqual(float(prices['3. low']), 184.5700)
            self.assertEqual(float(prices['2. high']), 186.4550)
            self.assertEqual(int(prices['5. volume']), 3433800)


    @patch("psycopg2.connect")
    @patch("psycopg2.extensions.cursor")
    def test_store_stock_info(self, mock_cursor, mock_connect):
        mock_connection = mock_connect.return_value
        mock_cursor_instance = mock_cursor.return_value

        stock_data = StockInfo("IBM", "International Business Machines Corp", 0.0, 0.0, 0.0, 0.0, 0, datetime.now(timezone.utc), 0.0, 0.0)
        api_data = {
            "Time Series (Daily)": {
                "2024-02-23": {
                    "1. open": "184.9000",
                    "2. high": "186.4550",
                    "3. low": "184.5700",
                    "4. close": "185.7200",
                    "5. volume": "3433800"
                }
            }
        }

        store_stock_info(stock_data, api_data)

        mock_connect.assert_called_once()
        mock_cursor_instance.execute.reset_mock()
        mock_connection.commit.assert_called_once()
        mock_connection.close.assert_called_once()


if __name__ == '__main__':
    unittest.main()