import pandas as pd
import matplotlib.pyplot as plt
from stock_indicators.indicators.common import Quote
from stock_indicators import indicators
import io


def calcRSI(tiker, interval, start_date, end_date, short_window):


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

    # Step 6: Calculate RSI
    results = indicators.get_rsi(quotes, lookback_periods=14)

    # Step 7: Extract dates and RSI values for plotting
    dates = [result.date for result in results if result.rsi is not None]
    rsi_values = [result.rsi for result in results if result.rsi is not None]

    # Step 8: Plot RSI
    plt.figure(figsize=(12, 6))

    # Plot RSI values
    plt.plot(dates, rsi_values, label="RSI (14)", color="blue", linewidth=1.5)

    # Add reference lines for 70 and 30
    plt.axhline(y=70, color='green', linestyle='--', label="Overbought (70)")
    plt.axhline(y=30, color='red', linestyle='--', label="Oversold (30)")

    # Customize plot
    plt.title("Relative Strength Index (RSI)")
    plt.xlabel("Date")
    plt.ylabel("RSI Value")
    plt.legend()
    plt.grid()
    plt.tight_layout()

    img_io = io.BytesIO()
    plt.savefig(img_io, format='png')
    img_io.seek(0)
    plt.close()

    return img_io
