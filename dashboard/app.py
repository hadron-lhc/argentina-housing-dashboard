import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import sys
import os

# Agregar path para importar db_utils
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

from data.db_utils import get_all_properties, get_unique_zones, get_unique_cities

# Configuración de la página
st.set_page_config(
    page_title="Argentina Housing Dashboard", page_icon="🏠", layout="wide"
)


# Cargar datos con caching
@st.cache_data
def load_data():
    """Carga los datos de la base de datos"""
    return get_all_properties()


# Funciones helper para filtros
def get_cities_by_zone(zona):
    """Obtiene ciudades de una zona específica"""
    if zona == "Todas":
        return get_unique_cities()
    return df[df["zona"] == zona]["ciudad"].unique().tolist()


# Cargar datos
df = load_data()

# ============================================================
# HEADER - Título y Métricas
# ============================================================

st.title("🏠 Argentina Housing Dashboard")
st.markdown("Análisis del mercado inmobiliario en Buenos Aires")

# Separador
st.markdown("---")

# Métricas en 4 columnas
col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric("Total Propiedades", f"{len(df):,}")

with col2:
    st.metric("Precio Promedio", f"${df['precio'].mean():,.0f}")

with col3:
    st.metric("Área Promedio", f"{df['area'].mean():.0f} m²")

with col4:
    st.metric("Precio/m²", f"${df['precio_por_m2'].mean():,.0f}")

# Separador
st.markdown("---")

# ============================================================
# VISUALIZACIONES - 5 Gráficos
# ============================================================

st.subheader("📈 Análisis Visual del Mercado")
st.markdown("")  # Espaciado

# Primera fila: 3 gráficos
col1, col2, col3 = st.columns(3)

with col1:
    # Gráfico 1: Distribución de Precios (Histograma)
    st.markdown("**Distribución de Precios**")
    fig1 = px.histogram(
        df,
        x="precio",
        nbins=40,
        labels={"precio": "Precio (USD)"},
        color_discrete_sequence=["#636EFA"],
    )
    fig1.update_layout(showlegend=False, height=300, margin=dict(l=0, r=0, t=0, b=0))
    st.plotly_chart(fig1, use_container_width=True)

with col2:
    # Gráfico 2: Precio Promedio por Zona (Barras)
    st.markdown("**Precio Promedio por Zona**")
    precio_por_zona = df.groupby("zona")["precio"].mean().reset_index()
    precio_por_zona = precio_por_zona.sort_values("precio", ascending=False)

    fig2 = px.bar(
        precio_por_zona,
        x="zona",
        y="precio",
        labels={"zona": "Zona", "precio": "Precio Promedio (USD)"},
        color="precio",
        color_continuous_scale="Blues",
    )
    fig2.update_layout(showlegend=False, height=300, margin=dict(l=0, r=0, t=0, b=0))
    st.plotly_chart(fig2, use_container_width=True)

with col3:
    # Gráfico 3: Distribución por Zona (Pie Chart)
    st.markdown("**Propiedades por Zona**")
    propiedades_por_zona = df["zona"].value_counts().reset_index()
    propiedades_por_zona.columns = ["zona", "cantidad"]

    fig3 = px.pie(
        propiedades_por_zona,
        values="cantidad",
        names="zona",
        hole=0.4,  # Donut chart
    )
    fig3.update_layout(height=300, margin=dict(l=0, r=0, t=0, b=0))
    st.plotly_chart(fig3, use_container_width=True)

# Segunda fila: 2 gráficos (más anchos)
col4, col5 = st.columns(2)

with col4:
    # Gráfico 4: Precio vs Área (Scatter)
    st.markdown("**Relación Precio vs Área**")
    fig4 = px.scatter(
        df.sample(1000),  # Muestra de 1000 para mejor performance
        x="area",
        y="precio",
        color="zona",
        labels={"area": "Área (m²)", "precio": "Precio (USD)"},
        opacity=0.6,
    )
    fig4.update_layout(height=350, margin=dict(l=0, r=0, t=0, b=0))
    st.plotly_chart(fig4, use_container_width=True)

with col5:
    # Gráfico 5: Precio por m² por Zona (Box Plot)
    st.markdown("**Precio por m² - Distribución por Zona**")
    fig5 = px.box(
        df,
        x="zona",
        y="precio_por_m2",
        labels={"zona": "Zona", "precio_por_m2": "Precio por m² (USD)"},
        color="zona",
    )
    fig5.update_layout(showlegend=False, height=350, margin=dict(l=0, r=0, t=0, b=0))
    st.plotly_chart(fig5, use_container_width=True)

st.markdown("---")

# ============================================================
# EXPLORACIÓN DE DATOS - Filtros y Tabla
# ============================================================

st.subheader("🔍 Exploración de Datos")
st.markdown("")  # Espaciado

# Inicializar session_state si no existe
if "zona_filter" not in st.session_state:
    st.session_state.zona_filter = "Todas"
if "ciudad_filter" not in st.session_state:
    st.session_state.ciudad_filter = "Todas"

# Filtros en 4 columnas
col1, col2, col3, col4 = st.columns(4)

with col1:
    # Lista de zonas
    zonas_list = ["Todas"] + get_unique_zones()

    # Índice actual basado en session_state
    zona_index = (
        zonas_list.index(st.session_state.zona_filter)
        if st.session_state.zona_filter in zonas_list
        else 0
    )

    # Selectbox de zona
    zona_seleccionada = st.selectbox(
        "Zona", zonas_list, index=zona_index, key="selectbox_zona"
    )

    # Actualizar session_state si cambió
    if zona_seleccionada != st.session_state.zona_filter:
        st.session_state.zona_filter = zona_seleccionada
        # Si cambió la zona, resetear ciudad a "Todas"
        st.session_state.ciudad_filter = "Todas"
        st.rerun()

with col2:
    # Solo habilitar si se seleccionó una zona específica
    ciudad_habilitada = st.session_state.zona_filter != "Todas"

    if ciudad_habilitada:
        # Obtener ciudades disponibles según la zona
        ciudades_disponibles = get_cities_by_zone(st.session_state.zona_filter)
        ciudades_list = ["Todas"] + sorted(ciudades_disponibles)

        # Índice actual
        ciudad_index = (
            ciudades_list.index(st.session_state.ciudad_filter)
            if st.session_state.ciudad_filter in ciudades_list
            else 0
        )

        # Selectbox habilitado
        ciudad_seleccionada = st.selectbox(
            "Ciudad", ciudades_list, index=ciudad_index, key="selectbox_ciudad"
        )

        # Actualizar session_state si cambió
        if ciudad_seleccionada != st.session_state.ciudad_filter:
            st.session_state.ciudad_filter = ciudad_seleccionada
            st.rerun()
    else:
        # Selectbox deshabilitado
        st.selectbox(
            "Ciudad",
            ["Primero seleccione una zona"],
            disabled=True,
            key="selectbox_ciudad_disabled",
        )
        st.session_state.ciudad_filter = "Todas"

with col3:
    precio_min = st.number_input(
        "Precio Mínimo (USD)", min_value=0, max_value=2000000, value=0, step=10000
    )

with col4:
    precio_max = st.number_input(
        "Precio Máximo (USD)", min_value=0, max_value=2000000, value=2000000, step=10000
    )

# Aplicar filtros al DataFrame usando session_state
df_filtrado = df.copy()

if st.session_state.zona_filter != "Todas":
    df_filtrado = df_filtrado[df_filtrado["zona"] == st.session_state.zona_filter]

if st.session_state.ciudad_filter != "Todas":
    df_filtrado = df_filtrado[df_filtrado["ciudad"] == st.session_state.ciudad_filter]

df_filtrado = df_filtrado[
    (df_filtrado["precio"] >= precio_min) & (df_filtrado["precio"] <= precio_max)
]

# Mostrar resultados
st.info(f"📊 Mostrando **{len(df_filtrado):,}** de **{len(df):,}** propiedades")

# Tabla interactiva
st.dataframe(
    df_filtrado[
        [
            "zona",
            "ciudad",
            "precio",
            "area",
            "ambientes",
            "bathrooms",
            "precio_por_m2",
            "url",
        ]
    ],
    use_container_width=True,
    height=400,
)
