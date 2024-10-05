import streamlit as st
import requests
import pandas as pd
import plotly.express as px

st.set_page_config(layout='wide')

def formatar_numero(valor, prefixo = ''):
    for unidade in ['', 'mil']:
        if valor <1000:
            return f'{prefixo} {valor: .2f} {unidade}'
        valor /= 1000
    return f'{prefixo} {valor: .2f} milhão'   

st.title('DASHBOARD DE VENDAS :shopping_trolley:')

url = 'https://labdados.com/produtos'

regioes = ['Brasil', 'Centro-Oeste', 'Nordeste' ,'Norte', 'Sudeste', 'Sul' ]

st.sidebar.title('Filtros')

regiao = st.sidebar.selectbox('Reigião', regioes)

if regioes == 'Brasil':
    regiao = ''

todos_anos = st.sidebar.checkbox('Dados de todo o período', value = True)

if todos_anos:
    ano = ''
else:
    ano = st.sidebar.slider('Ano', 2020, 2023)

query_string = {'região': regiao.lower, 'ano': ano}
#Armazenar os dados da url (respons)

response = requests.get(url, params = query_string)

# Transformando um requisicao em json 
dados = pd.DataFrame.from_dict(response.json())
ddados = pd.DataFrame.from_dict(response.json())

dados['Data da Compra'] = pd.to_datetime(dados['Data da Compra'], format = '%d/%m/%Y')

filtro_vendedores = st.sidebar.multiselect('Vendedores', dados['Vendedor'].unique())
if filtro_vendedores:
    dados = dados[dados['Vendedor'].isin(filtro_vendedores)]

##Tabelas
###Tabelas de Receitas
receita_estados = dados.groupby('Local da compra')[['Preço']].sum()

receita_estados = dados.drop_duplicates(subset = 'Local da compra')[['Local da compra', 'lat', 'lon']].merge(receita_estados, left_on = 'Local da compra', right_index = True).sort_values('Preço', ascending= False)
receita_mensal = dados.set_index('Data da Compra').groupby(pd.Grouper(freq='M'))['Preço'].sum().reset_index()
receita_mensal ['Ano'] = receita_mensal ['Data da Compra'].dt.year
receita_mensal ['Mes'] = receita_mensal ['Data da Compra']. dt.month_name()

receita_categoria = dados.groupby('Categoria do Produto')[['Preço']].sum().sort_values('Preço', ascending= False)

###Tabelas de quantidade de vendas
vendas_estados = pd.DataFrame(dados.groupby('Local da compra')['Preço'].count())
vendas_estados = dados.drop_duplicates(subset = 'Local da compra')[['Local da compra','lat', 'lon']].merge(vendas_estados, left_on = 'Local da compra', right_index = True).sort_values('Preço', ascending = False)

vendas_mensal = pd.DataFrame(dados.set_index('Data da Compra').groupby(pd.Grouper(freq = 'M'))['Preço'].count()).reset_index()
vendas_mensal['Ano'] = vendas_mensal['Data da Compra'].dt.year
vendas_mensal['Mes'] = vendas_mensal['Data da Compra'].dt.month_name()

vendas_categorias = pd.DataFrame(dados.groupby('Categoria do Produto')['Preço'].count().sort_values(ascending = False))

### Tabelas vendedores 
vendedores = pd.DataFrame(dados.groupby('Vendedor')['Preço'].agg(['sum', 'count']))

## Gráficos
fig_mapa_receita = px.scatter_geo(receita_estados,
                                   lat = 'lat',
                                   lon = 'lon',
                                   scope = 'south america',
                                   size = 'Preço',
                                   template = 'seaborn',
                                   hover_name = 'Local da compra',
                                   hover_data = {'lat':False,'lon':False},
                                   title = 'Receita por Estado')

fig_recieta_mensal = px.line(receita_mensal,
                             x= 'Mes',
                             y= 'Preço',
                             markers= True,
                             range_y= (0, receita_mensal.max()),
                             color= 'Ano',
                             line_dash= 'Ano',
                             title= 'Receita mensal')

fig_recieta_mensal.update_layout(yaxis_title = 'Receita')

fig_receita_estados = px.bar(receita_estados.head(),
                             x = 'Local da compra',
                             y = 'Preço',
                             text_auto = True,
                             title = 'Top estados (receitas)')

fig_receita_estados.update_layout(yaxis_title = 'Recita')

fig_receita_categora = px.bar(receita_categoria,
                              text_auto = True,
                              title ='Recita por categoria')

fig_receita_categora.update_layout(yaxis_title = 'Recita')


fig_mapa_vendas = px.scatter_geo(vendas_estados, 
                     lat = 'lat', 
                     lon= 'lon', 
                     scope = 'south america', 
                     #fitbounds = 'locations', 
                     template='seaborn', 
                     size = 'Preço', 
                     hover_name ='Local da compra', 
                     hover_data = {'lat':False,'lon':False},
                     title = 'Vendas por estado',
                     )

fig_vendas_mensal = px.line(vendas_mensal, 
              x = 'Mes',
              y='Preço',
              markers = True, 
              range_y = (0,vendas_mensal.max()), 
              color = 'Ano', 
              line_dash = 'Ano',
              title = 'Quantidade de vendas mensal')

fig_vendas_mensal.update_layout(yaxis_title='Quantidade de vendas')

fig_vendas_estados = px.bar(vendas_estados.head(),
                             x ='Local da compra',
                             y = 'Preço',
                             text_auto = True,
                             title = 'Top 5 estados'
)

fig_vendas_estados.update_layout(yaxis_title='Quantidade de vendas')

fig_vendas_categorias = px.bar(vendas_categorias, 
                                text_auto = True,
                                title = 'Vendas por categoria')
fig_vendas_categorias.update_layout(showlegend=False, yaxis_title='Quantidade de vendas')



## Vizualizacao no streamlit

aba1, aba2, aba3 = st.tabs (['Recita', 'Quantidade de vendas', 'Vendedor'])
with aba1:
    coluna1, coluna2 = st.columns(2)

    with coluna1:
        st.metric('Receita', formatar_numero (dados['Preço'].sum(), 'R$'))
        st.plotly_chart(fig_mapa_receita, use_container_width= True)
        st.plotly_chart(fig_receita_estados, use_container_width= True)

    with coluna2:
                                    #Quantidade de linhas e colunas do dataframe 
        st.metric('Quantidade de vendas', formatar_numero (dados.shape[0]))
        st.plotly_chart(fig_recieta_mensal, use_container_width= True)
        st.plotly_chart(fig_receita_categora, use_container_width= True)

with aba2:
    coluna1, coluna2 = st.columns(2)
    with coluna1:
        st.metric('Receita', formatar_numero (dados['Preço'].sum(), 'R$'))

    with coluna2:
                                    #Quantidade de linhas e colunas do dataframe 
        st.metric('Quantidade de vendas', formatar_numero (dados.shape[0]))
        st.plotly_chart(fig_vendas_mensal, use_container_width = True)
        st.plotly_chart(fig_vendas_categorias, use_container_width = True)
with aba3:

    qtd_vendedores = st.number_input('Quantidade de vendedor', 2, 10, 5)
    coluna1, coluna2 = st.columns(2)

    with coluna1:
        st.metric('Receita', formatar_numero (dados['Preço'].sum(), 'R$'))
        fig_receita_vendedores = px.bar(vendedores[['sum']].sort_values('sum', ascending = False).head(qtd_vendedores),
                                        x = 'sum',
                                        y = (vendedores[['sum']].sort_values('sum', ascending = False).head(qtd_vendedores).index),
                                        text_auto = True,
                                        title = f'Top {qtd_vendedores} vendedors (receita)')
        st.plotly_chart(fig_receita_vendedores)
    with coluna2:
        st.metric('Receita', formatar_numero (dados['Preço'].sum(), 'R$'))
        fig_vendas_vendedores = px.bar(vendedores[['count']].sort_values('count', ascending = False).head(qtd_vendedores),
                                        x = 'count',
                                        y = vendedores[['count']].sort_values('count', ascending = False).head(qtd_vendedores).index,
                                        text_auto = True,
                                        title = f'Top {qtd_vendedores} vendedors (quantidade de vendas)'
                                        )
        st.plotly_chart(fig_vendas_vendedores)
                                    #Quantidade de linhas e colunas do dataframe 
        st.metric('Quantidade de vendas', formatar_numero (dados.shape[0]))



##st.dataframe(dados)