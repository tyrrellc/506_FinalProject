import unittest
from SI507F17_finalproject import *



class Cache(unittest.TestCase):
    def setUp(self):
        self.cacheFile = open("dailyData.json")

    def test_files_exist(self):
        self.assertTrue(self.cacheFile.read())

    def tearDown(self):
        self.cacheFile.close()


class ApiPull(unittest.TestCase):
    def setUp(self):
        self.apple = TimeSeriesDaily('aapl')
        self.error = TimeSeriesDaily('')

    def test_data(self):
        self.assertEqual(type(self.apple), type({}))
        response = {
    "Error Message": "Invalid API call. Please retry or visit the documentation (https://www.alphavantage.co/documentation/) for TIME_SERIES_DAILY."
}
        self.assertEqual(self.error, response)


class Scrape(unittest.TestCase):
    def setUp(self):
        self.current, self.change, self.percent = scrape_control

    def test_types(self):
        self.assertEqual(type(self.current), float)
        self.assertEqual(type(self.change), float)
        self.assertEqual(type(self.percent), float)

    def test_percent(self):
        self.assertTrue(self.percent > 0)


class DBdataPrep(unittest.TestCase):
    def setUp(self):
        dict = {'11/16/17': [['10YR', '2.42', '2.30'], ['S&P', '2,559', '2,600'], ['RUT', '1,458', '1,500'], ['COMPQ', '6,673', '6,803']]}

        self.db = writeToDB(dict, 'rr')

    def test_data(self):
        self.assertEqual(tempDict, {'Date': '11/16/17','CommonDate': '171116', 'rrHigh': '6,803', 'rrLow':'6,673'})




if __name__ == '__main__':
    unittest.main(verbosity=2)
