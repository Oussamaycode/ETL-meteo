import pandas as pd
import streamlit as st
import plotly.express as px

st.set_page_config(page_title='Weather Dashboard',page_icon='⛅',layout='wide')

st.title("My weather Dashboard ⛅")
st.markdown("this is my weather dashboard")

connection=st.connection('postgresql',type='sql')

df=connection.query('SELECT * FROM meteo_data',ttl="10m")


col1,col2,col3,col4,col5=st.columns(5)
col1.metric('Nombres des villes',df['city'].nunique())
col2.metric('Tempeature maximale',df['temperature_2m_max'].max())
col3.metric('Precipitation maximale',df['precipitation_sum'].max())
col4.metric('Nombre de période à risque',len(df[df['risk_score']>60]))
ville = df.loc[
    df["risk_score"].idxmax(),
    "city"
]
col5.metric('Ville avec risque max',ville)

st.sidebar.header('filters')

ville_filter= st.sidebar.selectbox(
    "Ville",
    ["Toutes"] + sorted(df["city"].unique())
)

date_filter=st.sidebar.date_input(
    "Date",
    value=None
)

risk_score_filter=st.sidebar.selectbox(
    "risk_score",
    ["Toutes"] + sorted(df['risk_score'].unique())
)

df1=df.copy()

if ville_filter!="Toutes":
    df1=df1[df1['city']==ville_filter]

if date_filter!=None:
    df1=df1[df1['date'].dt.date==date_filter]

if risk_score_filter!="Toutes":
    df1=df1[df1['risk_score']==risk_score_filter]


col_map, col_legend = st.columns([4,1])


with col_map:

    st.subheader("Risque météorologique")

    df1["color"] = df1["risk_score"].apply(
    lambda x: "#dc2626" if x >= 80
    else "#f97316" if x >= 60
    else "#eab308" if x >= 40
    else "#22c55e"
    )

    st.map(
        df1,
        latitude="latitude",
        longitude="lng",
        color="color"
    )



with col_legend:

    st.subheader("Légende")
    st.markdown("""
    🔴 **Très élevé**  
    80 - 100

    🟠 **Élevé**  
    60 - 79

    🟡 **Moyen**  
    40 - 59

    🟢 **Faible**  
    20 - 39

    🔵 **Très faible**  
    0 - 19
    """)
  
st.dataframe(df1)


df_chart = df[df["city"].isin(["Agadir", "Safi", "Casablanca"])]

fig = px.line(
    df_chart,
    x="date",
    y="risk_score",
    color="city",
    markers=True
)

fig.update_layout(
    yaxis=dict(range=[0, 100]),
    hovermode="x unified"
)



df_pie_chart=df[df["city"].isin(["Agadir", "Safi", "Casablanca"])]

fig1=px.pie(df_pie_chart,values='risk_score',names="city",
    title="Répartition du risque météorologique"
)

col_graph,col_pie=st.columns([4,2])

st.plotly_chart(fig, use_container_width=True)
st.plotly_chart(fig1, use_container_width=True)


