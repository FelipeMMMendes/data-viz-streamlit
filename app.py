import pandas as pd
import streamlit as st
import plotly.express as px
import matplotlib.pyplot as plt

df = pd.read_csv('data\Dataset_FireWatch_Brazil_2024_combined_updated.csv')

df['data'] = pd.to_datetime(df['data'])
df = df.sort_values('data')

df['Month'] = df['data'].apply(lambda x: str(x.month))

# Adiciona a opção "Todos" para o filtro de mês e estado
month_options = ['Todos'] + list(df['Month'].unique())
state_options = ['Todos'] + list(df['estado'].unique())

month = st.sidebar.selectbox('Mês', month_options)

# Define "DF" como padrão inicial para o filtro de estado
state_default = 'DF' if 'DF' in df['estado'].unique() else state_options[0]
state = st.sidebar.selectbox('Estado', state_options, index=state_options.index(state_default))

# Filtragem condicional com base na seleção
if month == 'Todos' and state == 'Todos':
    df_filtered = df
elif month == 'Todos':
    df_filtered = df[df['estado'] == state]
elif state == 'Todos':
    df_filtered = df[df['Month'] == month]
else:
    df_filtered = df[(df['Month'] == month) & (df['estado'] == state)]

df_filtered

# Configurar o fundo bege para o gráfico
plt.rcParams['axes.facecolor'] = '#f5f5dc'  # Cor bege

# Preparação dos dados
df['data'] = pd.to_datetime(df['data'])
df = df.sort_values('data')

# Agrupar os dados por estado e mês, calculando a média de avg_precipitacao
df_monthly_avg = df.groupby(['estado', 'Month'])['avg_precipitacao'].mean().reset_index()

# Converter a coluna 'Month' para numérico para ordenar corretamente
df_monthly_avg['Month'] = pd.to_numeric(df_monthly_avg['Month'])

# Ordenar os dados pelo mês
df_monthly_avg = df_monthly_avg.sort_values('Month')

# Filtra os dados conforme o estado selecionado
if state != 'Todos':
    df_filtered = df_monthly_avg[df_monthly_avg['estado'] == state]
else:
    df_filtered = df_monthly_avg

# Criando o gráfico
st.write(f"Média de precipitação por mês - Estado: {state if state != 'Todos' else 'Todos os estados'}")
plt.figure(figsize=(10, 6))

# Plotando os dados
for estado in df_filtered['estado'].unique():
    subset = df_filtered[df_filtered['estado'] == estado]
    plt.plot(subset['Month'], subset['avg_precipitacao'], marker='o', label=estado)

plt.xlabel('Mês')
plt.ylabel('Média de Precipitação')
plt.title('Média de Precipitação por Mês e Estado')
plt.xticks(ticks=range(1, 11), labels=range(1, 11))  # Definir os ticks de 1 a 12 para meses
plt.legend(title='Estado')
plt.tight_layout()

# Exibir gráfico no Streamlit
st.pyplot(plt)

col1, col2 = st.columns(2)
col3, col4, col5 = st.columns(3)


