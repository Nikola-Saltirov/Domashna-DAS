import pandas as pd
import numpy as np
import locale
import seaborn as sns
import matplotlib.pyplot as plt
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import mean_squared_error, r2_score
from sklearn.model_selection import train_test_split
from keras.models import Sequential
from keras.layers import Input, LSTM, Dense
from datetime import timedelta


def parse_numeric_to_float(dataframe: pd.DataFrame):
    for col in dataframe.columns:
        if col=='Date':
            dataframe[col] = pd.to_datetime(dataframe[col], format='%d.%m.%Y')
        elif dataframe[col].dtype == 'object':
            try:
                dataframe[col] = dataframe[col].apply(locale.atof).astype('float64')
            except:
                pass


def drop_columns(dataframe: pd.DataFrame, columns):
    to_delete = [col for col in dataframe.columns if col not in columns]
    return dataframe.drop(to_delete, axis=1)


def shift_attributes_by_x(dataframe: pd.DataFrame, attributes, x: int):
    copy = dataframe.copy()
    for i in range(x, 0, -1):
        for attr in attributes:
            lag = attr + '_lag_' + str(i)
            copy[lag] = copy[attr].shift(i)
    copy.dropna(inplace=True)
    return copy


# reshape na originalnoto treniracko mnozestvo za da moze da se koristi vo LSTM-modelot
def reshape(X: pd.DataFrame, time_step):
    # scaler = StandardScaler()
    # tmp = scaler.fit_transform(X)
    tmp = X.to_numpy()
    reshaped = tmp.reshape(tmp.shape[0], time_step, n_features)
    return reshaped


# agregiranje na podatocite na nivo na mesec
def group_by_month(dataframe: pd.DataFrame):
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

if __name__ == '__main__':
    locale.setlocale(locale.LC_ALL, 'de_DE.UTF-8')
    #Inicijalizacija na promenlivi
    #Postavuvanje na tiker
    tiker = "ALK"
    # Postavuvanje na target
    target = 'avg_price'
    # inicijalizacija na lag
    lag = 7
    # Atributi za shiftanje
    attributes = ['max', 'min', 'avg_price']
    # broj na atributi sto gi koristime pri klasifikacija
    n_features = len(attributes)

    #Citanje na csv-to
    df = pd.read_csv(f"stocks/data/{tiker}.csv")
    #Data preparation
    df.ffill(axis=0, inplace=True)
    parse_numeric_to_float(df)
    #Gi trgame nepotrebnite koloni
    reduced_dataset = drop_columns(df, attributes)
    #Dodavame lag na max, min i avg
    df_shifted_7d = shift_attributes_by_x(reduced_dataset, attributes, lag)
    # prvo da se zeme target kolonata pred da ja trgneme od trening datasetot
    test = df_shifted_7d[target]
    # trganje na orginalnite koloni od datasetot
    df_shifted_7d.drop(attributes, axis=1, inplace=True)

    #Podelba na treniracko i testiracko mnozestvo
    train = df_shifted_7d
    x_train, x_test, y_train, y_test = train_test_split(train, test, test_size=0.3, shuffle=False)
    # Reshape na X
    x_train = reshape(x_train, lag)
    x_test = reshape(x_test, lag)
    print("X Training shape: " + str(x_train.shape))
    print("X Testing shape: " + str(x_test.shape))
    print("y Training shape: " + str(y_train.shape))
    print("y Testing shape: " + str(y_test.shape))

    # Pravenje na model
    # instanciranje na modelot
    model = Sequential([
        Input((lag, n_features)),
        LSTM(56, activation='relu'),
        Dense(1)
    ])
    model.compile(loss="mse", optimizer="adam")
    print("Training model...")
    history = model.fit(x_train, y_train, validation_split=0.1, epochs=70, batch_size=8, verbose=0)
    #Testing model performance
    pred = model.predict(x_test)
    print(f"Model r2-score: {r2_score(y_test, pred)}")
    # Making predictions for n-next days
    n=7
    current_date = df['Date'][len(df)-1]
    next_n_days = [(current_date + timedelta(days=i)).strftime("%d.%m.%Y") for i in range(1, n+1)]
    next_predicted_n_days = model.predict(x_test[n*(-1):])
    plt.plot(next_n_days, next_predicted_n_days)
