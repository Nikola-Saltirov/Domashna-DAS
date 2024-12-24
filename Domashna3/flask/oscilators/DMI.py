import pandas as pd
import matplotlib.pyplot as plt
from stock_indicators.indicators.common import Quote
from stock_indicators import indicators
import io

# Step 1: Read CSV and clean temp_data
def calcDMI(tiker, interval, start_date, end_date, short_window):

    df = pd.read_csv(f"temp_stocks/temp_data/{tiker}.csv")
    df['Date'] = pd.to_datetime(df['Date'], dayfirst=True)
    df.set_index('Date', inplace=True)
    df = df.loc[start_date:end_date]

    df['max'] = df['max'].astype(str).str.replace('.', '').str.replace(',', '.')
    df['min'] = df['min'].astype(str).str.replace('.', '').str.replace(',', '.')

    df['max'] = pd.to_numeric(df['max'], errors='coerce')
    df['min'] = pd.to_numeric(df['min'], errors='coerce')

    df['avg_price'] = df['avg_price'].astype(str).str.replace('.', '').str.replace(',', '.')
    df['avg_price'] = pd.to_numeric(df['avg_price'], errors='coerce')

    df = df.reset_index()
    df['Date'] = pd.to_datetime(df['Date'], format='%d.%m.%Y', errors='coerce')

    # Step 5: Convert to Quote objects
    quotes = [
        Quote(row.Date, None, row['max'], row['min'], row['avg_price'], None)
        for _, row in df.iterrows()
        if pd.notnull(row['max']) and pd.notnull(row['min']) and pd.notnull(row['avg_price'])
    ]

    results = indicators.get_dema(quotes, lookback_periods=short_window)

    dates = [result.date for result in results if result.dema is not None]
    demarker_values = [result.dema for result in results if result.dema is not None]

    # Step 8: Plot DeMarker Indicator
    plt.figure(figsize=(12, 6))

    # Plot DeMarker values
    plt.plot(dates, demarker_values, label=f"DeMarker ({short_window})", color="blue", linewidth=1.5)

    # Add reference lines for 0.7 (overbought) and 0.3 (oversold)
    plt.axhline(y=0.7, color='green', linestyle='--', label="Overbought (0.7)")
    plt.axhline(y=0.3, color='red', linestyle='--', label="Oversold (0.3)")

    # Customize plot
    plt.title("DeMarker Indicator")
    plt.xlabel("Date")
    plt.ylabel("DeMarker Value")
    plt.legend()
    plt.grid()
    plt.tight_layout()

    img_io = io.BytesIO()
    plt.savefig(img_io, format='png')
    img_io.seek(0)
    plt.close()

    return img_io
