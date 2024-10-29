# app.py
import streamlit as st
import geopandas as gpd
import pandas as pd
import plotly.express as px
import json

# Dividir a página em duas colunas
col1, col2 = st.columns(2)

df = pd.read_csv('data/Dataset_FireWatch_Brazil_2024_combined.csv', sep=',',encoding='utf-8')

df['data'] = pd.to_datetime(df['data'])
df = df.sort_values('data')

df['Month'] =  df['data'].apply(lambda x: str(x.year) + '-' + str(x.month))
month = st.sidebar.selectbox('Mês', df['Month'].unique())

df_filtered = df[df['Month'] == month]

col1, col2 = st.columns(2)
col3, col4, col5 = st.columns(3)

with col1:

    queim_dia = px.bar(df_filtered, x='data', y='avg_risco_fogo', title='Risco de fogo Diário')
    col1.plotly_chart(queim_dia)


    queim_estado = px.bar(df_filtered, x='estado', y='avg_risco_fogo', title='Risco de fogo por Estado')
    col1.plotly_chart(queim_estado)

    bioma_counts = df['bioma'].value_counts().reset_index()
    bioma_counts.columns = ['bioma', 'count']

    fig = px.pie(bioma_counts, names='bioma', values='count', title='Distribuição de Biomas')

    st.title('Distribuição de Biomas')
    st.plotly_chart(fig)

    st.title("Mapa de Risco de Fogo por Estado")

# Carregar o shapefile ou geojson com a geometria dos estados (exemplo: Brasil)
# Aqui usamos um GeoDataFrame com geometria fictícia. Substitua pelo caminho real para os dados.
geojson_path = "data\\br_states.json"

# Abrir o arquivo GeoJSON
with open(geojson_path) as f:
    geojson_data = json.load(f)

with col2:

    # Criar o mapa usando Plotly Express, mapear o campo 'id' do GeoJSON
    fig = px.choropleth(
        df,
        geojson=geojson_data,
        locations="estado",  # Coluna com as siglas dos estados no DataFrame
        featureidkey="properties.id",  # Mapeia com a chave 'id' do GeoJSON
        color="avg_risco_fogo",
        hover_name="estado",
        hover_data={"avg_risco_fogo": True},
        color_continuous_scale="Reds",
        labels={"avg_risco_fogo": "Risco de Fogo Médio"}
    )

    # Ajustar a visualização do mapa
    fig.update_geos(fitbounds="locations", visible=False)
    fig.update_layout(
        title="Mapa de Risco de Fogo por Estado",
        geo=dict(bgcolor='rgba(0,0,0,0)')
    )

    # Exibir o gráfico no Streamlit
    st.plotly_chart(fig)