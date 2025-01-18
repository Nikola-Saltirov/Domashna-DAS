import matplotlib.pyplot as plt
from .Oscillator_Generator import *
from stock_indicators import indicators
import pandas as pd

class CMO_Generator(Oscillator_Generator):
    def __init__(self, tiker, interval):
        super().__init__(tiker, interval)

    def get_results(self):
        # Step 6: Calculate CMO (Chande Momentum Oscillator)
        quotes = self.get_quotes()
        results = indicators.get_cmo(quotes, 20)
        # Step 7: Extract dates and CMO values for plotting
        cmo_values = [result.cmo for result in results if result.cmo is not None]
        dates = [result.date for result in results if result.cmo is not None]
        return dates, cmo_values

    def customize_plot(self):
        dates, values = self.get_results()
        plt.plot(dates, values, label="CMO (20)", color="blue", linewidth=1.5)
        # Add reference lines for +50 and -50
        plt.axhline(y=50, color='green', linestyle='--', label="Upper Level (+50)")
        plt.axhline(y=-50, color='red', linestyle='--', label="Lower Level (-50)")
        # Customize plot
        plt.title("Chande Momentum Oscillator (CMO)")
        plt.xlabel("Date")
        plt.ylabel("CMO Value")

class CCI_Generator(Oscillator_Generator):
    def __init__(self, tiker, interval):
        super().__init__(tiker, interval)

    def get_results(self):
        quotes = self.get_quotes()
        # Step 6: Calculate CCI
        results = indicators.get_cci(quotes, 20)
        # Step 7: Print results
        dates = [result.date for result in results if result.cci is not None]
        cci_values = [result.cci for result in results if result.cci is not None]
        return dates, cci_values

    def customize_plot(self):
        dates, values = self.get_results()
        plt.plot(dates, values, label=f"CCI ({self.interval})", color="blue", linewidth=1.5)
        # Add reference lines for +100 and -100
        plt.axhline(y=100, color='green', linestyle='--', label="Overbought (+100)")
        plt.axhline(y=-100, color='red', linestyle='--', label="Oversold (-100)")
        # Customize plot
        plt.title("Commodity Channel Index (CCI)")
        plt.xlabel("Date")
        plt.ylabel("CCI Value")

class Stochastic_O_Generator(Oscillator_Generator):
    def __init__(self, tiker, interval):
        super().__init__(tiker, interval)

    def get_results(self):
        quotes = self.get_quotes()
        # Step 6: Calculate Stochastic Oscillator
        results = indicators.get_stoch(quotes, lookback_periods=14, signal_periods=3, smooth_periods=3)
        # Step 7: Extract dates, %K and %D values for plotting
        dates = [result.date for result in results if result.k is not None and result.d is not None]
        stoch_k_values = [result.k for result in results if result.k is not None and result.d is not None]
        stoch_d_values = [result.d for result in results if result.d is not None and result.k is not None]
        return dates, stoch_k_values, stoch_d_values

    def customize_plot(self):
        dates, stoch_k_values, stoch_d_values = self.get_results()
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

class RSI_Generator(Oscillator_Generator):
    def __init__(self, tiker, interval):
        super().__init__(tiker, interval)

    def get_results(self):
        quotes = self.get_quotes()
        # Step 6: Calculate RSI
        results = indicators.get_rsi(quotes, lookback_periods=14)
        # Step 7: Extract dates and RSI values for plotting
        dates = [result.date for result in results if result.rsi is not None]
        rsi_values = [result.rsi for result in results if result.rsi is not None]
        return dates, rsi_values

    def customize_plot(self):
        dates, rsi_values = self.get_results()
        # Plot RSI values
        plt.plot(dates, rsi_values, label="RSI (14)", color="blue", linewidth=1.5)
        # Add reference lines for 70 and 30
        plt.axhline(y=70, color='green', linestyle='--', label="Overbought (70)")
        plt.axhline(y=30, color='red', linestyle='--', label="Oversold (30)")
        # Customize plot
        plt.title("Relative Strength Index (RSI)")
        plt.xlabel("Date")
        plt.ylabel("RSI Value")

class DMI_Generator(Oscillator_Generator):
    def __init__(self, tiker, interval, start_date, end_date, short_window):
        super().__init__(tiker, interval)
        self.start_date = start_date
        self.end_date = end_date
        self.short_window = short_window

    def prepare_data(self):
        self.df['Date'] = pd.to_datetime(self.df['Date'], dayfirst=True)
        self.df.set_index('Date', inplace=True)
        self.df = self.df.loc[self.start_date:self.end_date]
        # Step 2: Fix 'max' and 'min' columns (convert to numeric)
        self.df = self.df.tail(int(self.interval) + 20)
        self.df['max'] = self.df['max'].astype(str).str.replace('.', '').str.replace(',', '.')
        self.df['min'] = self.df['min'].astype(str).str.replace('.', '').str.replace(',', '.')
        self.df['max'] = pd.to_numeric(self.df['max'], errors='coerce')
        self.df['min'] = pd.to_numeric(self.df['min'], errors='coerce')
        # Step 3: Clean up 'avg_price' column
        self.df['avg_price'] = self.df['avg_price'].astype(str).str.replace('.', '').str.replace(',', '.')
        self.df['avg_price'] = pd.to_numeric(self.df['avg_price'], errors='coerce')
        #reset the index
        self.df = self.df.reset_index()
        # Step 4: Parse Date column properly
        self.df['Date'] = pd.to_datetime(self.df['Date'], format='%d.%m.%Y', errors='coerce')

    def get_results(self):
        quotes = self.get_quotes()
        results = indicators.get_dema(quotes, lookback_periods=self.short_window)
        dates = [result.date for result in results if result.dema is not None]
        demarker_values = [result.dema for result in results if result.dema is not None]
        return dates, demarker_values

    def customize_plot(self):
        dates, demarker_values = self.get_results()
        # Plot DeMarker values
        plt.plot(dates, demarker_values, label=f"DeMarker ({self.short_window})", color="blue", linewidth=1.5)
        # Add reference lines for 0.7 (overbought) and 0.3 (oversold)
        plt.axhline(y=0.7, color='green', linestyle='--', label="Overbought (0.7)")
        plt.axhline(y=0.3, color='red', linestyle='--', label="Oversold (0.3)")
        # Customize plot
        plt.title("DeMarker Indicator")
        plt.xlabel("Date")
        plt.ylabel("DeMarker Value")

class AO_Generator(Oscillator_Generator):
    def __init__(self, tiker, interval):
        super().__init__(tiker, interval)

    def get_results(self):
        median_price = (self.df['max'] + self.df['min']) / 2
        # Step 2: Calculate 5-period and 34-period SMAs
        sma_5 = median_price.rolling(window=5).mean()
        sma_34= median_price.rolling(window=34).mean()
        # Step 3: Calculate the Awesome Oscillator (AO)
        ao = sma_5 - sma_34
        return ao

    def customize_plot(self):
        ao = self.get_results()
        plt.bar(self.df['Date'], ao, color=['red' if ao_ < 0 else 'green' for ao_ in ao], width=1.0)
        plt.title('Awesome Oscillator (AO)')
        plt.xlabel('Date')
        plt.ylabel('AO Value')