import pandas as pd
from stock_indicators.indicators.common import Quote
from stock_indicators import indicators
import matplotlib.pyplot as plt
import io


def calcCCI(tiker, interval, start_date, end_date, short_window):

    # Step 1: Read CSV and clean temp_data
    df = pd.read_csv(f"temp_stocks/temp_data/{tiker}.csv")
    df=df.tail(int(interval)+20)
    df['Date'] = pd.to_datetime(df['Date'], format='%d.%m.%Y', errors='coerce')



    # Step 2: Fix 'max' and 'min' columns (convert to numeric)
    df['max'] = df['max'].astype(str).str.replace('.', '').str.replace(',', '.')
    df['min'] = df['min'].astype(str).str.replace('.', '').str.replace(',', '.')

    df['max'] = pd.to_numeric(df['max'], errors='coerce')
    df['min'] = pd.to_numeric(df['min'], errors='coerce')

    # Step 3: Clean up 'avg_price' column
    df['avg_price'] = df['avg_price'].astype(str).str.replace('.', '').str.replace(',', '.')
    df['avg_price'] = pd.to_numeric(df['avg_price'], errors='coerce')

    # Step 4: Parse Date column properly
    # df['Date'] = pd.to_datetime(df['Date'], format='%d.%m.%Y', errors='coerce')
    # print(len(df))
    # Step 5: Convert to Quote objects
    quotes = [
    Quote(row.Date, None, row['max'], row['min'], row['avg_price'], None)
    for _, row in df.iterrows()
    if pd.notnull(row['max']) and pd.notnull(row['min']) and pd.notnull(row['avg_price'])
    ]

    # Step 6: Calculate CCI
    results = indicators.get_cci(quotes, 20)

    # Step 7: Print results
    dates = [result.date for result in results if result.cci is not None]
    cci_values = [result.cci for result in results if result.cci is not None]

    # Step 8: Plot CCI
    plt.figure(figsize=(12, 6))
    plt.plot(dates, cci_values, label=f"CCI ({interval})", color="blue", linewidth=1.5)

    # Add reference lines for +100 and -100
    plt.axhline(y=100, color='green', linestyle='--', label="Overbought (+100)")
    plt.axhline(y=-100, color='red', linestyle='--', label="Oversold (-100)")

    # Customize plot
    plt.title("Commodity Channel Index (CCI)")
    plt.xlabel("Date")
    plt.ylabel("CCI Value")
    plt.legend()
    plt.grid()
    plt.tight_layout()

    img_io = io.BytesIO()
    plt.savefig(img_io, format='png')
    img_io.seek(0)
    plt.close()

    return img_io
