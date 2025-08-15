import numpy as np
from scipy.stats import norm


class BlackScholesPricer:
  def __init__(self, S, K, T, r, sigma, option_type = 'call'):
    if S <= 0:
        raise ValueError("Stock price must be positive")
    if K <= 0:
        raise ValueError("Strike price must be positive")
    if T <= 0:
        raise ValueError("Time to expiration must be positive")
    if sigma <= 0:
        raise ValueError("Volatility must be positive")
    self.S = S
    self.K = K
    self.T = T
    self.r = r
    self.sigma = sigma
    self.option_type = option_type.lower()

    self._calculate_all_values()

  def _calculate_all_values(self):
    self._calculate_d1_d2()
    self.n_d1 = norm.cdf(self.d1)
    self.n_d2 = norm.cdf(self.d2)
    self.n_neg_d1 = norm.cdf(-self.d1)
    self.n_neg_d2 = norm.cdf(-self.d2)
    self.pdf_d1 = norm.pdf(self.d1)

  def _calculate_d1_d2(self):
    T_safe = max(self.T, 1e-8)
    sqrt_T = np.sqrt(T_safe)

    self.d1 = (np.log(self.S / self.K) + (self.r + self.sigma**2 / 2) * T_safe) / (self.sigma * sqrt_T)
    self.d2 = self.d1 - (self.sigma * sqrt_T)

  def price(self):
    if self.option_type == 'call':
      price = self.S * self.n_d1 - self.K * np.exp(-self.r * self.T) * self.n_d2
    elif self.option_type == 'put':
      price = self.K * np.exp(-self.r * self.T) * self.n_neg_d2 - self.S * self.n_neg_d1
    else:
      raise ValueError("Option type must be 'call or 'put'.")

    return price

  def delta(self):
    if self.option_type == 'call':
      delta = self.n_d1
    elif self.option_type == 'put':
      delta = self.n_d1 - 1
    else:
      raise ValueError("Option type must be 'call or 'put'.")

    return delta

  def gamma(self):
    gamma = self.pdf_d1 / (self.S * self.sigma * np.sqrt(self.T))

    return gamma

  def vega(self):
    vega = self.S * self.pdf_d1 * np.sqrt(self.T)

    return vega

  def theta(self):
    const = (-self.S * self.pdf_d1 * self.sigma / (2 * np.sqrt(self.T)))
    if self.option_type == 'call':
      theta = const - self.r * self.K * np.exp(-self.r * self.T) * self.n_d2
    elif self.option_type == 'put':
      theta = const + self.r * self.K * np.exp(-self.r * self.T) * self.n_neg_d2
    else:
      raise ValueError("Option type must be 'call or 'put'.")

    return theta


  def rho(self):
    if self.option_type == 'call':
      rho = self.K * self.T * np.exp(-self.r * self.T) * self.n_d2
    elif self.option_type == 'put':
      rho = -self.K * self.T * np.exp(-self.r * self.T) * self.n_neg_d1
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




""" if __name__ == '__main__':
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
            print(f"  {greek.capitalize()}: {value:.4f}") """