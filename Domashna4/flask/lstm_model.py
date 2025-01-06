import pandas as pd
import numpy as np
import locale
import seaborn as sns
import matplotlib.pyplot as plt
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import mean_absolute_error, r2_score
from sklearn.model_selection import train_test_split
from keras.models import Sequential
from keras.layers import Input, LSTM, Dense
from datetime import timedelta
import io
from matplotlib.ticker import MaxNLocator

class StocksAveragePricePredictor:
    def __init__(self, tiker, lag, timelapse, target):
        self.tiker = tiker
        self.lag = lag
        self.timelapse = timelapse
        self.attributes = ['avg_price']
        self.n_features = len(self.attributes)
        self.dataset = pd.read_csv(f"temp_stocks/temp_data/{tiker}.csv")
        self.target = target

    def parse_numeric_to_float(self):
        locale.setlocale(locale.LC_ALL, 'de_DE.UTF-8')
        for col in self.dataset.columns:
            if col=='Date':
                self.dataset[col] = pd.to_datetime(self.dataset[col], format='%d.%m.%Y')
            elif self.dataset[col].dtype == 'object':
                try:
                    self.dataset[col] = self.dataset[col].apply(locale.atof).astype('float64')
                except:
                    pass
        return self.dataset


    def drop_columns(self, dataframe: pd.DataFrame, columns):
        to_delete = [col for col in dataframe.columns if col not in columns]
        return dataframe.drop(to_delete, axis=1)


    def shift_attributes_by_x(self, dataframe: pd.DataFrame, attributes, x: int):
        copy = dataframe.copy()
        for i in range(x, 0, -1):
            for attr in attributes:
                lag = attr + '_lag_' + str(i)
                copy[lag] = copy[attr].shift(i)
        copy.dropna(inplace=True)
        return copy


    # reshape na originalnoto treniracko mnozestvo za da moze da se koristi vo LSTM-modelot
    def reshape(self, X: pd.DataFrame, time_step):
        # scaler = StandardScaler()
        # tmp = scaler.fit_transform(X)
        tmp = X.to_numpy()
        reshaped = tmp.reshape(tmp.shape[0], time_step, self.n_features)
        return reshaped


    # agregiranje na podatocite na nivo na mesec
    def group_by_month(self, dataframe: pd.DataFrame):
        by_month = dataframe.copy()
        by_month['Date'] = pd.to_datetime(by_month['Date'], dayfirst=True)
        by_month = by_month.groupby(pd.Grouper(key='Date', freq='ME')).agg({
            'last_traded_price': 'last',  # Last closing value of the month
            'max': 'max',  # Maximum high of the month
            'min': 'min',  # Minimum low of the month
            'avg_price': 'mean',  # average per month
            'promet': 'mean',
            'volume': 'sum',  # Total BTC volume for the month
            'promet_BEST': 'sum',  # Total USD volume for the month
            'promet_vo_denari': 'sum'  # Total USD volume for the month
        })
        return by_month

    def prepare_data(self):
        # Data preparation
        self.dataset.ffill(axis=0, inplace=True)
        parsed_numeric = self.parse_numeric_to_float()
        # Gi trgame nepotrebnite koloni
        reduced_dataset = self.drop_columns(parsed_numeric, self.attributes)
        # Dodavame lag na max, min i avg
        df_shifted_7d = self.shift_attributes_by_x(reduced_dataset, self.attributes, self.lag)
        # prvo da se zeme target kolonata pred da ja trgneme od trening datasetot
        test = df_shifted_7d[self.target]
        # trganje na orginalnite koloni od datasetot
        df_shifted_7d.drop(self.attributes, axis=1, inplace=True)
        # Podelba na treniracko i testiracko mnozestvo
        train = df_shifted_7d
        if self.timelapse>30:
            self.lag=3
            by_month = self.group_by_month(parsed_numeric)
            by_month = self.drop_columns(by_month, self.attributes)
            df_shifted_3m = self.shift_attributes_by_x(by_month, self.attributes, self.lag)
            test = df_shifted_3m[self.target]
            df_shifted_3m.drop(self.attributes, axis=1, inplace=True)
            train = df_shifted_3m
        x_train, x_test, y_train, y_test = train_test_split(train, test, test_size=0.3, shuffle=False)
        # Reshape na X
        x_train = self.reshape(x_train, self.lag)
        x_test = self.reshape(x_test, self.lag)
        print("X Training shape: " + str(x_train.shape))
        print("X Testing shape: " + str(x_test.shape))
        print("y Training shape: " + str(y_train.shape))
        print("y Testing shape: " + str(y_test.shape))
        return x_train, x_test, y_train, y_test

    def build_model(self):
        # Pravenje na model
        # instanciranje na modelot
        x_train, x_test, y_train, y_test = self.prepare_data()
        model = Sequential([
            Input((self.lag, self.n_features)),
            LSTM(70, activation='relu'),
            Dense(1)
        ])
        model.compile(loss="mean_absolute_error", optimizer="adam")
        print("Training model...")
        history = model.fit(x_train, y_train, validation_split=0.1, epochs=30, batch_size=8)
        return model, x_test, y_test

    def predict_and_plot(self):
        model, x_test, y_test = self.build_model()
        pred1 = model.predict(x_test)
        print(f"Model r2-score: {r2_score(y_test, pred1)}")
        print(f"Model mean-absolute-error: {mean_absolute_error(y_test, pred1)}")
        # Making predictions for n-next days
        current_date = self.dataset['Date'][len(self.dataset) - 1]
        next_n_days = [(current_date + timedelta(days=i)).strftime("%d.%m.%y") for i in range(1, self.timelapse+1)]
        last = x_test[-1]
        if self.timelapse>30:
            next_n_months = [(current_date + timedelta(days=i)).strftime("%m.%y") for i in range(30, self.timelapse+1, 30)]
            next_predicted_n_months = []
            for i in range(len(next_n_months)+1):
                reshaped_last = last.reshape(1, self.lag, 1)
                pred = model.predict(reshaped_last)
                if i>0:
                    next_predicted_n_months.append(pred[0])
                last = np.append(last, pred[0])
                last = last[1:]
            return self.plot(next_n_months, next_predicted_n_months)

        next_predicted_n_days = []
        for day in next_n_days:
            reshaped_last = last.reshape(1, self.lag, 1)
            pred = model.predict(reshaped_last)
            next_predicted_n_days.append(pred[0])
            last = np.append(last, pred[0])
            last = last[1:]
        return self.plot(next_n_days, next_predicted_n_days)

    def plot(self, x, y):
        self.customize_plot()
        plt.plot(x, y, label=f"{self.tiker} Average", color="green", linewidth=1.5)
        img_io = io.BytesIO()
        plt.savefig(img_io, format='png')
        img_io.seek(0)
        plt.close()
        return img_io

    def customize_plot(self):
        plt.figure(figsize=(12, 6))
        # Customize plot
        fig, ax = plt.subplots()
        plt.title(f"Predicted Average Stock Price for {self.tiker}")
        plt.xlabel("Date")
        plt.ylabel("Predictred Average")
        ax.xaxis.set_major_locator(MaxNLocator(7))
        plt.legend()
        plt.grid()
        plt.tight_layout()

if __name__ == '__main__':
    predictor = StocksAveragePricePredictor('ALK', 7, 210, 'avg_price')
    predictor.predict_and_plot()
