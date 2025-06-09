import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="Histórias de Consumo", layout="wide")
st.title("Como Gastamos: Perfis, Prioridades e Padrões de Consumo no Brasil")

df = pd.read_csv('dataset_bancario_tratado.csv', sep=';', encoding='utf-8', dtype=str)
df['valor'] = df['valor'].str.replace('.', '', regex=False).str.replace(',', '.', regex=False)
df['valor'] = pd.to_numeric(df['valor'], errors='coerce')
df['data'] = pd.to_datetime(df['data'], errors='coerce')
df['mes'] = df['data'].dt.to_period('M').astype(str)
df['sexo'] = df['sexo'].map({'M': 'Masculino', 'F': 'Feminino'})
df['cliente'] = 'Cliente ' + (df.groupby('id', sort=False).ngroup() + 1).astype(str)

st.header("Quem gasta mais em...")
categorias = sorted(df['grupo_estabelecimento'].dropna().unique())
cat_escolhida = st.selectbox("Escolha uma categoria:", categorias)
df_cat = df[df['grupo_estabelecimento'] == cat_escolhida]
df_top = df_cat.groupby('cliente')['valor'].sum().reset_index().sort_values(by='valor', ascending=False).head(20)
fig1 = px.bar(df_top, x='cliente', y='valor', title=f'20 Clientes em {cat_escolhida}')
st.plotly_chart(fig1, use_container_width=True)

st.header("Homens vs. Mulheres no Consumo")
df_heat = df.groupby(['sexo', 'grupo_estabelecimento'])['valor'].sum().reset_index()
df_heat['grupo_estabelecimento'] = df_heat['grupo_estabelecimento'].astype('category')
ordem_categorias = df_heat.groupby('grupo_estabelecimento')['valor'].sum().sort_values(ascending=False).index
df_heat['grupo_estabelecimento'] = df_heat['grupo_estabelecimento'].cat.set_categories(ordem_categorias, ordered=True)

fig2 = px.density_heatmap(df_heat,
                         x='grupo_estabelecimento',
                         y='sexo',
                         z='valor',
                         color_continuous_scale='Viridis',
                         labels={'grupo_estabelecimento': 'Categoria', 'sexo': 'Sexo', 'valor': 'Total de Gastos (R$)'},
                         title='Mapa de Calor dos Gastos por Sexo e Categoria',
                         text_auto='.2s')
fig2.update_layout(xaxis_tickangle=45)
st.plotly_chart(fig2, use_container_width=True)

st.header("Perfis de Consumo")
cliente_ex = st.selectbox("Escolha um cliente:", df['cliente'].unique())
df_ex = df[df['cliente'] == cliente_ex]
df_perfil = df_ex.groupby('grupo_estabelecimento')['valor'].sum().reset_index()
fig3 = px.bar(df_perfil, x='grupo_estabelecimento', y='valor', title=f'Perfil de Consumo de {cliente_ex}')
fig3.update_layout(xaxis_tickangle=45)
st.plotly_chart(fig3, use_container_width=True)

st.markdown("---")
st.caption("Projeto de Análise de Consumo | Ana | Matheus | Rossana | Victor")