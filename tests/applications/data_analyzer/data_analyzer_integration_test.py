import unittest
from fastapi.testclient import TestClient
from datetime import datetime, timezone
from unittest.mock import patch, Mock
from applications.data_analyzer.app import app

client = TestClient(app)


class TestDataAnalyzerAppIntegration(unittest.TestCase):

    @patch("psycopg2.connect")
    def test_get_stock_info_from_db(self, mock_connect):

        mock_cursor = Mock()
        mock_cursor.fetchall.return_value = [
            (1, "IBM", "International Business Machines Corp", 10.0, 20.0, 25.0, 5.0, 10001, datetime.now(timezone.utc), 100.0, 10.0)
        ]
        mock_connect.return_value.cursor.return_value = mock_cursor

        response = client.get(
            "/get-stock-info", params={"symbol": "IBM"}
        )
        response_data = response.json()[0]

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response_data["symbol"], "IBM")
        self.assertEqual(response_data["company"], "International Business Machines Corp")
        self.assertEqual(float(response_data["open"]), 10.0)
        self.assertEqual(float(response_data["close"]), 20.0)
        self.assertEqual(float(response_data["high"]), 25.0)
        self.assertEqual(float(response_data["low"]), 5.0)
        self.assertEqual(int(response_data["volume"]), 10001)
        self.assertEqual(float(response_data["change_difference"]), 10.0)
        self.assertEqual(float(response_data["change_percentage"]), 100.0)


if __name__ == '__main__':
    unittest.main()