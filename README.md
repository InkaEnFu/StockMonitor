Multithread Financial Monitor with Real-Time API

Author: Matyáš Prokop

Summary:
Monitors prices of selected stocks, calculates portfolio value, and sends alerts.

Requirements:

Python 3.10+

Installation:

pip install -r requirements.txt

Fill your portfolio with stocks and its values, set alerts and symbols in the main.py:

PORTFOLIO_CONFIG = {} -> PORTFOLIO_CONFIG = {"AAPL": 10, "TSLA": 5}

ALERT_CONFIG = {} -> ALERT_CONFIG = {"AAPL": 150, "TSLA": 180}

Run:

python main.py

Detailed documentation and specifications (BR/FR/NFR, tests) are available in the file DOCUMENTATION_EN.md.

