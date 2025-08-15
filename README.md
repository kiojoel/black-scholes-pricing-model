# Black-Scholes Option Pricing & Greeks Calculator

[![Streamlit App](https://static.streamlit.io/badges/streamlit_badge_black_red.svg)](https://black-scholes-pricing-models.streamlit.app/)

An interactive and web application for pricing European options using the Black-Scholes model. The tool fetches live market data to calculate theoretical prices, all major Greeks, and provides key metrics for analysis.

**Live Application Link:** [https://black-scholes-pricing-models.streamlit.app/](https://black-scholes-pricing-models.streamlit.app/)

## Features

- **Interactive Pricer:** Input any stock ticker, strike price, and expiration date to get instant calculations.
- **Real-Time Market Data:** Automatically fetches the latest stock price, historical volatility, and risk-free rates from Yahoo Finance.
- **Comprehensive Greek Analysis:** Calculates Delta, Gamma, Vega, Theta, and Rho to provide a full risk profile of the option.
- **Rich UI & Data Visualization:** A clean, user-friendly interface built with Streamlit, providing key metrics like Time Value and Moneyness.
- **Backend Data Store:** All calculations performed by the batch pricer are saved to an SQLite database for potential historical analysis.

## Tech Stack

- **Backend:** Python
- **Frontend:** Streamlit
- **Data Manipulation:** Pandas, NumPy
- **Financial Math:** SciPy
- **Live Data API:** yfinance
- **Database:** SQLite

## How to Run Locally

1.  **Clone the repository:**

    ```bash
    git clone https://github.com/kiojoel/black-scholes-pricing-model.git
    cd black-scholes-pricing-model
    ```

2.  **Create and activate a virtual environment:**

    ```bash
    python -m venv venv
    source venv/bin/activate  # On Windows: venv\Scripts\activate
    ```

3.  **Install the required dependencies:**

    ```bash
    pip install -r requirements.txt
    ```

4.  **Run the Streamlit application:**
    ```bash
    streamlit run app.py
    ```
