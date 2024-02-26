class StockInfo:
    def __init__(self, symbol, company, open, close, high, low, volume, last_updated, change_percent, change_diff):
        self.symbol = symbol
        self.company = company
        self.open = open
        self.close = close
        self.high = high
        self.low = low
        self.volume = volume
        self.last_updated = last_updated
        self.change_percentage = change_percent
        self.change_difference = change_diff
