import pandas as pd
import numpy as np
import yfinance as yf
from datetime import datetime
from pricer import BlackScholesPricer
from database import get_all_options, save_calculation_result, setup_database


def get_live_market_data(ticker_symbol):
  print(f"Fetching data for {ticker_symbol}...")
  ticker = yf.Ticker(ticker_symbol)

  # Get the most recent price
  hist = ticker.history(period="1d")
  if hist.empty:
      raise ValueError(f"Could not get price for {ticker_symbol}. Is the ticker correct?")
  current_price = hist['Close'].iloc[0]

  # Get historical data for the last year to calculate volatility
  hist_data = ticker.history(period="1y")

  # Calculate daily log returns
  log_returns = np.log(hist_data['Close'] / hist_data['Close'].shift(1))

  # Calculate annualized historical volatility

  # Multiplying daily std dev by sqrt of trading days (252)
  annualized_volatility = log_returns.std() * np.sqrt(252)

  print(f"  > Price: {current_price:.2f}, Volatility: {annualized_volatility:.4f}")

  return {
      'price': current_price,
      'volatility': annualized_volatility
  }



def calculate_time_to_expiration(exp_date_str):
  exp_date = datetime.strptime(exp_date_str, '%Y-%m-%d')
  today = datetime.now()

  time_delta = exp_date - today

  return max(time_delta.days / 365.25, 1e-12)



def main():
  setup_database()

  # Set a single risk-free rate for all calculations
  RISK_FREE_RATE = 0.05

  print("Fetching options from the database...")
  options_to_price = get_all_options()

  if not options_to_price:
      print("No options in Database.")
      return

  results = []

  for option in options_to_price:
      ticker = option['ticker']
      option_id = option['id']
      try:
            # Get live market data for the specific ticker
            market_data = get_live_market_data(ticker)
            S = market_data['price']
            sigma = market_data['volatility']
      except Exception as e:
          print(f"Could not process {ticker}. Error: {e}. Skipping.")
          continue

      K = option['strike_price']
      option_type = option['option_type']
      T = calculate_time_to_expiration(option['expiration_date'])

      pricer_instance = BlackScholesPricer(S, K, T, RISK_FREE_RATE, sigma, option_type)

      calculated_price = pricer_instance.price()
      calculated_greeks = pricer_instance.get_all_greeks()


      print(f"  > Saving results for {ticker} option ID {option_id}...")
      save_calculation_result(option_id, calculated_price, S, calculated_greeks)

      result_row = {
          'Ticker': ticker,
          'Type': option_type.capitalize(),
          'Strike': K,
          'Expiration': option['expiration_date'],
          'Live Price': round(S, 2),
          'Option Price': round(calculated_price, 2),
          'Delta': round(calculated_greeks['delta'], 4),
          'Gamma': round(calculated_greeks['gamma'], 4),
          'Vega': round(calculated_greeks['vega'] / 100, 4),
          'Theta': round(calculated_greeks['theta'] / 365, 4),
          'Rho': round(calculated_greeks['rho'] / 100, 4),
      }
      results.append(result_row)

  if results:
      df = pd.DataFrame(results)
      print("\nLive Black-Scholes Pricing & Greeks Results")
      print(df.to_string())


if __name__ == '__main__':
    main()
