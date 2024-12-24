import pandas as pd
import matplotlib.pyplot as plt
from stock_indicators.indicators.common import Quote
from stock_indicators import indicators
import io


def calcSO(tiker, interval, start_date, end_date, short_window):
    # Step 1: Read CSV and clean temp_data
    df = pd.read_csv(f"temp_stocks/temp_data/{tiker}.csv")
    df = df.tail(int(interval) + 14)

    # Step 2: Fix 'max' and 'min' columns (convert to numeric)
    df['max'] = df['max'].astype(str).str.replace('.', '').str.replace(',', '.')
    df['min'] = df['min'].astype(str).str.replace('.', '').str.replace(',', '.')

    df['max'] = pd.to_numeric(df['max'], errors='coerce')
    df['min'] = pd.to_numeric(df['min'], errors='coerce')

    # Step 3: Clean up 'avg_price' column
    df['avg_price'] = df['avg_price'].astype(str).str.replace('.', '').str.replace(',', '.')
    df['avg_price'] = pd.to_numeric(df['avg_price'], errors='coerce')

    # Step 4: Parse Date column properly
    df['Date'] = pd.to_datetime(df['Date'], format='%d.%m.%Y', errors='coerce')

    # Step 5: Convert to Quote objects
    quotes = [
        Quote(row.Date, None, row['max'], row['min'], row['avg_price'], None)
        for _, row in df.iterrows()
        if pd.notnull(row['max']) and pd.notnull(row['min']) and pd.notnull(row['avg_price'])
    ]

    # Step 6: Calculate Stochastic Oscillator
    results = indicators.get_stoch(quotes, lookback_periods=14, signal_periods=3, smooth_periods=3)

    # Step 7: Extract dates, %K and %D values for plotting
    dates = [result.date for result in results if result.k is not None and result.d is not None]
    stoch_k_values = [result.k for result in results if result.k is not None and result.d is not None]
    stoch_d_values = [result.d for result in results if result.d is not None and result.k is not None]

    print(len(dates))
    print(len(stoch_k_values))
    print(len(stoch_d_values))


    # Step 8: Plot Stochastic Oscillator
    plt.figure(figsize=(12, 6))

    # Plot %K and %D lines
    plt.plot(dates, stoch_k_values, label="%K (Stochastic)", color="blue", linewidth=1.5)
    plt.plot(dates, stoch_d_values, label="%D (Signal)", color="orange", linestyle="--", linewidth=1.5)

    # Add reference lines for 80 (overbought) and 20 (oversold)
    plt.axhline(y=80, color='green', linestyle='--', label="Overbought (80)")
    plt.axhline(y=20, color='red', linestyle='--', label="Oversold (20)")

    # Customize plot
    plt.title("Stochastic Oscillator")
    plt.xlabel("Date")
    plt.ylabel("Stochastic Value")
    plt.legend()
    plt.grid()
    plt.tight_layout()

    img_io = io.BytesIO()
    plt.savefig(img_io, format='png')
    img_io.seek(0)
    plt.close()

    return img_io
