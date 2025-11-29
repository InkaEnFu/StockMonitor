import threading
import time
import queue
import yfinance as yf
from src.shared_state import SharedState

class LoggerThread(threading.Thread):
    def __init__(self, log_queue, stop_event):
        super().__init__(daemon=True)
        self.log_queue = log_queue
        self.stop_event = stop_event

    def run(self):
        while not self.stop_event.is_set():
            try:
                msg = self.log_queue.get(timeout=1)
                print("[LOG]", msg)
            except queue.Empty:
                continue


class PriceProducer(threading.Thread):
    def __init__(self, shared_state, work_queue, log_queue, stop_event):
        super().__init__(daemon=True)
        self.shared = shared_state
        self.work_queue = work_queue
        self.log_queue = log_queue
        self.stop_event = stop_event

    def run(self):
        while not self.stop_event.is_set():
            try:
                symbols = self.shared.symbols 
                if not symbols:
                    self.log_queue.put("Producer ERROR: No symbols defined.")
                    time.sleep(5)
                    continue
                
                data = yf.download(
                    tickers=" ".join(symbols),
                    period="1d",
                    interval="1m",
                    progress=False,
                    auto_adjust=False
                )

                last_row = data.tail(1)

                for symbol in symbols:
                    price = float(last_row["Close"][symbol].iloc[0])
                    self.work_queue.put((symbol, price))
                    self.log_queue.put(f"[API] {symbol} = {price}")

            except Exception as e:
                self.log_queue.put(f"yfinance ERROR: {e}")

            time.sleep(2)


class PortfolioConsumer(threading.Thread):
    def __init__(self, shared_state, work_queue, log_queue, stop_event):
        super().__init__(daemon=True)
        self.shared = shared_state
        self.work_queue = work_queue
        self.log_queue = log_queue
        self.stop_event = stop_event

    def run(self):
        while not self.stop_event.is_set():
            symbol, price = self.work_queue.get()
            with self.shared.lock:
                self.shared.prices[symbol] = price
                total = 0
                for stock, shares in self.shared.portfolio.items():
                    if stock in self.shared.prices:
                        total += self.shared.prices[stock] * shares
                self.shared.portfolio_value = round(total, 2)

            self.log_queue.put(
                f"Portfolio update: {symbol}={price}, total value = {self.shared.portfolio_value}"
            )
            self.work_queue.task_done()


class AlertConsumer(threading.Thread):
    def __init__(self, shared_state, log_queue, stop_event):
        super().__init__(daemon=True)
        self.shared = shared_state
        self.log_queue = log_queue
        self.stop_event = stop_event

    def run(self):
        while not self.stop_event.is_set():
            with self.shared.lock:
                for symbol, limit in self.shared.alerts.items():
                    if symbol in self.shared.prices:
                        price = self.shared.prices[symbol]
                        if price > limit:
                            self.log_queue.put(
                                f"ALERT: {symbol} exceeded limit {limit}! Current price ={price}"
                            )
            time.sleep(1)