import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="Histórias de Consumo", layout="wide")
st.title("Como Gastamos: Perfis, Prioridades e Padrões de Consumo no Brasil")

st.text('Imagine que cada compra que você faz — o café da manhã na padaria, o remédio na farmácia, ou aquela passagem de avião comprada com antecedência — deixa uma pequena pista sobre quem você é. Agora imagine reunir milhões dessas pistas, anonimizadas, e organizá-las para entender um grande retrato coletivo.')
st.text("Essa é a proposta do nosso projeto: descobrir histórias por trás dos números. Usamos dados reais de transações financeiras para mapear quem gasta mais, em que tipo de estabelecimento, com que frequência, e em qual momento da vida.")
st.text("Ao longo desta análise, teremos perfis de consumidores, diferenças entre homens e mulheres, padrões por faixa etária, e até categorias de consumo com maior impacto financeiro ou social.")
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
df_top = df_cat.groupby(['cliente', 'sexo', 'idade'])['valor'].sum().reset_index().sort_values(by='valor', ascending=False).head(20)
fig1 = px.bar(df_top, x='cliente', y='valor', 
              hover_data=['sexo', 'idade'],
              title=f'Clientes em {cat_escolhida}')
st.plotly_chart(fig1, use_container_width=True)

st.header("Homens vs. Mulheres no Consumo")
df_heat = df.groupby(['sexo', 'grupo_estabelecimento'])['valor'].sum().reset_index()

# Contar quantidade de clientes por sexo
clientes_por_sexo = df.groupby('sexo')['id'].nunique().reset_index()
clientes_por_sexo.columns = ['sexo', 'total_clientes']

# Juntar para normalizar o valor
df_heat = df_heat.merge(clientes_por_sexo, on='sexo')
df_heat['valor_normalizado'] = df_heat['valor'] / df_heat['total_clientes']

# Ordenar categorias
ordem_categorias = df_heat.groupby('grupo_estabelecimento')['valor'].sum().sort_values(ascending=False).index
df_heat['grupo_estabelecimento'] = pd.Categorical(df_heat['grupo_estabelecimento'], categories=ordem_categorias, ordered=True)

fig2 = px.density_heatmap(df_heat,
                         x='grupo_estabelecimento',
                         y='sexo',
                         z='valor_normalizado',
                         color_continuous_scale='Greys',
                         labels={'grupo_estabelecimento': 'Categoria', 'sexo': 'Sexo', 'valor_normalizado': 'Gasto Médio por Cliente (R$)'},
                         title='Mapa de Calor dos Gastos Médios por Sexo e Categoria',
                         text_auto='.2s')
fig2.update_layout(xaxis_tickangle=45)
fig2.update_coloraxes(colorbar_title='Gasto Médio por Cliente (R$)')
st.plotly_chart(fig2, use_container_width=True)


st.header("Quem Gasta Mais e Onde? Uma Visão por Idade e Categoria")
filtro = df['idade'].notna() & df['grupo_estabelecimento'].notna()
df_bolha = df[filtro].copy()
df_bolha['idade'] = pd.to_numeric(df_bolha['idade'], errors='coerce').round().astype('Int64')

df_agg = df_bolha.groupby(['grupo_estabelecimento', 'idade']).agg({
    'valor': 'sum',
    'id': pd.Series.nunique
}).reset_index().rename(columns={'id': 'num_clientes'})

df_agg = df_agg[df_agg['valor'] > 0]
fig = px.scatter(
    df_agg, 
    x='valor', 
    y='idade', 
    size='num_clientes', 
    color='grupo_estabelecimento',
    labels={
        'valor': 'Total Gasto (R$)',
        'idade': 'Idade',
        'grupo_estabelecimento': 'Categoria',
        'num_clientes': 'Nº de Clientes'
    },
    title='Categorias por Idade: Gasto vs Popularidade'
)
fig.update_xaxes(
    type='log',
    tickvals=[10, 100, 1000, 10000, 100000],
    ticktext=['10', '100', '1k', '10k', '100k']
)
fig.update_xaxes(type='log')
st.plotly_chart(fig, use_container_width=True)

st.text("Cada bolha representa uma combinação entre idade e tipo de gasto: quanto maior a bolha, mais pessoas daquela idade compraram naquela categoria. E quanto mais à direita, maior foi o gasto total.")
st.text("O que vemos é que pessoas entre 30 e 50 anos concentram a maior parte das transações, tanto em volume financeiro quanto em variedade de categorias.")
st.text("Categorias como farmácias, clínicas e companhias aéreas aparecem com frequência, indicando sua presença constante no dia a dia.")
st.text("Já categorias como hotéis e joalherias, embora menos acessadas, registram valores bem mais altos quando utilizadas, principalmente por faixas etárias mais maduras.")
st.text("A escala logarítmica ajuda a evidenciar que até os pequenos gastos contam, e que mesmo transações de menor valor podem ser muito populares em determinadas idades.")

st.markdown("---")
st.caption("Projeto de Análise de Consumo | Ana | Matheus | Rossana | Victor")
