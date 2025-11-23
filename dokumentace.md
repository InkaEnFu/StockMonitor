Název projektu:
Multithread Finanční Monitor s Real-Time API

Autor:
Matyáš Prokop

Kontakt:
inkaenfu69@gmail.com

Škola:
SPŠE Ječná

Datum vypracování:
23. 11. 2025

Poznámka:
Tento dokument je součástí školního projektu.

**1. Účel aplikace a uživatelské požadavky**

Aplikace řeší reálný problém paralelního zpracování dat: monitorování živých cen akcií, výpočtu hodnoty portfolia a vyhodnocování alertů v reálném čase.

**Business Requirements (BR)**

BR1: Uživatel musí mít možnost automaticky sledovat aktuální hodnotu svého portfolia bez nutnosti manuální aktualizace cen.

BR2: Uživatel musí být okamžitě upozorněn při překročení důležitých cenových úrovní, aby mohl včas reagovat.

BR3: Aplikace musí pracovat paralelně — musí být schopna současně stahovat data, zpracovávat je, kontrolovat alerty a logovat průběh bez blokování.

BR4: Sdílená data musejí být bezpečně dostupná více vláknům bez rizika poškození nebo nekonzistence.

BR5: Aplikace musí minimalizovat lidskou chybu tím, že plně automatizuje monitoring, výpočty i upozornění.

BR6: Systém musí běžet nepřetržitě a reagovat v reálném čase na změny cen na trhu.

BR7: Aplikace musí být reálně použitelná jako součást investičního monitoringu a nesmí být pouze simulací.

**Functional Requirements (FR)**

FR1: Aplikace musí periodicky stahovat reálné ceny akcií AAPL a TSLA.

FR2: Aplikace musí ukládat aktuální ceny do sdíleného stavu.

FR3: Aplikace musí počítat aktuální hodnotu portfolia v reálném čase.

FR4: Aplikace musí vyhodnocovat alerty (cena > limit).

FR5: Aplikace musí zapisovat veškeré události do logu.

FR6: Program musí běžet vícevláknově a nesmí blokovat hlavní vlákno.

FR7: Program musí běžet, dokud jej uživatel neukončí.

**Non-Functional Requirements (NFR)**

NFR1: API požadavky musí být stabilní, nesmí blokovat vlákna (timeout, error handling).

NFR2: Synchronizace sdílených dat musí být bezpečná (thread-safe).
NFR3: Systém musí být odolný vůči selhání API.

NFR4: Logování nesmí blokovat hlavní běh aplikace.

NFR5: Program musí být snadno konfigurovatelný.

**2. Architektura aplikace**

      Aplikace je založena na producer–consumer architektuře s více konzumenty a jedním loggerem.

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
      (počítá hodnotu)                       (hlídá limity)
            │                                         │
            └───────────────────┬─────────────────────┘
                              ▼
                        log_queue
                              │
                              ▼
                        LoggerThread

**3. Popis tříd (Class Diagram – textová forma)**

**SharedState**

prices: dict[str, float]

portfolio: dict[str, int]

alerts: dict[str, float]

lock: threading.Lock

**LoggerThread**

Bere zprávy z log_queue a vypisuje je (nevytváří blokující I/O v hlavním běhu).

**PriceProducer**

Periodicky (konfigurovatelně, výchozí každé 2 s) stahuje ceny akcií přes yfinance a vkládá je do work_queue.

**PortfolioConsumer**

Zpracovává ceny z pracovní fronty, zamyká sdílený stav při aktualizaci, přepočítává hodnotu portfolia a posílá zprávy do log_queue.

AlertConsumer

Pravidelně čte sdílený stav pod zámkem, kontroluje definované limity v alerts a při překročení posílá alerty do log_queue.

**4. Behaviorální model (Activity Diagram – textová forma)**

**PriceProducer**

- Čekej dle intervalu (výchozí 2 s)
- Zavolej yfinance API (s timeoutem a ošetřením chyb)
- Získej ceny akcií
- Pro každý symbol vlož cenu do work_queue
- Poslat informační záznam do log_queue
- Repeat

**PortfolioConsumer**

- Čekej na nový prvek z work_queue
- Zamkni SharedState
- Aktualizuj cenu ve prices
- Přepočítej hodnotu portfolia
- Odemkni
- Pošli výstup do log_queue
- Repeat

**AlertConsumer**

- Zamkni SharedState
- Pro každý symbol zkontroluj hodnotu proti alerts
- Pokud cena > limit → pošli alert do log_queue
- Odemkni
- Čekej krátký interval (např. 1 s)
- Repeat

**LoggerThread**

- Čekej na zprávu ve log_queue
- Vypiš ji (stdout nebo soubor) asynchronně
- Repeat

**5. Použité knihovny a rozhraní**

Python standard library

- threading, queue, time

Third-party knihovny

- yfinance — wrapper pro Yahoo Finance API

API služby

- Yahoo Finance (přes yfinance)

**6. Licenční aspekty**

yfinance: Apache 2.0 License

Data z Yahoo Finance jsou veřejně dostupná, doporučeno používat je pro nekomerční a výukové účely podle podmínek služby.

Projekt: školní práce.

**7. Konfigurace aplikace**

Výchozí nastavení v SharedState:

portfolio = {"AAPL": 10, "TSLA": 5}
alerts = {"AAPL": 150, "TSLA": 180}

Výchozí nastavení PriceProducer:

self.symbols = ["AAPL", "TSLA"]
interval = 2s (konfigurovatelné)
period = 1d (pokud se používají historická data)

Uživatel může upravit:

- portfolio
- alert limity
- sledované akcie
- frekvenci obnovy dat

**8. Testování a validace**

Testy provedené:

- Test 1: Přístup k API — yfinance vrací data; při selhání se zapíše chyba do logu a služba pokračuje.
- Test 2: Synchronizace sdíleného stavu — testy ukazují žádné race conditions při použití threading.Lock.
- Test 3: Alerty — při překročení limitů se generují alerty.
- Test 4: Ukončení vláken — aplikace reaguje na Ctrl+C/SIGINT a ukončí daemon vlákna bezpečně.

**9. Seznam verzí a známé bugy**

Verze 1.0 — 23. 11. 2025

První verze projektu; splňuje požadavky zadání.

Známé bugy:

- občasné výpadky API (síťové problémy) — ošetřeny retry/backoff
- API může vracet NaN hodnoty — ošetřeno v kódu (ignorování/nepřepisování hodnot)

**10. Instalace a spuštění aplikace**

Požadavky:

- Python 3.10+

Instalace závislostí:

Terminál:
pip install -r requirements.txt


Spuštění aplikace:

python Stock.py