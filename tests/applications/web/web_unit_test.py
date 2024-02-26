import unittest
from applications.web.app import app


class TestWeb(unittest.TestCase):

    def setUp(self):
        self.app = app.test_client()

    def test_health_endpoint(self):
        endpoint_response = self.app.get('/health')
        self.assertEqual(endpoint_response.status_code, 200)

    def test_metrics_endpoint(self):
        endpoint_response = self.app.get('/metrics')
        self.assertEqual(endpoint_response.status_code, 200)


if __name__ == '__main__':
    unittest.main()
