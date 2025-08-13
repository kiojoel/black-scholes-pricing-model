import numpy as np
from scipy.stats import norm


class BlackScholesPricer:
  def __init__(self, S, K, T, r, sigma, option_type = 'call'):
    self.S = S
    self.K = K
    self.T = T
    self.r = r
    self.sigma = sigma
    self.option_type = option_type.lower()

    self._calculate_d1_d2()

  def _calculate_d1_d2(self):
    self.d1 = (np.log(self.S / self.K) + (self.r + self.sigma**2 / 2) * self.T) / (self.sigma * np.sqrt(self.T))
    self.d2 = self.d1 - (self.sigma * np.sqrt(self.T))

  def price(self):
    if self.option_type == 'call':
      price = self.S * norm.cdf(self.d1) - self.K * np.exp(-self.r * self.T) * norm.cdf(self.d2)

    elif self.option_type == 'put':
      price = self.K * np.exp(-self.r * self.T) * norm.cdf(-self.d2) - self.S * norm.cdf(-self.d1)

    else:
      raise ValueError("Option type must be 'call or 'put'.")

    return price



if __name__ == '__main__':
    # Test a Call Option
    # Inputs: Stock Price=100, Strike=105, Time=1 year, Rate=5%, Volatility=20%
    call_pricer = BlackScholesPricer(S=100, K=105, T=1, r=0.05, sigma=0.20, option_type='call')
    call_price = call_pricer.price()
    print(f"Call Option Price: {call_price:.2f}")

    # Test a Put Option (with the same inputs)
    put_pricer = BlackScholesPricer(S=100, K=105, T=1, r=0.05, sigma=0.20, option_type='put')
    put_price = put_pricer.price()
    print(f"Put Option Price: {put_price:.2f}")