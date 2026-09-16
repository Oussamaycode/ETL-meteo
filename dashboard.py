import streamlit as st
import pandas as pd

st.set_page_config(page_title="My Dashboard", page_icon="📊", layout="wide")


st.title("🌦️ Weather Risk Dashboard")
st.markdown("Welcome to the interactive sales overview.")   



conn = st.connection("postgresql", type="sql")


df = conn.query("SELECT * FROM gold_data;", ttl="10m")   

col1, col2, col3, col4, col5 = st.columns(5)

col1.metric("Nombre de villes", df["city"].nunique())

col2.metric(
    "Température maximale",
    f"{df['temperature_2m_max'].max()} °C"
)

col3.metric(
    "Précipitations maximales",
    f"{df['precipitation_sum'].max()} mm"
)

col4.metric(
    "Périodes à risque",
    len(df[df["risk_score"] >= 60])
)

ville = df.loc[df["risk_score"].idxmax(), "city"]

col5.metric(
    "Ville présentant le risque le plus élevé",
    ville
)

st.sidebar.header("Filtres")

# Ville
ville = st.sidebar.selectbox(
    "Ville",
    ["Toutes"] + sorted(df["city"].unique())
)

# Date
date = st.sidebar.date_input(
    "Date",
    value=None
)



niveau_risque = st.sidebar.selectbox(
    "Niveau de risque",
    ["Tous"] + sorted(df["risk_score"].unique())
)

df_filtre = df.copy()

if ville != "Toutes":
    df_filtre = df_filtre[df_filtre["city"] == ville]

if date is not None:
    df_filtre = df_filtre[df_filtre["date"].dt.date == date]


if niveau_risque != "Tous":
    df_filtre = df_filtre[
        df_filtre["risk_score"] == niveau_risque
    ]

st.dataframe(df_filtre)    