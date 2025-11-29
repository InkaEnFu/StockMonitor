import unittest
from src.shared_state import SharedState
from queue import Queue

class TestPortfolioConsumer(unittest.TestCase):
    def test_portfolio_value_updates_correctly(self):
        mock_portfolio = {"AAPL": 10, "TSLA": 5}
        shared_state = SharedState(mock_portfolio, {}, ["AAPL", "TSLA"])
        work_queue = Queue()

        work_queue.put(("AAPL", 150.00))
        work_queue.put(("TSLA", 200.00))


        symbol_1, price_1 = work_queue.get(timeout=0.1)
        with shared_state.lock:
            shared_state.prices[symbol_1] = price_1
            total = sum(shared_state.prices.get(stock, 0) * shares 
                        for stock, shares in shared_state.portfolio.items())
            shared_state.portfolio_value = round(total, 2)

        symbol_2, price_2 = work_queue.get(timeout=0.1)
        with shared_state.lock:
            shared_state.prices[symbol_2] = price_2
            total = sum(shared_state.prices.get(stock, 0) * shares 
                        for stock, shares in shared_state.portfolio.items())
            shared_state.portfolio_value = round(total, 2)

        self.assertEqual(shared_state.prices["AAPL"], 150.00)
        self.assertEqual(shared_state.prices["TSLA"], 200.00)
        self.assertEqual(shared_state.portfolio_value, 2500.00)
        self.assertTrue(work_queue.empty())