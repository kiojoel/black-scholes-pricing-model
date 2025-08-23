import pandas as pd
from pricer import BlackScholesPricer

def scenario_analysis(pricer, stock_price_scenarios):
     """
    Calculates option price and P&L across a range of stock prices.

    Args:
        pricer: A configured BlackScholesPricer instance.
        stock_price_scenarios: A list of new stock prices to test.

    Returns:
        A pandas DataFrame with the analysis results.
    """
     results = []
     initial_price = pricer.price()

     for new_price in stock_price_scenarios:
        # A new pricer for the scenario with the new stock price
        scenario_pricer = BlackScholesPricer(
            S=new_price,
            K=pricer.K,
            T=pricer.T,
            r=pricer.r,
            sigma=pricer.sigma,
            option_type=pricer.option_type
        )

        scenario_option_price = scenario_pricer.price()
        pnl = scenario_option_price - initial_price

        results.append({
            'Stock Price': new_price,
            'Option Price': scenario_option_price,
            'P&L': pnl
        })

     return pd.DataFrame(results)


def implied_volatility(market_price, S, K, T, r, option_type, initial_guess=0.5, tolerance=1e-6, max_iterations=100):
    """
    Calculates the implied volatility of an option using the Newton-Raphson method.
    """

    sigma = initial_guess

    for i in range(max_iterations):
        pricer = BlackScholesPricer(S, K, T, r, sigma, option_type)
        price_diff = pricer.price() - market_price
        vega = pricer.vega()

        if abs(price_diff) < tolerance:
          return sigma

        if vega < 1e-8:
            break

        # The Newton-Raphson formula: New Guess = Old Guess - (Error / Derivative)
        sigma = sigma - (price_diff / vega)

    return sigma