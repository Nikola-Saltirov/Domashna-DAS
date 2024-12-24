import time

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import datetime

import ta
from tabulate import tabulate
import warnings
from ta.trend import WMAIndicator
import ta.volume
import ta.momentum
import io


warnings.filterwarnings('ignore')


def calculate_vwma(df, window):
    price_volume = df['avg_price'] * df['volume']
    volume_sum = df['volume'].rolling(window=window).sum()
    vwma = price_volume.rolling(window=window).sum() / volume_sum
    return vwma

def MovingAverageCrossStrategy(tiker='ADIN', start_date=datetime.date.today(), end_date=datetime.date.today(),
                               short_window=20, long_window=50, moving_avg='SMA'):
    stock_symbol = f"temp_stocks/temp_data/{tiker}.csv"
    stock_df = pd.read_csv(stock_symbol)
    stock_df['max'] = [
        ''.join([c if c not in '.,' else ',' if c == '.' else '.' for c in str(num)])
        if pd.notnull(num) else ''
        for num in stock_df['max']
    ]

    stock_df['min'] = [
        ''.join([c if c not in '.,' else ',' if c == '.' else '.' for c in str(num)])
        if pd.notnull(num) else ''
        for num in stock_df['min']
    ]
    stock_df['min'] = stock_df['min'].str.replace(',', '')
    stock_df['min'] = stock_df['min'].astype(float)
    stock_df['max'] = stock_df['max'].str.replace(',', '').astype(float)
    stock_df['max'] = pd.to_numeric(stock_df['max'], errors='coerce')
    stock_df['min'] = pd.to_numeric(stock_df['min'], errors='coerce')
    stock_df['avg_price'] = [
        ''.join([c if c not in '.,' else ',' if c == '.' else '.' for c in str(num)])
        if pd.notnull(num) else ''  # Handle NaN or missing values
        for num in stock_df['avg_price']
    ]
    stock_df['avg_price'] = stock_df['avg_price'].str.replace(',', '').astype(float)
    stock_df['volume'] = stock_df['volume'].astype(float)
    stock_df['Date'] = pd.to_datetime(stock_df['Date'], dayfirst=True)
    stock_df.set_index('Date', inplace=True)
    stock_df = stock_df.loc[start_date:end_date]
    short_window_col = str(short_window) + '_' + moving_avg
    long_window_col = str(long_window) + '_' + moving_avg

    if moving_avg == 'SMA':
        stock_df[short_window_col] = stock_df['avg_price'].rolling(window=short_window, min_periods=1).mean()
        stock_df[long_window_col] = stock_df['avg_price'].rolling(window=long_window, min_periods=1).mean()

    elif moving_avg == 'EMA':
        stock_df[short_window_col] = stock_df['avg_price'].ewm(span=short_window, adjust=False).mean()
        stock_df[long_window_col] = stock_df['avg_price'].ewm(span=long_window, adjust=False).mean()
    elif moving_avg == 'WMA':
        wma_indicator = WMAIndicator(close=stock_df['avg_price'], window=short_window)
        stock_df[short_window_col] = wma_indicator.wma()
        wma_indicator = WMAIndicator(close=stock_df['avg_price'], window=long_window)
        stock_df[long_window_col] = wma_indicator.wma()
    elif moving_avg == 'SMMA':
        stock_df[short_window_col] = ta.trend.sma_indicator(stock_df['avg_price'], window=short_window)
        stock_df[long_window_col] = ta.trend.sma_indicator(stock_df['avg_price'], window=long_window)
    elif moving_avg == 'VWMA':
        stock_df[short_window_col] = calculate_vwma(stock_df,short_window)
        stock_df[long_window_col] = calculate_vwma(stock_df,long_window)

    stock_df['Signal'] = 0.0
    stock_df['Signal'] = np.where(stock_df[short_window_col] > stock_df[long_window_col], 1.0, 0.0)

    stock_df['Position'] = stock_df['Signal'].diff()

    plt.figure(figsize=(20, 10))
    plt.tick_params(axis='both', labelsize=14)
    stock_df['avg_price'].plot(color='k', lw=1, label='avg_price')
    stock_df[short_window_col].plot(color='b', lw=1, label=short_window_col)
    stock_df[long_window_col].plot(color='g', lw=1, label=long_window_col)
    plt.plot(stock_df[stock_df['Position'] == 1].index,
             stock_df[short_window_col][stock_df['Position'] == 1],
             '^', markersize=15, color='g', alpha=0.7, label='buy')
    plt.plot(stock_df[stock_df['Position'] == -1].index,
             stock_df[short_window_col][stock_df['Position'] == -1],
             'v', markersize=15, color='r', alpha=0.7, label='sell')
    plt.ylabel('Price in MKD', fontsize=16)
    plt.xlabel('Data', fontsize=16)
    plt.title(str(stock_symbol) + ' - ' + str(moving_avg) + ' Crossover', fontsize=20)
    plt.legend()
    plt.grid()
    img_io = io.BytesIO()
    plt.savefig(img_io, format='png')
    img_io.seek(0)
    plt.close()

    return img_io