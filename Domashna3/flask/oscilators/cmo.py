import pandas as pd
import matplotlib.pyplot as plt
from stock_indicators.indicators.common import Quote
from stock_indicators import indicators
import io

def calcCMO(tiker, interval, start_date, end_date, short_window):

    # Step 1: Read CSV and clean temp_data
    df = pd.read_csv(f"temp_stocks/temp_data/{tiker}.csv")
    df = df.tail(int(interval)+20)
    df.dropna(inplace=True)

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

    # Step 6: Calculate CMO (Chande Momentum Oscillator)
    results = indicators.get_cmo(quotes, 20)

    # Step 7: Extract dates and CMO values for plotting
    dates = [result.date for result in results if result.cmo is not None]
    cmo_values = [result.cmo for result in results if result.cmo is not None]

    # Step 8: Plot CMO
    plt.figure(figsize=(12, 6))
    plt.plot(dates, cmo_values, label="CMO (20)", color="blue", linewidth=1.5)

    # Add reference lines for +50 and -50
    plt.axhline(y=50, color='green', linestyle='--', label="Upper Level (+50)")
    plt.axhline(y=-50, color='red', linestyle='--', label="Lower Level (-50)")

    # Customize plot
    plt.title("Chande Momentum Oscillator (CMO)")
    plt.xlabel("Date")
    plt.ylabel("CMO Value")
    plt.legend()
    plt.grid()
    plt.tight_layout()

    img_io = io.BytesIO()
    plt.savefig(img_io, format='png')
    img_io.seek(0)
    plt.close()

    return img_io
