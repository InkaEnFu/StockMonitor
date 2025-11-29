import unittest
from queue import Queue
from src.shared_state import SharedState
from src.workers import PriceProducer
import threading
import time

class TestPriceProducer(unittest.TestCase):
    def test_producer_logs_error_if_no_symbols(self):
        shared = SharedState(portfolio={}, alerts={}, symbols=[])

        work_q = Queue()
        log_q = Queue()
        stop_event = threading.Event()

        prod = PriceProducer(shared, work_q, log_q, stop_event)
        prod.daemon = True
        prod.start()

        time.sleep(0.3)
        stop_event.set()

        msg = log_q.get(timeout=0.5)
        self.assertIn("Producer ERROR: No symbols defined.", msg)
