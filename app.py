import pandas as pd
import streamlit as st
import plotly.express as px
import matplotlib.pyplot as plt
import seaborn as sns
from streamlit_folium import folium_static
import folium

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
st.markdown(f"<h2 style='text-align: center; font-size: 24px;'>Média de precipitação por mês - Estado: {state if state != 'Todos' else 'Todos os estados'}</h2>", unsafe_allow_html=True)

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

# Filtrar os dados conforme a seleção do estado
if state != 'Todos':
    df_monthly_avg = df_monthly_avg[df_monthly_avg['estado'] == state]

# Criando uma tabela cruzada (pivot table) para usar no heatmap
heatmap_data = df_monthly_avg.pivot(index='estado', columns='Month', values='avg_precipitacao')

# Criando o gráfico
st.markdown(f"<h2 style='text-align: center; font-size: 24px;'>Mapa de calor da média de precipitação por mês - Estado: {state if state != 'Todos' else 'Todos os estados'}</h2>", unsafe_allow_html=True)

plt.figure(figsize=(12, 8))
sns.heatmap(heatmap_data, annot=True, fmt=".1f", cmap="Blues", cbar_kws={'label': 'Média de Precipitação'})

plt.xlabel('Mês')
plt.ylabel('Estado')
plt.title(f'Média de Precipitação Mensal - Estado: {state if state != "Todos" else "Todos os estados"}')

# Exibir o heatmap no Streamlit
st.pyplot(plt)

# Agrupando por bioma e mês para calcular a soma ou média de 'avg_precipitacao'
# Aqui usarei a média como exemplo, mas se você preferir a soma, altere 'mean' para 'sum'
df_bioma_precip = df.groupby(['bioma', 'Month'])['avg_precipitacao'].mean().reset_index()

# Filtrar os dados para o mês selecionado
df_month_filtered = df_bioma_precip[df_bioma_precip['Month'] == month]

# Criando o gráfico de pizza
st.markdown(f"<h2 style='text-align: center; font-size: 24px;'>Distribuição da Precipitação por Bioma - Mês: {month}</h2>", unsafe_allow_html=True)
plt.figure(figsize=(8, 8))

# Gráfico de pizza para o mês selecionado
plt.pie(
    df_month_filtered['avg_precipitacao'],
    labels=df_month_filtered['bioma'],
    autopct='%1.1f%%',
    startangle=140
)
plt.title(f'Distribuição da Precipitação por Bioma - Mês: {month}')

# Exibir gráfico no Streamlit
st.pyplot(plt)

# Dados das coordenadas centrais dos estados brasileiros
coords = {
    'estado': ["AC", "AL", "AM", "AP", "BA", "CE", "DF", "ES", "GO", "MA", "MT", "MS", "MG", "PA", "PB", "PR", "PE", "PI", "RJ", "RN", "RO", "RR", "RS", "SC", "SE", "SP", "TO"],
    'latitude': [-9.07, -9.57, -3.47, 1.41, -12.97, -5.2, -15.83, -19.19, -15.98, -2.53, -12.64, -20.51, -18.1, -3.79, -7.12, -25.43, -8.28, -5.09, -22.84, -5.81, -10.83, 2.82, -30.03, -27.33, -10.91, -23.55, -10.25],
    'longitude': [-70.81, -36.64, -65.1, -51.77, -38.51, -39.53, -47.86, -40.34, -49.86, -44.3, -55.43, -54.54, -44.38, -52.48, -36.52, -49.27, -37.86, -42.81, -43.15, -35.2, -63.04, -60.67, -51.22, -49.44, -37.07, -46.63, -48.25]
}

# Criando o DataFrame de coordenadas
df_coords = pd.DataFrame(coords)

# Agrupar os dados para calcular a média de precipitação por estado
df_precip_estado = df.groupby('estado')['avg_precipitacao'].mean().reset_index()

# Mesclar os dados de precipitação com as coordenadas
df_precip_estado = df_precip_estado.merge(df_coords, on='estado')

# Carregar o arquivo GeoJSON com as fronteiras dos estados do Brasil
geojson_path = 'data/br_states.json'  # Substitua pelo caminho correto do arquivo

# Criar o mapa centralizado no Brasil
m = folium.Map(location=[-15.788497, -47.879873], zoom_start=4)

# Adicionar o mapa coroplético
folium.Choropleth(
    geo_data=geojson_path,
    name="choropleth",
    data=df_precip_estado,
    columns=["estado", "avg_precipitacao"],
    key_on="feature.id",  # Atualizado para usar a propriedade 'id'
    fill_color="YlGnBu",
    fill_opacity=0.7,
    line_opacity=0.2,
    legend_name="Média de Precipitação (mm)"
).add_to(m)

# Adicionar popup com informações de precipitação
for _, row in df_precip_estado.iterrows():
    folium.Marker(
        location=[row['latitude'], row['longitude']],
        popup=f"{row['estado']}: {row['avg_precipitacao']} mm",
    ).add_to(m)

# Criando o gráfico
st.markdown(f"<h2 style='text-align: center; font-size: 24px;'>Mapa de precipitação media por estado</h2>", unsafe_allow_html=True)
folium_static(m)