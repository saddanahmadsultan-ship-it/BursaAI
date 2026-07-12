def pre_filter(data):
    """
    Menapis saham sebelum diproses bagi
    menjimatkan masa scan.
    """

    if data.empty:
        return False

    last = data.iloc[-1]

    # Pastikan MA200 sudah cukup data
    if data["MA200"].isna().iloc[-1]:
        return False

    # Elakkan saham terlalu murah
    if float(last["Close"]) < 0.20:
        return False

    # Elakkan volume terlalu rendah
    if float(last["Volume"]) < 100000:
        return False

    return True