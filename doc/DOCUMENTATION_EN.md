Project Name:
Multithread Financial Monitor with Real-Time API

Author:
Matyáš Prokop

Contact:
inkaenfu69@gmail.com

School:
SPŠE Ječná

Date of Completion:
23 November 2025

Note:
This document is part of a school project.

**1. Purpose of the Application and User Requirements**

The application solves a real-world problem of parallel data processing:
monitoring live stock prices, calculating the portfolio value, and evaluating alerts in real time.

**Business Requirements (BR)**

BR1: The user must be able to automatically track the current value of their portfolio without manually updating prices.

BR2: The user must be immediately notified when important price levels are exceeded, allowing timely reactions.

BR3: The application must run in parallel — it must be able to fetch data, process it, check alerts, and log activity simultaneously without blocking.

BR4: Shared data must be safely accessible by multiple threads without the risk of corruption or inconsistency.

BR5: The application must minimize human error by fully automating monitoring, calculations, and notifications.

BR6: The system must run continuously and react in real time to market price changes.

BR7: The application must be realistically usable as part of an investment monitoring system and must not be just a simulation.

**Functional Requirements (FR)**

FR1: The application must periodically download real stock prices for selected stock
FR2: The application must store current prices in shared state.
FR3: The application must calculate the real-time portfolio value.
FR4: The application must evaluate alerts (price > limit).
FR5: The application must log all events.
FR6: The program must run multithreaded and must not block the main thread.
FR7: The program must continue running until the user terminates it.

**Non-Functional Requirements (NFR)**

NFR1: API requests must be stable and must not block threads (timeout, error handling).
NFR2: Synchronization of shared data must be safe (thread-safe).
NFR3: The system must be resilient to API failures.
NFR4: Logging must not block the main execution flow.
NFR5: The program must be easily configurable.

**2. Application Architecture**

The application is based on a producer–consumer architecture with multiple consumers and a single logger.

                ┌───────────────────────┐
                │    PriceProducer      │
                │  (yfinance API fetch) │
                └──────────┬────────────┘
                              │
                              ▼
                        work_queue
                              │
            ┌───────────────────┴─────────────────────┐
            │                                         │
            ▼                                         ▼
      PortfolioConsumer                        AlertConsumer
      (calculates value)                      (monitors limits)
            │                                         │
            └───────────────────┬─────────────────────┘
                              ▼
                        log_queue
                              │
                              ▼
                        LoggerThread

**3. Class Descriptions (Text-Based Class Diagram)**
**SharedState**

prices: dict[str, float]

portfolio: dict[str, int]

alerts: dict[str, float]

lock: threading.Lock

**LoggerThread**

Reads messages from log_queue and prints them (non-blocking for the main flow).

**PriceProducer**

Periodically (configurable, default every 2 seconds) downloads stock prices via yfinance and inserts them into work_queue.

**PortfolioConsumer**

Processes prices from the work queue, locks shared state during updates, recalculates portfolio value, and sends messages to log_queue.

**AlertConsumer**

Periodically reads shared state under a lock, checks defined alert limits, and sends alerts to log_queue when exceeded.

**4. Behavioral Model (Activity Diagram – Text Form)**
**PriceProducer**

Wait according to interval (default 2s)

Call yfinance API (with timeout and error handling)

Fetch stock prices

For each symbol, insert price into work_queue

Send informational entry to log_queue

Repeat

**PortfolioConsumer**

Wait for a new item from work_queue

Lock SharedState

Update price in prices

Recalculate portfolio value

Unlock

Send output to log_queue

Repeat

**AlertConsumer**

Lock SharedState

For each symbol, compare value against alerts

If price > limit → send alert to log_queue

Unlock

Wait a short interval (e.g., 1s)

Repeat

**LoggerThread**

Wait for a message in log_queue

Print it (stdout or file) asynchronously

Repeat

**5. Libraries and Interfaces Used**
Python Standard Library

threading

queue

time

Third-Party Libraries

yfinance — wrapper for Yahoo Finance API

API Services

Yahoo Finance (via yfinance)

**6. Licensing Aspects**

yfinance: Apache 2.0 License

Yahoo Finance data is publicly accessible; recommended for non-commercial and educational use according to service terms

Project: school assignment

**7. Application Configuration**

Default configuration in PriceProducer:

interval = 2s (configurable)
period = 1d (when using historical data)


The user may modify:

portfolio

alert limits

tracked stocks

data refresh frequency

**8. Testing and Validation**

Performed tests:

Test 1: API access — yfinance returns data; on failure, an error is logged and service continues.

Test 2: Shared state synchronization — verified no race conditions when using threading.Lock.

Test 3: Alerts — alerts are generated when limits are exceeded.

Test 4: Thread termination — application responds to Ctrl+C/SIGINT and safely stops daemon threads.

**9. Version List and Known Bugs**

Version 1.0 — 23 November 2025
First version of the project; meets assignment requirements.

Known bugs:

occasional API outages (network issues) — handled with retry/backoff

API may return NaN values — handled in code (ignored/not overwriting values)

**10. Installation and Running the Application**

Requirements:

Python 3.10+

Installation:

pip install -r requirements.txt

Fill your portfolio with stocks and its values, set alerts and symbols:

self.portfolio = {} -> self.portfolio = {"AAPL": 10, "TSLA": 5}
self.alerts = {} -> self.alerts = {"AAPL": 150, "TSLA": 180}
self.symbols = [] -> self.symbols = ["AAPL", "TSLA"]

Run:

python Stock.py or py Stock.py
