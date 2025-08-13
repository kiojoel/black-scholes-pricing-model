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



if __name__ == '__main__':
  setup_database()

  print("\n--- Adding Sample Data ---")
  add_option('AAPL', 'call', 180.0, '2024-12-20')
  add_option('GOOG', 'put', 140.0, '2024-09-20')

  print("\n--- Current options in database ---")
  all_options = get_all_options()
  for option in all_options:
      print(option)