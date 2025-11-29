import unittest
from queue import Queue
from src.shared_state import SharedState
from src.workers import PortfolioConsumer
import threading
import time

class TestPortfolioConsumerMultiple(unittest.TestCase):
    def test_multiple_price_updates(self):
        shared = SharedState(
            portfolio={"AAPL": 2, "TSLA": 1},
            alerts={},
            symbols=["AAPL", "TSLA"]
        )

        work_q = Queue()
        log_q = Queue()
        stop_event = threading.Event()

        consumer = PortfolioConsumer(shared, work_q, log_q, stop_event)
        consumer.daemon = True
        consumer.start()

        work_q.put(("AAPL", 100))
        work_q.put(("TSLA", 300))

        time.sleep(0.3)
        stop_event.set()

        with shared.lock:
            self.assertEqual(shared.prices["AAPL"], 100)
            self.assertEqual(shared.prices["TSLA"], 300)
            self.assertEqual(shared.portfolio_value, 2*100 + 300)  
