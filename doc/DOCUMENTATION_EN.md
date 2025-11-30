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

FR1: The application must periodically download real stock prices for all tickers entered by the user at startup.

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
                            │     user_input.py     │
                            │ (collects tickers,    │
                            │  shares, alerts,      │
                            │  validates symbols)   │
                            └──────────┬────────────┘
                                       │
                                       ▼
                                ┌──────────────────┐
                                │   TradeEngine    │
                                │ (initializes     │
                                │  threads + state)│
                                └─────────┬────────┘
                                          │
                                          ▼
                                    ┌────────────┐
                                    │SharedState │
                                    └─────┬──────┘
                                          │
                                          ▼
                                ┌──────────────────────┐
                                │    PriceProducer     │
                                │ (yfinance API fetch) │
                                └──────────┬───────────┘
                                           │
                                           ▼
                                        work_queue
                                            │
                    ┌───────────────────────┴────────────────────────┐
                    │                                                │
                    ▼                                                ▼
            ┌──────────────────┐                           ┌───────────────────┐
            │ PortfolioConsumer│                           │  AlertConsumer    │
            │ (calculates      │                           │ (monitors limits) │
            │  portfolio value)│                           └───────────────────┘
            └──────────┬───────┘
                       │
                       ▼
                   log_queue
                      │
                      ▼
                ┌────────────────┐
                │  LoggerThread  │
                └────────────────┘

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

**TradeEngine**

Coordinates the entire system, initializes all queues, threads, and shared state, and starts/stops the worker threads.

**User_input.py**

Handles user interaction before the engine starts.


**4. Behavioral Model (Activity Diagram – Text Form)**
**User Input Phase**

Before the threaded system starts, the application performs an interactive input phase:

Ask the user to enter stock tickers

Validate ticker existence

Ask for number of shares

Ask whether an alert should be set (y/n)

If yes, ask for the alert threshold

Build portfolio, alerts, and symbols

Pass all values into TradeEngine

**TradeEngine** 

The TradeEngine acts as the coordinator of the entire application:

Creates SharedState

Initializes internal queues (price_queue, log_queue)

Creates all worker threads:

LoggerThread

PriceProducer

PortfolioConsumer

AlertConsumer

Starts all threads in the correct order

Runs the monitoring loop (run_monitor), which periodically displays prices and portfolio value

Ensures the system remains active until termination

The TradeEngine does not process business logic itself — it orchestrates the worker threads that perform the work.

**PriceProducer**

Wait for a fixed interval (default 2 s)

Download the latest prices for all watched symbols

Insert each price into work_queue

Insert an informational message into log_queue

Repeat indefinitely

**PortfolioConsumer**

Wait for new data in work_queue

Acquire SharedState.lock

Update prices

Recalculate portfolio_value

Release lock

Log the updated value to log_queue

Repeat indefinitely

**AlertConsumer**

Acquire SharedState.lock

For each ticker with an alert, compare current price with threshold

If the threshold is exceeded, write an alert message to log_queue

Release lock

Sleep briefly (default 1 s)

Repeat indefinitely

**LoggerThread**

Wait for messages in log_queue

Print them asynchronously

Repeat indefinitely

**5. Libraries and Interfaces Used**
Python Standard Library

threading

queue

time

Third-Party Libraries

yfinance — wrapper for Yahoo Finance API

pytest - for testing project

API Services

Yahoo Finance (via yfinance)

**6. Licensing Aspects**

yfinance: Apache 2.0 License

Yahoo Finance data is publicly accessible; recommended for non-commercial and educational use according to service terms

Project: school assignment

**7. Application Configuration**

The application is configured dynamically through interactive console input before the monitoring engine starts. -> py main.py

**8. Testing and Validation**

Performed tests:

Test 1 – test_portfolio_value_update.py – Verifies portfolio recalculation

This test checks that after two manual price updates, the correct stock prices are stored and the final portfolio value is computed accurately.

Test 2 – test_alert_creation.py – Verifies alert generation

This test simulates a price that exceeds the alert threshold and checks that an alert message is correctly logged.

Test 3 – test_log_error.py – Verifies producer error handling

This test runs the PriceProducer without any symbols and verifies that it logs the expected “No symbols defined” error.

Test 4 – test_price_calculation.py – Verifies multi-price updates

This test ensures that the PortfolioConsumer correctly updates multiple stock prices and recalculates the portfolio value accordingly.

**9. Version List and Known Bugs**

Version 1.0 — 23 November 2025
First version of the project; meets assignment requirements.

Known bugs:

occasional API outages (network issues) — handled with retry/backoff

API may return NaN values — handled in code (ignored/not overwriting values)

Version 1.1 - 30 November 2025

Added interactive console input for portfolio and alert configuration, introduced ticker validation, and refactored architecture

Known bugs:

Negative user input for prices 


**10. Installation and Running the Application**

Requirements:

Python 3.10+

Install dependencies:

Terminal:

pip install -r requirements.txt


Run the application:

python Stock.py

Run the test:

$env:PYTHONPATH="."
pytest tests/