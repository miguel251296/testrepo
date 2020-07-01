import pandas as pd
import plotly.graph_objects as go
import plotly.subplots as pxs
import plotly.express as px
import numpy as np
from datetime import date


dadoscorona = pd.DataFrame(pd.read_csv('Pacientes_compilados_csv_BORB.csv',
                                       sep=';',
                                       encoding='ISO 8859-1',
                                       index_col=0))
dadoscorona.columns = dadoscorona.columns.str.strip()
dadoscorona.reset_index(drop=True,
                        inplace=True)
dadosrsd = dadoscorona.copy()
dadosrsd['Bairro'] = dadosrsd['Bairro'].str.strip()

# Trocando os nomes de bairros e informações faltando
dadosrsd["Bairro"] = dadosrsd['Bairro'].fillna('Residência não informada')
dadosrsd.loc[dadosrsd['Bairro'] == 'Não Identificado','Bairro'] = 'Residência não informada'

dadoscoord = pd.DataFrame(pd.read_csv('coord-borb.csv')).drop_duplicates()
dadosrsd = dadosrsd.merge(dadoscoord, how='left', on='Bairro')

# Borborema Sexo
dadosrsd['Sexo'] = dadosrsd['Sexo'].str.strip()
dadosrsd['Sexo'] = dadosrsd['Sexo'].str.upper()
dadosrsd['Sexo'] = dadosrsd['Sexo'].apply(lambda x: x[0])

dadosrsd["Status"] = dadosrsd["Status"].fillna("Status não informado")
dadosrsd_obito = dadosrsd[dadosrsd["Status"].str.contains("bito", case=False)]

sexo = dadosrsd.groupby('Sexo').count()['Data de confirmação(testes)']
mortesexo = dadosrsd_obito.groupby('Sexo').count()['Status']
dadosrsd_sexo = pd.DataFrame({'Número de casos': sexo, 'Número de mortes': mortesexo})

dadosrsd_sexo['Sexo'] = dadosrsd_sexo.index
dadosrsd_sexo.reset_index(drop=True, inplace=True)

dadosrsd_sexo['Sexo'].replace(to_replace=['F', 'M'], value=["Mulher", 'Homem'], inplace=True)

# Borborema Bairro - Confirmed/Dead
casosbairro = dadosrsd.groupby('Bairro').count()['Data de confirmação(testes)']
curasbairro = dadosrsd.loc[dadosrsd['Status']=='Curado'].groupby('Bairro').count()['Status']
mortebairro = dadosrsd_obito.groupby('Bairro').count()['Status']
dadosrsd_bairro = pd.DataFrame({'Número de casos': casosbairro, 'Número de mortes': mortebairro,
                                'Número de curados':curasbairro})
dadosrsd_bairro['Bairro'] = dadosrsd_bairro.index
dadosrsd_bairro.reset_index(drop=True, inplace=True)

dadosrsd_bairro = dadosrsd_bairro.merge(dadoscoord, how='left', on='Bairro')
dadosrsd_bairro["Número de mortes"] = dadosrsd_bairro['Número de mortes'].fillna('0')
dadosrsd_bairro["Número de curados"] = dadosrsd_bairro['Número de curados'].fillna('0')

# Borborema - Cases and Deaths
for i in range(len(dadosrsd['Data de confirmação(testes)'])):
    if dadosrsd.loc[i, 'Data de confirmação(testes)'] == "FILL_VALUE":
        dadosrsd.loc[i, 'Data de confirmação(testes)'] = dadosrsd.loc[i-1, 'Data de confirmação(testes)']
        


df_teste = pd.DataFrame(
    dadosrsd.groupby(
        pd.to_datetime(
            dadosrsd['Data de confirmação(testes)'], 
            dayfirst=True)
    ).count()[['Data de confirmação(testes)']]).sort_index()

df_mortes = pd.DataFrame(
    dadosrsd_obito.groupby(
        pd.to_datetime(
            dadosrsd_obito['Óbito(data)'], 
            dayfirst=True)
    ).count()[['Óbito(data)']]).sort_index()


df_teste['Data'] = df_teste.index
df_mortes['Data'] = df_mortes.index

idx = pd.date_range(start = df_teste['Data'].iloc[0], 
                    end = date.today())

df_teste = df_teste.reindex(idx, fill_value=0)
df_mortes = df_mortes.reindex(idx, fill_value=0)

df_teste['Número de casos'] = 0
df_mortes['Número de mortes'] = 0

for x in range(len(df_teste)):
    if x == 0:
        df_teste['Número de casos'][x] = df_teste['Data de confirmação(testes)'][x]
    else:
        df_teste['Número de casos'][x] = df_teste['Data de confirmação(testes)'][x] + df_teste['Número de casos'][x-1]

for x in range(len(df_mortes)):
    if x == 0:
        df_mortes['Número de mortes'][x] = df_mortes['Óbito(data)'][x]
    else:
        df_mortes['Número de mortes'][x] = df_mortes['Óbito(data)'][x] + df_mortes['Número de mortes'][x-1]


# Age Group - Figure
df_masculino= dadosrsd[dadosrsd['Sexo']=='M'].fillna(0)
df_feminino= dadosrsd[dadosrsd['Sexo']=='F'].fillna(0)
df_desconhecido = dadosrsd[dadosrsd['Sexo'] == 'Desconhecido'].fillna(0)

df_masculino_ob= dadosrsd_obito[dadosrsd_obito['Sexo']=='M'].fillna(0)
df_feminino_ob= dadosrsd_obito[dadosrsd_obito['Sexo']=='F'].fillna(0)
df_desconhecido_ob = dadosrsd_obito[dadosrsd_obito['Sexo'] == 'Desconhecido'].fillna(0)

def cont(df):
    limits= [(0, 0),
             (1, 10),
             (11, 20),
             (21, 30),
             (31, 40),
             (41, 50),
             (51, 60),
             (61, 70),
             (71, 80),
             (81, 110)]
    soma = 0
    tabela = []
    for x in range(len(limits)):
        lim = limits[x]
        for i in range(len(df)):
            if lim[0] <= int(df.iloc[i, 3]) <= lim[1]:
                soma += 1
        tabela.append(soma)
        soma = 0
    return tabela

def contmorte(df):
    limits= [(0, 0),
             (1, 10),
             (11, 20),
             (21, 30),
             (31, 40),
             (41, 50),
             (51, 60),
             (61, 70),
             (71, 80),
             (81, 110)]
    soma = 0
    tabela = []
    for x in range(len(limits)):
        lim = limits[x]
        for i in range(len(df)):
            if lim[0] <= int(df.iloc[i, 3]) <= lim[1]:
                soma += 1
        tabela.append(soma)
        soma = 0
    return tabela

dado_homem = cont(df_masculino)
dado_mulher = cont(df_feminino)
dado_desconhecido = cont(df_desconhecido)

dado_morte_homem = contmorte(df_masculino_ob)
dado_morte_mulher = contmorte(df_feminino_ob)
dado_morte_desconhecido = contmorte(df_desconhecido_ob)

faixas=['0','1-10','11-20','21-30','31-40','41-50','51-60','61-70','71-80','+80']

agegroup = pxs.make_subplots(rows=1,
                             cols=2,
                             specs=[[{"type": "bar"},
                                     {"type": "bar"}]],
                             subplot_titles=['Nº de Casos',
                                             'Nº de Óbitos']
                             )

agegroup.add_trace(go.Bar(y=faixas,
                          x=dado_mulher,
                          name='Mulher',
                          orientation='h',
                          marker=dict(color='white',
                                      line=dict(color='black',
                                                width=1)),
                          text=dado_mulher,
                          textposition='auto',
                          textangle=0,
                          outsidetextfont={"color":"black"}),
                   row=1,
                   col=1)

agegroup.add_trace(go.Bar(y=faixas,
                          x=dado_homem,
                          name='Homem',
                          orientation='h',
                          marker=dict(color='black',
                                      line=dict(color='black',
                                                width=1)),
                          text=dado_homem,
                          textposition='auto',
                          textangle=0,
                          outsidetextfont={"color":"black"}),
                   row=1, col=1)

if dado_desconhecido != [0,0,0,0,0,0,0,0,0,0]:
    agegroup.add_trace(go.Bar(y=faixas,
                              x=dado_desconhecido,
                              name='Desconhecido',
                              orientation='h',
                              marker=dict(color='lightblue',
                                          line=dict(color='lightblue',
                                                    width=1)),
                              text=dado_desconhecido,
                              textposition='auto',
                              textangle=0,
                              outsidetextfont={"color":"black"}),
                       row=1,
                       col=1)

# Grafico numero de morte
#agegroup.add_trace(go.Bar(x=dado_morte_mulher,
#                          name='Mulher',
#                          orientation='h',
#                          marker=dict(color='white',
#                                      line=dict(color='black',
#                                                width=1)),
#                          showlegend=False,
#                          text=dado_morte_mulher,
#                          textposition='auto',
#                          textangle=0,
#                          outsidetextfont={"color":"black"}),
#                   row=1,
#                   col=2)

#agegroup.add_trace(go.Bar(x=dado_morte_homem,
#                          name='Homem',
##                          orientation='h',
#                         marker=dict(color='black',
#                                     line=dict(color='black',
#                                                width=1)),
#                          showlegend=False,
#                          text=dado_morte_homem,
#                          textposition='auto',
#                          textangle=0,
#                          outsidetextfont={"color":"black"}),
#                   row=1,
#                   col=2)

#if dado_morte_desconhecido != [0,0,0,0,0,0,0,0,0,0]:
#    agegroup.add_trace(go.Bar( x=dado_morte_desconhecido,
#                               name='Homem',
#                               orientation='h',
#                               marker=dict(color='lightblue',
#                                           line=dict(color='lightblue',
#                                                     width=3)),
#                               showlegend=False,
#                               text=dado_morte_desconhecido,
#                               textposition='auto',
#                               textangle=0,
#                               outsidetextfont={"color":"black"}),
#                       row=1,
#                       col=2)

# Atualização gráfico
agegroup.update_traces(textfont_size=12,
                       hoverinfo='x+name')

agegroup.update_layout(plot_bgcolor='rgba(105, 105, 105, 0)',
                       paper_bgcolor='lightgrey',
                       legend=dict(x=1,
                                   y=1.2,
                                   font=dict(color='white', size=15)),
                       showlegend=False,
                       annotations=[{'showarrow': False,
                                     'y':1,
                                     "font": {"color":'black',
                                              'size': 13}}],
                       barmode='stack',
                       margin=dict(b=10, t=30, r=30, l=80),
                       hovermode='y unified',
                       hoverlabel=dict(bgcolor="#EBEBEB"),
                       height=250-36)

agegroup.update_xaxes(color='black',
                      showgrid=True,
                      gridwidth=1,
                      gridcolor='dimgrey')
agegroup.update_yaxes(color='black',
                      row=1,
                      col=1,
                      title='Idade',)
agegroup.update_yaxes(color='black',
                      visible=False,
                      row=1,
                      col=2)

# Pie - SEXO
piegraph = pxs.make_subplots(rows=1,
                             cols=2,
                             specs=[[{"type": "domain"},
                                     {"type": "domain"}]],
                             subplot_titles=['Número de Casos',
                                             'Número de Óbitos'])

piegraph.add_trace(go.Pie(labels=dadosrsd_sexo['Sexo'],
                          values=dadosrsd_sexo['Número de casos'],
                          hoverinfo='label+value',
                          textposition='inside',
                          textinfo='percent+label',
                          hole=.2),
                   row=1,
                   col=1)

piegraph.add_trace(go.Pie(labels=dadosrsd_sexo['Sexo'],
                          values=dadosrsd_sexo['Número de mortes'],
                          hoverinfo='label+value',
                          textposition='inside',
                          textinfo='percent+label',
                          hole=.2),
                   row=1,
                   col=2)

piegraph.update_traces(textfont_size=12,
                       marker=dict(colors=['White',
                                           'Black',
                                           'Lightgrey'],
                                   line = dict(color='#000000', width=0.5)))

piegraph.update_layout(paper_bgcolor='dimgrey',
                       showlegend=True,
                       height=250-36,
                       legend_orientation="h",
                       legend=dict(x=.5,
                                   y=-.1,
                                   xanchor="center",
                                   font=dict(color='white',
                                             size=15)),
                       annotations=[{'showarrow': False,
                                     'y':1,
                                     "font": {"color":'white',
                                              'size': 12}}],
                       margin=dict(l=10,r=10,b=20,t=30))
# Time Series - BAR
fig1 = go.Figure()
fig2 = pxs.make_subplots(rows=1,
                         cols=2,
                         subplot_titles=("Em Cada Dia",
                                         'Acumulado'))

# Seção criação dos objetos de gráficos:
                                    #--------Casos Gerais--------#
casos1= go.Bar(x=df_teste.index,
                      y=(df_teste['Data de confirmação(testes)']),
                      name='Nº de Casos Diários',
                      hovertemplate='%{y}<br>Nº de casos acumulados até este dia: %{customdata}',
                      text=(df_teste['Data de confirmação(testes)']),
                      textposition='outside',
                      textangle=0,
                      customdata=df_teste['Número de casos'],
                      marker_color="#0582FF",
                      visible=True)

casos2= go.Bar(x=df_teste.index,
                      y=df_teste['Número de casos'],
                      name='Nº Acumulado de Casos',
                      hovertemplate='%{y}<br>Nº de casos do dia: %{customdata}',
                      text=df_teste['Número de casos'],
                      textposition='outside',
                      textangle=0,
                      customdata=df_teste['Data de confirmação(testes)'],
                      marker_color="#0582FF",
                      visible=True)
fig2.append_trace(casos1, 1, 1)
fig2.append_trace(casos2, 1, 2)
                                    #--------Óbitos--------#
mortes1=go.Bar(x=df_mortes.index,
                      y=df_mortes['Óbito(data)'],
                      name='Número de Óbitos do Dia',
                      hovertemplate='%{y}<br>Nº de óbitos acumulados até este dia: %{customdata}',
                      text=df_mortes['Óbito(data)'],
                      textposition='outside',
                      textangle=0,
                      customdata=df_mortes['Número de mortes'],
                      marker_color="#E81313",
                      visible=False)

mortes2= go.Bar(x=df_mortes.index,
                      y=df_mortes['Número de mortes'],
                      name='Número de Óbitos',
                      hovertemplate='%{y}<br>Nº de Óbitos do dia: %{customdata}',
                      text=df_mortes['Número de mortes'],
                      textposition='outside',
                      textangle=0,
                      customdata=df_mortes["Óbito(data)"],
                      marker_color="#E81313",
                      visible=False)
fig2.append_trace(mortes1, 1, 1)
fig2.append_trace(mortes2, 1, 2)

                                   
#                                      **BOTÕES**
buttons = []
labels= ["Casos Notificados",
         "Óbitos",
         # 'PCR',
         # 'Teste Rápido',
         # "Teste não identificado"
         ]
titulos=['Acompanhamento de casos por dia','Número de Óbitos']

for i,label,titulo in zip(range(0,len(fig2.data),2),labels,titulos):
    visibility=[False]*len(fig2.data)
    visibility[i]=True
    visibility[i+1]=True
    button = dict(
                 label =  label,
                 method = 'update',
                 args = [{'visible': visibility},
                     {'title': titulo}])
    buttons.append(button)

updatemenus = list([
    dict(type="dropdown",
         direction="down",
         active=0, x=0.5, y=1.057, xanchor='center', yanchor="middle",
         buttons=buttons
    )
])
#                                       **LAYOUT**
fig2.update_layout(updatemenus=updatemenus,
                   margin=dict(b=50, t=93, r=40, l=40),
                   title='Acompanhamento de COVID-19',
                   paper_bgcolor='lightgrey',
                   plot_bgcolor='rgba(250, 250, 250, 0.3)',
                   showlegend=False,
                   yaxis_title= "Número de pessoas",
                   hovermode='x unified',
                   height=250)
fig2.update(layout=dict(title=dict(x=0.505, y=.97),
                        xaxis=dict(fixedrange=True)))

mapa = px.scatter_mapbox(dadosrsd_bairro,
                         lat='lat',
                         lon='long',
                         hover_data=['Número de casos',
                                     'Número de mortes',
                                     'Número de curados'],
                         hover_name='Bairro',
                         zoom=11.5,
                         size='Número de casos',
                         size_max=40,
                         height=250,
                         center=dict(lat=-21.6222,
                                     lon=-49.0786))

mapa.data[0].hovertemplate='<b>%{hovertext}</b><br><br>Número de casos=%{customdata[0]}<br>Número de mortes=%{customdata[1]}<br>Número de curados=%{customdata[2]}<extra></extra>'

mapa.update_layout(mapbox_style='dark',
                   mapbox_accesstoken='pk.eyJ1IjoibWF0aGV1c2dhbGhhbm8iLCJhIjoiY2s5YWozZmZyMjQyazNkcGdqZXlzajFraSJ9.mQwhayrKhADgig-Y1MKwSA',
                   margin={"r":0,"t":0,"l":0,"b":0},
                   coloraxis_showscale=False)
