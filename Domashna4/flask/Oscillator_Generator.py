import pandas as pd
import matplotlib.pyplot as plt
from stock_indicators.indicators.common import Quote
import io
from abc import ABC, abstractmethod
import os

# Path to the CSV directory
BASE_DIR = os.getenv("CSV_DIR", "./temp_stocks")

class Oscillator_Generator(ABC):
    def __init__(self, tiker, interval):
        self.df = None
        self.tiker = tiker
        self.interval = interval

    def generate_graph(self):
        self.read_dataframe()
        self.prepare_data()
        return self.plot()

    def read_dataframe(self):
        # Step 1: Read CSV and clean temp_data
        # os.path.join(BASE_DIR, '../names.csv')
        # df = pd.read_csv(f"temp_stocks/temp_data/{self.tiker}.csv")
        fileName = f'{self.tiker}.csv'
        csv_path = os.path.join(BASE_DIR, 'temp_data', fileName)
        df = pd.read_csv(csv_path)
        df.dropna(inplace=True)
        self.df = df

    def prepare_data(self):
        # Step 2: Fix 'max' and 'min' columns (convert to numeric)
        self.df = self.df.tail(int(self.interval) + 20)
        self.df['max'] = self.df['max'].astype(str).str.replace('.', '').str.replace(',', '.')
        self.df['min'] = self.df['min'].astype(str).str.replace('.', '').str.replace(',', '.')
        self.df['max'] = pd.to_numeric(self.df['max'], errors='coerce')
        self.df['min'] = pd.to_numeric(self.df['min'], errors='coerce')
        # Step 3: Clean up 'avg_price' column
        self.df['avg_price'] = self.df['avg_price'].astype(str).str.replace('.', '').str.replace(',', '.')
        self.df['avg_price'] = pd.to_numeric(self.df['avg_price'], errors='coerce')
        # Step 4: Parse Date column properly
        self.df['Date'] = pd.to_datetime(self.df['Date'], format='%d.%m.%Y', errors='coerce')

    def get_quotes(self):
        # Step 5: Convert to Quote objects
        quotes = [
            Quote(row.Date, None, row['max'], row['min'], row['avg_price'], None)
            for _, row in self.df.iterrows()
            if pd.notnull(row['max']) and pd.notnull(row['min']) and pd.notnull(row['avg_price'])
        ]
        return quotes

    def plot(self):
        # Step 8: Plot CMO
        plt.figure(figsize=(12, 6))
        #implemented in the abstract class' extensions
        self.customize_plot()
        #the rest is boilerplate
        plt.legend()
        plt.grid()
        plt.tight_layout()
        #Generate and return img_io object
        img_io = io.BytesIO()
        plt.savefig(img_io, format='png')
        img_io.seek(0)
        plt.close()
        return img_io

    @abstractmethod
    def customize_plot(self):
        pass

    @abstractmethod
    def get_results(self):
        pass
