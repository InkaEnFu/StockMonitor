import threading

class SharedState:
    def __init__(self, portfolio, alerts, symbols):
        self.prices = {}
        self.portfolio = portfolio
        self.portfolio_value = 0.0
        self.alerts = alerts
        self.symbols = symbols
        self.lock = threading.Lock()