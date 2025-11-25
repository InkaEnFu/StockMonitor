import threading
import time
import queue
import yfinance as yf


class SharedState:
    def __init__(self):
        self.prices = {}
        self.portfolio = {}
        self.portfolio_value = 0.0
        self.alerts = {}
        self.lock = threading.Lock()


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
    def __init__(self, work_queue, log_queue, stop_event):
        super().__init__(daemon=True)
        self.work_queue = work_queue
        self.log_queue = log_queue
        self.stop_event = stop_event
        self.symbols = []

    def run(self):
        while not self.stop_event.is_set():
            try:
                data = yf.download(
                    tickers=" ".join(self.symbols),
                    period="1d",
                    interval="1m",
                    progress=False,
                    auto_adjust=False
                )

                last_row = data.tail(1)

                for symbol in self.symbols:
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


def main():
    stop_event = threading.Event()
    shared_state = SharedState()

    price_queue = queue.Queue()
    log_queue = queue.Queue()

    logger_thread = LoggerThread(log_queue, stop_event)
    producer = PriceProducer(price_queue, log_queue, stop_event)
    portfolio_consumer = PortfolioConsumer(shared_state, price_queue, log_queue, stop_event)
    alert_consumer = AlertConsumer(shared_state, log_queue, stop_event)

    logger_thread.start()
    producer.start()
    portfolio_consumer.start()
    alert_consumer.start()

    try:
        while True:
            time.sleep(3)
            with shared_state.lock:
                print("Prices:", shared_state.prices)
                print("Portfolio value:", shared_state.portfolio_value)
                print("---")
    except KeyboardInterrupt:
        stop_event.set()
        print("Stopping...")


if __name__ == "__main__":
    main()
