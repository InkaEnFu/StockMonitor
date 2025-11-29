import unittest
from queue import Queue
from src.shared_state import SharedState
from src.workers import AlertConsumer
import threading
import time

class TestAlertConsumer(unittest.TestCase):
    def test_alert_triggered_when_price_exceeds_limit(self):
        shared = SharedState(
            portfolio={}, 
            alerts={"AAPL": 150}, 
            symbols=[]
        )

        shared.prices["AAPL"] = 160  

        log_q = Queue()
        stop_event = threading.Event()

        worker = AlertConsumer(shared, log_q, stop_event)
        worker.daemon = True
        worker.start()

        time.sleep(0.2)
        stop_event.set()

        msg = log_q.get(timeout=0.5)
        self.assertIn("ALERT: AAPL exceeded limit 150", msg)
