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

  def delta(self):
    if self.option_type == 'call':
      delta = norm.cdf(self.d1)
    elif self.option_type == 'put':
      delta = norm.cdf(self.d1) - 1
    else:
      raise ValueError("Option type must be 'call or 'put'.")

    return delta

  def gamma(self):
    gamma = norm.pdf(self.d1) / (self.S * self.sigma * np.sqrt(self.T))

    return gamma

  def vega(self):
    vega = self.S * norm.pdf(self.d1) * np.sqrt(self.T)

    return vega

  def theta(self):
    const = (-self.S * norm.pdf(self.d1) * self.sigma / (2 * np.sqrt(self.T)))
    if self.option_type == 'call':
      theta = const - self.r * self.K * np.exp(-self.r * self.T) * norm.cdf(self.d2)
    elif self.option_type == 'put':
      theta = const + self.r * self.K * np.exp(-self.r * self.T) * norm.cdf(-self.d2)
    else:
      raise ValueError("Option type must be 'call or 'put'.")

    return theta


  def rho(self):
    if self.option_type == 'call':
      rho = self.K * self.T * np.exp(-self.r * self.T) * norm.cdf(self.d2)
    elif self.option_type == 'put':
      rho = -self.K * self.T * np.exp(-self.r * self.T) * norm.cdf(-self.d2)
    else:
      raise ValueError("Option type must be 'call or 'put'.")

    return rho

  def get_all_greeks(self):
        """Return a dictionary of all Greeks."""
        return {
            'delta': self.delta(),
            'gamma': self.gamma(),
            'vega': self.vega(),
            'theta': self.theta(),
            'rho': self.rho()
        }




if __name__ == '__main__':
    # Test a Call Option
    # Inputs: Stock Price=100, Strike=105, Time=1 year, Rate=5%, Volatility=20%
    call_pricer = BlackScholesPricer(S=100, K=105, T=1, r=0.05, sigma=0.20, option_type='call')

    price = call_pricer.price()
    greeks = call_pricer.get_all_greeks()

    print("Call Option")
    print(f"Price: {price:.2f}")
    print("Greeks:")
    for greek, value in greeks.items():
        # Theta is often quoted per day, Vega per 1% change.
        if greek == 'theta':
            # The formula gives annual theta, so we divide by 365
            print(f"  {greek.capitalize()}: {value/365:.4f} (per day)")
        elif greek in ['vega', 'rho']:
            # The formula gives the change per 1.0 move
            # Divide by 100 to get the value per 1% change.
             print(f"  {greek.capitalize()}: {value/100:.4f} (per 1% change)")
        else:
            print(f"  {greek.capitalize()}: {value:.4f}")