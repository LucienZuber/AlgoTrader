def spotRsiExceed(current_rsi):
    if current_rsi > 70:
        # The market may be overbought, it may become bearish
        return -1

    elif current_rsi < 30:
        # the market may be ouversold, it may become bullish
        return 1

    return 0
