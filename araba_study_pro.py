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
    return pd.read_csv("data_araba_cleaned.csv")

df_total = cargar_datos()
df = df_total.copy()

# ==================================================
# SIDEBAR - FILTROS
# ==================================================

st.sidebar.header("Filtros")

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

# ==================================================
# KPIs
# ==================================================

st.subheader("Indicadores generales")

porcentaje = round(len(df) / len(df_total) * 100, 1)

c1, c2, c3, c4 = st.columns(4)

c1.metric("Certificados", f"{len(df):,}", f"{porcentaje}% del total")
c2.metric("Consumo medio", round(df["Consumo anual"].mean(), 1))
c3.metric("Emisiones medias", round(df["Emisiones anuales"].mean(), 1))
c4.metric("Superficie media", round(df["Superficie habitable"].mean(), 1))

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

tab1, tab2, tab3, tab4, tab5, tab6, tab7 = st.tabs([
    "📊 Resumen",
    "🏙️ Municipios",
    "📈 Consumo",
    "🏠 Tipología",
    "⚡ Energías",
    "🔍 Correlaciones",
    "📋 Datos"
])

# ==================================================
# TAB 1 - RESUMEN
# ==================================================

with tab1:

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
# TAB 2 - MUNICIPIOS
# ==================================================

with tab2:

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

# ==================================================
# TAB 3 - CONSUMO
# ==================================================

with tab3:

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
# TAB 4 - TIPOLOGÍA
# ==================================================

with tab4:

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
# TAB 5 - ENERGÍAS
# ==================================================

with tab5:

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
# TAB 6 - CORRELACIONES
# ==================================================

with tab6:

    st.subheader("Correlación entre variables")

    corr = df.select_dtypes(include="number").corr()

    st.plotly_chart(
        px.imshow(corr, text_auto=".2f"),
        use_container_width=True
    )

    st.subheader("Resumen estadístico")

    st.dataframe(
        df.select_dtypes(include="number").describe(),
        use_container_width=True
    )

# ==================================================
# TAB 7 - DATOS
# ==================================================

with tab7:

    st.subheader("Datos filtrados")

    st.dataframe(df, use_container_width=True)

    csv = df.to_csv(index=False).encode("utf-8")

    st.download_button(
        "⬇️ Descargar datos filtrados",
        csv,
        "certificados_filtrados.csv",
        "text/csv"
    )