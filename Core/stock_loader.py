"""
=========================================
BursaAI Stock Loader
Version : 3.0 Stable
=========================================
"""

import os

import pandas as pd


def load_stock_list():

    filepath = "data/stocks.csv"

    if not os.path.exists(filepath):

        raise FileNotFoundError(

            f"Fail tidak dijumpai : {filepath}"

        )

    df = pd.read_csv(filepath)

    if "Code" not in df.columns:

        raise ValueError(

            "Column 'Code' tidak dijumpai."

        )

    df = df.dropna(subset=["Code"])

    df["Code"] = df["Code"].astype(str).str.strip().str.upper()

    df = df[df["Code"] != ""]

    stocks = df["Code"].drop_duplicates().tolist()

    return stocks
