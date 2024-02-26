import unittest
from applications.data_analyzer.app import calculate_difference, calculate_difference_percentage

class TestDataAnalyzerApp(unittest.TestCase):

    def test_calculate_difference(self):
        difference1 = calculate_difference(10, 5)
        self.assertEqual(difference1, -5)

        difference2 = calculate_difference(2, 6)
        self.assertEqual(difference2, 4)

    def test_calculate_difference_percentage(self):
        difference_percent1 = calculate_difference_percentage(10, 5)
        self.assertEqual(difference_percent1, -50.0)

        difference_percent2 = calculate_difference_percentage(2, 4)
        self.assertEqual(difference_percent2, 100)


if __name__ == '__main__':
    unittest.main()