def spotSarInversion(current_sar, current_data_close, previous_sar, previous_data_close):
    if((current_sar-current_data_close) * (previous_sar-previous_data_close) < 0):
        if current_sar-current_data_close > 0:
            # this means that the SAR is lower than the price, therefore the market may be bullish
            return 1
        else:
            # this means that the SAR is higher than the price, therefore the market may be bearish
            return -1
    return 0
