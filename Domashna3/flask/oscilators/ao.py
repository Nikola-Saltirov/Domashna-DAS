import time

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import datetime
import io

import ta
from tabulate import tabulate
import warnings
from ta.trend import WMAIndicator
import ta.volume


def calcAO(tiker, interval, start_date, end_date, short_window):
    data=pd.read_csv(f'temp_stocks/temp_data/{tiker}.csv')
    df = pd.DataFrame(data)
    df = df.tail(int(interval)+34)
    df.dropna(inplace=True)

    df['max'] = [
        ''.join([c if c not in '.,' else ',' if c == '.' else '.' for c in str(num)])
        if pd.notnull(num) else ''  # Handle NaN or missing values
        for num in df['max']
    ]
    # print(df['min'])
    df['min'] = [
        ''.join([c if c not in '.,' else ',' if c == '.' else '.' for c in str(num)])
        if pd.notnull(num) else ''  # Handle NaN or missing values
        for num in df['min']
    ]
    # print(df['min'])
    df['min'] = df['min'].str.replace(',', '').astype(float)
    df['max'] = df['max'].str.replace(',', '').astype(float)
    # Step 1: Calculate the Median Price
    df['max']=pd.to_numeric(df['max'],errors='coerce')
    df['min']=pd.to_numeric(df['min'],errors='coerce')
    df['Median_Price'] = (df['max'] + df['min']) / 2


    # Step 2: Calculate 5-period and 34-period SMAs
    df['SMA_5'] = df['Median_Price'].rolling(window=5).mean()
    df['SMA_34'] = df['Median_Price'].rolling(window=34).mean()

    # Step 3: Calculate the Awesome Oscillator (AO)
    df['AO'] = df['SMA_5'] - df['SMA_34']
    print(df['AO'])
    df = df.dropna(subset=['AO'])
    # Step 4: Plot the Awesome Oscillator
    plt.figure(figsize=(12, 6))
    plt.bar(df['Date'], df['AO'], color=['red' if ao < 0 else 'green' for ao in df['AO']], width=1.0)
    plt.title('Awesome Oscillator (AO)')
    plt.xlabel('Date')
    plt.ylabel('AO Value')
    plt.grid()
    # plt.tight_layout()
    img_io = io.BytesIO()
    plt.savefig(img_io, format='png')
    img_io.seek(0)
    plt.close()

    return img_io