import pandas as pd


df = pd.read_csv("stocks/data/ALK.csv")
print(df.isnull().sum())