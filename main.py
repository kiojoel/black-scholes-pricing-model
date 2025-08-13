import pandas as pd
from datetime import datetime
from pricer import BlackScholesPricer
from database import get_all_options


# Hard-coded Market Data
MARKET_DATA = {
    'AAPL': {'price': 171.50, 'volatility': 0.22},
    'GOOG': {'price': 139.75, 'volatility': 0.28},
}
RISK_FREE_RATE = 0.05


def calculate_time_to_expiration(exp_date_str):
  exp_date = datetime.strptime(exp_date_str, '%Y-%m-%d')
  today = datetime.now()

  time_delta = exp_date - today

  return max(time_delta.days / 365.25, 1e-12)


def main():
  print("Fetching options from the database...")
  options_to_price = get_all_options()

  if not options_to_price:
      print("No options in Database.")
      return

  results = []

  for option in options_to_price:
      ticker = option['ticker']

      # Check if we have market data for this ticker
      if ticker not in MARKET_DATA:
          print(f"Warning: Market data for {ticker} not found. Skipping.")
          continue

      S = MARKET_DATA[ticker]['price']
      sigma = MARKET_DATA[ticker]['volatility']
      K = option['strike_price']
      option_type = option['option_type']
      T = calculate_time_to_expiration(option['expiration_date'])


      pricer_instance = BlackScholesPricer(S,K,T,RISK_FREE_RATE,sigma,option_type=option_type)

      calculated_price = pricer_instance.price()
      calculated_greeks = pricer_instance.get_all_greeks()

      result_row = {
            'Ticker': ticker,
            'Type': option_type.capitalize(),
            'Strike': K,
            'Expiration': option['expiration_date'],
            'Price': round(calculated_price, 2),
            'Delta': round(calculated_greeks['delta'], 4),
            'Gamma': round(calculated_greeks['gamma'], 4),
            'Vega': round(calculated_greeks['vega'] / 100, 4),
            'Theta': round(calculated_greeks['theta'] / 365, 4),
            'Rho': round(calculated_greeks['rho'] / 100, 4),
        }
      results.append(result_row)


  if results:
     df = pd.DataFrame(results)
     print("\nBlack-Scholes Pricing & Greeks Results")
     print(df.to_string())

if __name__ == '__main__':
    main()
