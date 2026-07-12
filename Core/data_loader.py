"""
=========================================
BursaAI Data Loader
Version : 3.0 Stable
=========================================
"""

import yfinance as yf


REQUIRED_COLUMNS = ["Open", "High", "Low", "Close", "Volume"]


def load_stock(symbol):

    try:

        stock = yf.Ticker(symbol)

        data = stock.history(
            period="1y",
            auto_adjust=False
        )

        if data is None or data.empty:

            print(f"Tiada data untuk {symbol}")

            return None

        missing = [
            column for column in REQUIRED_COLUMNS
            if column not in data.columns
        ]

        if missing:

            print(
                f"Data {symbol} tidak lengkap: "
                f"{', '.join(missing)}"
            )

            return None

        data = data.sort_index()

        return data

    except Exception as e:

        print(f"Load Error [{symbol}] : {e}")

        return None
