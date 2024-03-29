# -*- coding: utf-8 -*-
"""tech_challenge_2_fase

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1LyLSzoDVCMfy904hlkhHgN-I2fKvVkh0

#Importando as bibliotécas
"""

# Commented out IPython magic to ensure Python compatibility.
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import plotly.graph_objects as go
import seaborn as sns
# %matplotlib inline

import yfinance as yf

from statsmodels.tsa.seasonal import seasonal_decompose
from statsmodels.tsa.stattools import adfuller
from statsmodels.tsa.stattools import acf, pacf
from statsmodels.graphics.tsaplots import plot_acf, plot_pacf
from statsmodels.tsa.seasonal import seasonal_decompose
from statsmodels.tsa.arima.model import ARIMA

from sklearn.preprocessing import MinMaxScaler
from sklearn.metrics import mean_squared_error
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_absolute_error


import warnings
warnings.filterwarnings('ignore')

from prophet import Prophet

"""#Importando os dados"""

symbol = '^BVSP'
start_date = '2020-01-26'
end_date = '2024-01-26'

df = yf.download(symbol, start=start_date, end=end_date)

# Verifica pontos nulos
print(df.isnull().sum())
null_columns = df.columns[df.isnull().any()]
print(df[df.isnull().any(axis=1)][null_columns])

# Preenche pontos nulos
df = df.fillna(method='ffill')
# Se o primeiro registro for NaN, copie o valor do segundo registro
if df.iloc[0].isnull().any():
    df.iloc[0] = df.iloc[0].fillna(df.iloc[1])
null_columns = df.columns[df.isnull().any()]
print(df[df.isnull().any(axis=1)][null_columns])

df

"""#Produzindo uma EDA"""

df_ajustado = df['Close']
df_ajustado = pd.DataFrame(df_ajustado)
df_ajustado

plt.plot(df_ajustado.index, df_ajustado.Close)

resultados = seasonal_decompose(df_ajustado, period = 5, model='multiplicative')


fig, (ax1, ax2, ax3, ax4) = plt.subplots(4,1, figsize = (15,10))

resultados.observed.plot(ax=ax1)
resultados.trend.plot(ax=ax2)
resultados.seasonal.plot(ax=ax3)
resultados.resid.plot(ax=ax4)

plt.tight_layout()

X  = df_ajustado.Close.values

result = adfuller(X)

print("Teste ADF")
print(f"Teste Estatístico: {result[0]}")
print(f"P-Value: {result[1]}")
print("Valores críticos:")

for key, value in result[4].items():
  print(f"\t{key}: {value}")

ma = df_ajustado.rolling(12).mean()


f, ax = plt.subplots()
df_ajustado.plot (ax=ax, legend = False)
ma.plot (ax=ax, legend = False, color = 'r')


plt.tight_layout()

df_ajustado_log = np.log(df_ajustado)
ma_log = df_ajustado_log.rolling(12).mean()

f, ax = plt.subplots()
df_ajustado_log.plot (ax=ax, legend = False)
ma_log.plot (ax=ax, legend = False, color = 'r')


plt.tight_layout()

df_s = (df_ajustado_log - ma_log ).dropna()

ma_s = df_s.rolling(12).mean()

std = df_s.rolling(12).std()

f, ax = plt.subplots()
df_s.plot (ax=ax, legend = False)
ma_s.plot (ax=ax, legend = False, color = 'r')
std.plot (ax=ax, legend = False, color = 'g')

plt.tight_layout()

X_s  = df_s.Close.values

result_s = adfuller(X_s)

print("Teste ADF")
print(f"Teste Estatístico: {result_s[0]}")
print(f"P-Value: {result_s[1]}")
print("Valores críticos:")

for key, value in result_s[4].items():
  print(f"\t{key}: {value}")

df_diff = df_s.diff(1)
ma_diff = df_diff.rolling(12).mean()

std_diff = df_diff.rolling(12).std()

f, ax = plt.subplots()
df_diff.plot (ax=ax, legend = False)
ma_diff.plot (ax=ax, legend = False, color = 'r')
std_diff.plot (ax=ax, legend = False, color = 'g')

plt.tight_layout()

X_diff  = df_diff.Close.dropna().values

result_diff = adfuller(X_diff)

print("Teste ADF")
print(f"Teste Estatístico: {result_diff[0]}")
print(f"P-Value: {result_diff[1]}")
print("Valores críticos:")

for key, value in result_diff[4].items():
  print(f"\t{key}: {value}")

lag_acf = acf(df_diff.dropna(), nlags = 25)
lag_pacf = pacf(df_diff.dropna(), nlags = 25)

plt.plot(lag_acf)

plt.axhline(y= -1.96/(np.sqrt((len(df_diff) -1))), linestyle = '--', color = 'gray', linewidth = .7)
plt.axhline(y= 0, linestyle = '--', color = 'gray', linewidth = .7)
plt.axhline(y= 1.96/(np.sqrt((len(df_diff) -1))), linestyle = '--', color = 'gray', linewidth = .7)

plt.title("ACF")

plt.show()

plot_acf(df_ajustado.Close)

plt.show()

plt.plot(lag_pacf)

plt.axhline(y= -1.96/(np.sqrt((len(df_diff) -1))), linestyle = '--', color = 'gray', linewidth = .7)
plt.axhline(y= 0, linestyle = '--', color = 'gray', linewidth = .7)
plt.axhline(y= 1.96/(np.sqrt((len(df_diff) -1))), linestyle = '--', color = 'gray', linewidth = .7)

plt.title("PACF")

plt.show()

plot_pacf(df_ajustado.Close)

plt.show()

modelo = ARIMA(df_diff, order=(2,1,2))#(p,d,q)
resultado_AR = modelo.fit()
plt.plot(df_diff)
plt.plot(resultado_AR.fittedvalues, color='red')
plt.title('RSS: %.4f'%sum((resultado_AR.fittedvalues - df_diff['Close'])**2))
print('Plotting AR model')

# Verifica pontos nulos
print(df_diff.isnull().sum())
null_columns = df_diff.columns[df_diff.isnull().any()]
print(df_diff[df_diff.isnull().any(axis=1)][null_columns])

# Preenche pontos nulos
df = df_diff.fillna(method='ffill')
# Se o primeiro registro for NaN, copie o valor do segundo registro
if df_diff.iloc[0].isnull().any():
    df_diff.iloc[0] = df_diff.iloc[0].fillna(df_diff.iloc[1])
null_columns = df_diff.columns[df_diff.isnull().any()]
print(df_diff[df_diff.isnull().any(axis=1)][null_columns])

predictions = resultado_AR.fittedvalues


predictions.index = df_diff.index

predicted_values = df_ajustado_log['Close'].iloc[0] + np.cumsum(predictions)


mape = mean_absolute_error(df_diff['Close'], predicted_values) * 100

print(f"MAPE: {mape:.2f}%")

#Coletando os dados novamente

symbol = '^BVSP'
start_date = '2020-01-26'
end_date = '2024-01-26'

df = yf.download(symbol, start=start_date, end=end_date)S
df = df.reset_index('Date')
df['Date'] = pd.to_datetime(df['Date']) #realizando a conversão da data para formato datetime
df.drop(columns=['Open', 'High', 'Low', 'Volume', 'Adj Close'], inplace=True)
# Renomeando as colunas para 'ds' e 'y'
df = df.rename(columns={'Date': 'ds', 'Close': 'y'})
#df[['ds','y']] = df[['Date','Close']]
df.head()

#train_data = df.sample(frac=0.8, random_state=0)
#test_data = df.drop(train_data.index)

# Dividindo os dados em treinamento, validação e teste
train_size = int(len(df) * 0.7)
val_size = int(len(df) * 0.15)
test_size = len(df) - train_size - val_size

train_data, test_and_val_data = np.split(df, [train_size])
val_data, test_data = np.split(test_and_val_data, [val_size])


print(f'training data size : {train_data.shape}')
print(f'testing data size : {test_data.shape}')

train_data

modelo = Prophet(daily_seasonality=True)
modelo.fit(train_data)
dataFramefuture = modelo.make_future_dataframe(periods=20, freq='M')
previsao = modelo.predict(dataFramefuture)
previsao.head()

modelo.plot(previsao, figsize=(20,6));
plt.plot(test_and_val_data['ds'], test_and_val_data['y'], '.r')

previsao_cols = ['ds', 'yhat']
valores_reais_cols = ['ds', 'y']

previsao = previsao[previsao_cols]
valores_reais = test_and_val_data[valores_reais_cols]

# Mesclar os DataFrames nas colunas 'ds' para comparar previsões e valores reais
resultados = pd.merge(previsao, valores_reais, on='ds', how='inner')

# Calcular o erro percentual absoluto para cada ponto de dados
resultados['erro_percentual_absoluto'] = np.abs((resultados['y'] - resultados['yhat']) / resultados['y']) * 100

# Calcular o MAPE
mape = np.mean(resultados['erro_percentual_absoluto'])

print(f"MAPE: {mape:.2f}%")

resultados