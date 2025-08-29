import sqlite3

DB_NAME = 'options.db'


def setup_database():
  conn = sqlite3.connect(DB_NAME)

  try:
    cursor = conn.cursor()

    cursor.execute("""
CREATE TABLE IF NOT EXISTS options_data(
                   id INTEGER PRIMARY KEY AUTOINCREMENT,
                   ticker TEXT NOT NULL,
                   option_type TEXT NOT NULL,
                   strike_price REAL,
                   expiration_date TEXT NOT NULL
                   );
""")


    cursor.execute("""
          CREATE TABLE IF NOT EXISTS calculated_prices (
              id INTEGER PRIMARY KEY AUTOINCREMENT,
              option_id INTEGER NOT NULL,
              calculation_timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
              theoretical_price REAL NOT NULL,
              underlying_price REAL NOT NULL,
              delta REAL,
              gamma REAL,
              vega REAL,
              theta REAL,
              rho REAL,
              FOREIGN KEY (option_id) REFERENCES options_data (id)
          );
      """)
    cursor.execute("""
            CREATE TABLE IF NOT EXISTS portfolios (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL UNIQUE,
                description TEXT
            );
        """)

    cursor.execute("""
          CREATE TABLE IF NOT EXISTS positions (
              id INTEGER PRIMARY KEY AUTOINCREMENT,
              portfolio_id INTEGER NOT NULL,
              ticker TEXT NOT NULL,
              quantity INTEGER NOT NULL, -- Positive for long, negative for short
              asset_type TEXT CHECK(asset_type IN ('call', 'put', 'stock')) NOT NULL,
              strike_price REAL, -- Can be NULL for stocks
              expiration_date TEXT, -- Can be NULL for stocks
              FOREIGN KEY (portfolio_id) REFERENCES portfolios(id)
          );
      """)

    cursor.execute("INSERT OR IGNORE INTO portfolios (id, name, description) VALUES (?, ?, ?)",
                       (1, 'My First Portfolio', 'A default portfolio for tracking positions.'))

    conn.commit()
    print("Database setup complete. Table 'options_data' is ready.")


  except sqlite3.Error as e:
    print(f"Error creating table: {e}")

  finally:
    if conn:
      conn.close()



def add_option(ticker, option_type, strike_price, expiration_date):
  conn = sqlite3.connect(DB_NAME)

  sql = ''' INSERT INTO options_data(ticker, option_type, strike_price, expiration_date) VALUES(?,?,?,?) '''

  try:
    cursor = conn.cursor()
    cursor.execute(sql,(ticker, option_type, strike_price, expiration_date))
    conn.commit()
    print(f"Added option: {ticker} {strike_price} {option_type}")
  except sqlite3.Error as e:
      print(f"Error adding option: {e}")
  finally:
      if conn:
          conn.close()

def get_all_options():
   conn = sqlite3.connect(DB_NAME)

   try:
      conn.row_factory = sqlite3.Row
      cursor = conn.cursor()

      cursor.execute(''' SELECT * FROM options_data ''')

      rows = cursor.fetchall()

      return [dict(row) for row in rows]
   except sqlite3.Error as e:
        print(f"Error fetching options: {e}")
        return []
   finally:
        if conn:
            conn.close()


def save_calculation_result(option_id, price, S, greeks):
    """Saves a single calculation result to the database."""
    conn = sqlite3.connect(DB_NAME)
    sql = ''' INSERT INTO calculated_prices(option_id, theoretical_price, underlying_price, delta, gamma, vega, theta, rho)
              VALUES(?,?,?,?,?,?,?,?) '''
    try:
        cursor = conn.cursor()
        cursor.execute(sql, (
            option_id,
            price,
            S,
            greeks['delta'],
            greeks['gamma'],
            greeks['vega'],
            greeks['theta'],
            greeks['rho']
        ))
        conn.commit()
    except sqlite3.Error as e:
        print(f"Error saving calculation: {e}")
    finally:
        if conn:
            conn.close()


def get_portfolios():
    """Queries all portfolios from the database."""
    conn = sqlite3.connect(DB_NAME)
    try:
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM portfolios ORDER BY name")
        rows = cursor.fetchall()
        return [dict(row) for row in rows]
    except sqlite3.Error as e:
        print(f"Error fetching portfolios: {e}")
        return []
    finally:
        if conn:
            conn.close()

def create_portfolio(name, description=""):
    """Creates a new portfolio in the database."""
    conn = sqlite3.connect(DB_NAME)
    sql = ''' INSERT INTO portfolios(name, description) VALUES(?,?) '''
    try:
        cursor = conn.cursor()
        cursor.execute(sql, (name, description))
        conn.commit()
        print(f"Created portfolio: {name}")
        return cursor.lastrowid
    except sqlite3.Error as e:
        print(f"Error creating portfolio: {e}")
        return None
    finally:
        if conn:
            conn.close()

def add_position(portfolio_id, ticker, quantity, asset_type, strike_price=None, expiration_date=None):
    """Adds a new position to a specific portfolio."""
    conn = sqlite3.connect(DB_NAME)
    sql = ''' INSERT INTO positions(portfolio_id, ticker, quantity, asset_type, strike_price, expiration_date)
              VALUES(?,?,?,?,?,?) '''
    try:
        cursor = conn.cursor()
        cursor.execute(sql, (portfolio_id, ticker, quantity, asset_type, strike_price, expiration_date))
        conn.commit()
        print(f"Added {quantity} {ticker} {asset_type} to portfolio ID {portfolio_id}")
        return cursor.lastrowid
    except sqlite3.Error as e:
        print(f"Error adding position: {e}")
        return None
    finally:
        if conn:
            conn.close()

def get_positions_for_portfolio(portfolio_id):
    """Queries all positions for a given portfolio_id."""
    conn = sqlite3.connect(DB_NAME)
    try:
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM positions WHERE portfolio_id = ? ORDER BY ticker", (portfolio_id,))
        rows = cursor.fetchall()
        return [dict(row) for row in rows]
    except sqlite3.Error as e:
        print(f"Error fetching positions: {e}")
        return []
    finally:
        if conn:
            conn.close()


if __name__ == '__main__':
    import os
    if os.path.exists(DB_NAME):
        os.remove(DB_NAME)
        print(f"Removed old {DB_NAME} for a fresh start.")

    setup_database()

    create_portfolio("My Options Plays", "A portfolio for speculative call and put options.")
    create_portfolio("Long Term Holdings")

    print("\n--- Current Portfolios in Database ---")
    portfolios = get_portfolios()
    for p in portfolios:
        print(p)

    # Find the ID of our default portfolio by looping and checking the name
    default_portfolio_id = None
    for p in portfolios:
        if p['name'] == 'My First Portfolio':
            default_portfolio_id = p['id']
            break

    # Proceed only if we successfully found the portfolio
    if default_portfolio_id is not None:
        print(f"\n--- Adding positions to portfolio: 'My First Portfolio' (ID: {default_portfolio_id}) ---")

        add_position(default_portfolio_id, 'NVDA', 100, 'stock')
        add_position(default_portfolio_id, 'TSLA', 500, 'call', strike_price=350.0, expiration_date='2026-03-20')
        add_position(default_portfolio_id, 'AAPL', -1000, 'put', strike_price=180.0, expiration_date='2026-06-19')

        print(f"\n--- Verifying positions in portfolio ID: {default_portfolio_id} ---")
        positions = get_positions_for_portfolio(default_portfolio_id)
        for pos in positions:
            print(pos)
    else:
        print("\nCould not find the 'My First Portfolio' to add positions to.")