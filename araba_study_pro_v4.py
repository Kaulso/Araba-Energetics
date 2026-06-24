import streamlit as st
import pandas as pd
import plotly.express as px

# ==================================================
# CONFIGURACIÓN GENERAL
# ==================================================

st.set_page_config(
    page_title="Certificados Energéticos de Álava",
    layout="wide"
)

st.title("🏠 Dashboard de Certificados Energéticos de Álava")

st.markdown(
    "Análisis interactivo de eficiencia energética de edificios en Álava."
)

# ==================================================
# CARGA DE DATOS
# ==================================================

@st.cache_data
def cargar_datos():
    df = pd.read_csv("data_araba_cleaned.csv")

    # Eliminar columnas constantes
    columnas_constantes = [
        col for col in df.columns
        if df[col].nunique(dropna=False) <= 1
    ]

    df = df.drop(columns=columnas_constantes)

    return df

df_total = cargar_datos()
df = df_total.copy()

# ==================================================
# SCORE ENERGÉTICO (0-100)
# ==================================================

def calcular_score_energetico(df):

    mapa_calificacion = {
        "A": 100,
        "B": 85,
        "C": 70,
        "D": 55,
        "E": 40,
        "F": 25,
        "G": 10
    }

    score_calificacion = (
        df["Calificación energética"]
        .map(mapa_calificacion)
        .fillna(0)
    )

    score_emisiones_calif = (
        df["Calificación energ. emisiones"]
        .map(mapa_calificacion)
        .fillna(0)
    )

    consumo_norm = (
        1 -
        (
            (df["Consumo anual"] - df["Consumo anual"].min())
            /
            (
                df["Consumo anual"].max()
                - df["Consumo anual"].min()
            )
        )
    ) * 100

    emisiones_norm = (
        1 -
        (
            (df["Emisiones anuales"] - df["Emisiones anuales"].min())
            /
            (
                df["Emisiones anuales"].max()
                - df["Emisiones anuales"].min()
            )
        )
    ) * 100

    score = (
        score_calificacion * 0.40 +
        score_emisiones_calif * 0.30 +
        consumo_norm * 0.20 +
        emisiones_norm * 0.10
    )

    return score.round(1)

df_total["Score energético"] = calcular_score_energetico(df_total)


# ==================================================
# SIDEBAR - FILTROS
# ==================================================

st.sidebar.image(
    "Escudo_alava.png",
    caption="Fuente: Gobierno Vasco",
    width=200
)

st.sidebar.header("Filtros")
st.sidebar.markdown("Donde se pueden filtrar por municipio, tipo de edificio, año de construcción y superficie habitable.")


municipios = sorted(df_total["Municipio"].dropna().unique())
municipio = st.sidebar.multiselect("Municipio", municipios)

if municipio:
    df = df[df["Municipio"].isin(municipio)]

tipos = sorted(df_total["Tipo edificio"].dropna().unique())
tipo_edificio = st.sidebar.multiselect("Tipo edificio", tipos)

if tipo_edificio:
    df = df[df["Tipo edificio"].isin(tipo_edificio)]

# Año construcción
min_year = int(df_total["Año construcción"].min())
max_year = int(df_total["Año construcción"].max())

rango = st.sidebar.slider(
    "Año construcción",
    min_year,
    max_year,
    (min_year, max_year)
)

df = df[
    (df["Año construcción"] >= rango[0]) &
    (df["Año construcción"] <= rango[1])
]

# Superficie
sup_min = int(df_total["Superficie habitable"].min())
sup_max = int(df_total["Superficie habitable"].max())

superficie = st.sidebar.slider(
    "Superficie habitable (m²)",
    sup_min,
    sup_max,
    (sup_min, sup_max)
)

df = df[
    (df["Superficie habitable"] >= superficie[0]) &
    (df["Superficie habitable"] <= superficie[1])
]

df["Score energético"] = calcular_score_energetico(df)

# ==================================================
# KPIs
# ==================================================

st.subheader("Indicadores generales")

porcentaje = round(len(df) / len(df_total) * 100, 1)

c1, c2, c3, c4, c5 = st.columns(5)

c1.metric("Certificados", f"{len(df):,}", f"{porcentaje}% del total")
c2.metric("Consumo medio", round(df["Consumo anual"].mean(), 1))
c3.metric("Emisiones medias", round(df["Emisiones anuales"].mean(), 1))
c4.metric("Superficie media", round(df["Superficie habitable"].mean(), 1))
c5.metric("Score energético", f"{df['Score energético'].mean():.1f}/100")

st.divider()

# ==================================================
# COLORES CALIFICACIÓN
# ==================================================

colores_calificacion = {
    "A": "#00A651",
    "B": "#65B32E",
    "C": "#A8C545",
    "D": "#FFD700",
    "E": "#F9A602",
    "F": "#FF6B35",
    "G": "#D62828"
}

# ==================================================
# TABS
# ==================================================

tab1, tab2, tab3, tab4, tab5, tab6, tab7, tab8, tab9 = st.tabs([
    "🏠 Menu Principal",
    "📊 Resumen",
    "🏙️ Municipios",
    "📈 Consumo",
    "🏠 Tipología",
    "⚡ Energías",
    "🔍 Correlaciones",
    "🏆 Ranking",
    "📋 Datos"
])

# ==================================================
# TAB 1 - MENU PRINCIPAL
# ==================================================

with tab1:

    st.subheader("MENU PRINCIPAL")
    st.markdown(
        """
        Bienvenido al dashboard de certificados energéticos de Álava. 
        Use los filtros en la barra lateral para explorar los datos y visualizar los indicadores clave.
        """
    )

# ==================================================
# TAB 2 - RESUMEN
# ==================================================

with tab2:

    st.subheader("Calificación energética")

    calif = df["Calificación energética"].value_counts().reset_index()
    calif.columns = ["Calificación", "Cantidad"]

    fig = px.bar(
        calif,
        x="Calificación",
        y="Cantidad",
        color="Calificación",
        color_discrete_map=colores_calificacion,
        text_auto=True
    )

    st.plotly_chart(fig, use_container_width=True)

    st.subheader("Calificación de emisiones")

    emisiones = df["Calificación energ. emisiones"].value_counts().reset_index()
    emisiones.columns = ["Calificación", "Cantidad"]

    fig = px.bar(
        emisiones,
        x="Calificación",
        y="Cantidad",
        color="Calificación",
        color_discrete_map=colores_calificacion,
        text_auto=True
    )

    st.plotly_chart(fig, use_container_width=True)

# ==================================================
# TAB 3 - MUNICIPIOS
# ==================================================

with tab3:

    st.subheader("Municipios con más certificados")

    top_n = st.slider("Número de municipios", 5, 25, 10)

    top = df["Municipio"].value_counts().head(top_n).reset_index()
    top.columns = ["Municipio", "Certificados"]

    fig = px.bar(
        top,
        x="Certificados",
        y="Municipio",
        orientation="h",
        text_auto=True
    )

    st.plotly_chart(fig, use_container_width=True)

    st.divider()

    st.subheader("Mapa interactivo de municipios")

    # Coordenadas aproximadas de municipios principales de Álava
    coords = {
        "Vitoria-Gasteiz": (42.8467, -2.6726),
        "Amurrio": (43.0526, -3.0007),
        "Laudio/Llodio": (43.1430, -2.9630),
        "Agurain/Salvatierra": (42.8500, -2.3900),
        "Alegría-Dulantzi": (42.9390, -2.5140),
        "Araia": (42.8950, -2.3130),
        "Artziniega": (43.1220, -3.1280),
        "Labastida": (42.5900, -2.7930),
        "Laguardia": (42.5540, -2.5850),
        "Oion": (42.5060, -2.4360),
        "Zuia": (42.9550, -2.8190)
    }

    mapa = (
        df.groupby("Municipio")
        .agg(
            Certificados=("Municipio", "count"),
            Consumo_Medio=("Consumo anual", "mean"),
            Emisiones_Medias=("Emisiones anuales", "mean")
        )
        .reset_index()
    )

    mapa["lat"] = mapa["Municipio"].map(
        lambda x: coords.get(x, (None, None))[0]
    )

    mapa["lon"] = mapa["Municipio"].map(
        lambda x: coords.get(x, (None, None))[1]
    )

    mapa = mapa.dropna(subset=["lat", "lon"])

    if not mapa.empty:

        fig_map = px.scatter_mapbox(
            mapa,
            lat="lat",
            lon="lon",
            size="Certificados",
            color="Consumo_Medio",
            hover_name="Municipio",
            hover_data={
                "Certificados": True,
                "Consumo_Medio": ":.1f",
                "Emisiones_Medias": ":.1f",
                "lat": False,
                "lon": False
            },
            zoom=8,
            center={
                "lat": 42.85,
                "lon": -2.68
            },
            height=650,
            mapbox_style="carto-positron"
        )

        fig_map.update_layout(
            margin=dict(l=0, r=0, t=30, b=0)
        )

        st.plotly_chart(
            fig_map,
            use_container_width=True
        )

    else:
        st.info(
            "No hay coordenadas disponibles para los municipios seleccionados."
        )

# ==================================================
# TAB 4 - CONSUMO
# ==================================================

with tab4:

    st.subheader("Consumo vs Emisiones")

    fig = px.scatter(
        df,
        x="Consumo anual",
        y="Emisiones anuales",
        color="Tipo edificio",
        size="Superficie habitable",
        hover_data=["Municipio"]
        # ❌ sin trendline para evitar dependencia statsmodels
    )

    st.plotly_chart(fig, use_container_width=True)

    st.subheader("Distribución consumo")

    st.plotly_chart(
        px.histogram(df, x="Consumo anual", nbins=40),
        use_container_width=True
    )

    st.subheader("Distribución emisiones")

    st.plotly_chart(
        px.histogram(df, x="Emisiones anuales", nbins=40),
        use_container_width=True
    )

# ==================================================
# TAB 5 - TIPOLOGÍA
# ==================================================

with tab5:

    tipos = df["Tipo edificio"].value_counts().reset_index()
    tipos.columns = ["Tipo edificio", "Cantidad"]

    st.plotly_chart(
        px.bar(tipos, x="Tipo edificio", y="Cantidad", text_auto=True),
        use_container_width=True
    )

    col1, col2 = st.columns(2)

    with col1:
        st.plotly_chart(
            px.box(df, x="Tipo edificio", y="Consumo anual"),
            use_container_width=True
        )

    with col2:
        st.plotly_chart(
            px.box(df, x="Tipo edificio", y="Emisiones anuales"),
            use_container_width=True
        )

# ==================================================
# TAB 6 - ENERGÍAS
# ==================================================

with tab6:

    calefaccion = df["Cal. Tipo Energia"].value_counts().head(10).reset_index()
    calefaccion.columns = ["Energía", "Cantidad"]

    acs = df["ACS Tipo Energia"].value_counts().head(10).reset_index()
    acs.columns = ["Energía", "Cantidad"]

    col1, col2 = st.columns(2)

    with col1:
        st.plotly_chart(
            px.pie(calefaccion, names="Energía", values="Cantidad"),
            use_container_width=True
        )

    with col2:
        st.plotly_chart(
            px.pie(acs, names="Energía", values="Cantidad"),
            use_container_width=True
        )

# ==================================================
# TAB 7 - CORRELACIONES
# ==================================================

with tab7:

    st.subheader("Correlación entre variables")

    numericas = df.select_dtypes(include="number")

    # Eliminar variables sin variabilidad
    numericas = numericas.loc[
        :,
        numericas.nunique() > 1
    ]

    corr = numericas.corr()

    fig = px.imshow(
        corr,
        text_auto=".2f",
        aspect="auto",
        color_continuous_scale="Blues"
    )

    fig.update_layout(
        height=800,
        xaxis_title="",
        yaxis_title=""
    )

    st.plotly_chart(
        fig,
        use_container_width=True
    )

    st.subheader("Resumen estadístico")

    st.dataframe(
        numericas.describe(),
        use_container_width=True
    )

    st.subheader("Variables incluidas")

    st.write(list(numericas.columns))

# ==================================================
# TAB 8 - RANKING ENERGÉTICO
# ==================================================

with tab8:

    st.subheader("Ranking energético")

    ranking = (
        df.groupby("Municipio")
        .agg(
            Score=("Score energético", "mean"),
            Certificados=("Municipio", "count"),
            Consumo=("Consumo anual", "mean"),
            Emisiones=("Emisiones anuales", "mean")
        )
        .reset_index()
        .sort_values("Score", ascending=False)
    )

    st.plotly_chart(
        px.bar(
            ranking.head(20),
            x="Score",
            y="Municipio",
            orientation="h",
            color="Score",
            text_auto=".1f",
            color_continuous_scale="RdYlGn"
        ),
        use_container_width=True
    )

    st.dataframe(
        ranking.round(2),
        use_container_width=True
    )

# ==================================================
# TAB 9 - DATOS
# ==================================================

with tab9:

    st.subheader("Datos filtrados")

    st.dataframe(df, use_container_width=True)

    csv = df.to_csv(index=False).encode("utf-8")

    st.download_button(
        "⬇️ Descargar datos filtrados",
        csv,
        "certificados_filtrados.csv",
        "text/csv"
    )
