import streamlit as st
import pandas as pd
from datetime import datetime
import plotly.express as px
from supabase import create_client, Client

# --- Configuración de la Aplicación ---
st.set_page_config(
    page_title="Nancy's Collection - Sistema de Inventario",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.title("Nancy's Collection - Sistema de Gestión de Inventario")
st.markdown("""
Plataforma de consulta de inventario en tiempo real | Arquitectura Cloud-Native  
Tecnologías: Supabase (PostgreSQL) | API Gateway | Integración ERP
""")


# --- Conexión a Supabase (API REST) ---
@st.cache_resource
def init_supabase_client() -> Client:
    """Inicializa cliente de Supabase usando API REST (sin problemas de firewall)."""
    try:
        url = st.secrets["supabase"]["url"]
        key = st.secrets["supabase"]["key"]
        return create_client(url, key)
    except KeyError:
        st.error("Configuración faltante: Por favor configura st.secrets['supabase']")
        st.info("""
        Configuración requerida en .streamlit/secrets.toml:
        
        [supabase]
        url = "https://tu-proyecto.supabase.co"
        key = "tu-anon-key-aqui"
        """)
        st.info("""
        Para obtener estas credenciales:
        1. Ve a tu proyecto en Supabase
        2. Settings → API
        3. Copia 'Project URL' y 'anon/public key'
        """)
        st.stop()
    except Exception as e:
        st.error(f"Error al inicializar Supabase: {e}")
        st.stop()


supabase = init_supabase_client()


# --- Carga de Datos con Cache ---
@st.cache_data(ttl=60)
def load_catalog_data():
    """Carga el catálogo desde Supabase con TTL de 60s (simula consulta 'tiempo real' desde ERP)."""
    try:
        response = supabase.table('tb_catalogo_stock').select('*').order('modelo').order('talla').execute()
        df = pd.DataFrame(response.data)
        return df
    except Exception as e:
        st.error(f"Error al cargar catálogo: {e}")
        st.info("Verifica que la tabla 'tb_catalogo_stock' exista en Supabase y tenga datos.")
        return pd.DataFrame()


df_catalogo = load_catalog_data()

# --- Verificación de datos ---
if df_catalogo.empty:
    st.warning("No hay productos en el catálogo. Verifica la tabla tb_catalogo_stock en Supabase.")
    st.stop()

# --- Sidebar: Métricas de Negocio ---
with st.sidebar:
    st.header("Métricas de Inventario")
    
    total_productos = len(df_catalogo)
    valor_inventario = (df_catalogo['precio_soles'] * df_catalogo['stock_actual']).sum()
    productos_agotados = len(df_catalogo[df_catalogo['stock_actual'] == 0])
    productos_criticos = len(df_catalogo[df_catalogo['stock_actual'] <= 5])
    
    st.metric("Total Productos", total_productos)
    st.metric("Valor Inventario", f"S/ {valor_inventario:,.2f}")
    st.metric("Productos Agotados", productos_agotados, delta_color="inverse")
    st.metric("Stock Crítico (≤5)", productos_criticos, delta_color="inverse")
    
    st.markdown("---")
    st.markdown("**Análisis de Stock:**")
    if productos_criticos > 0:
        st.warning(f"Hay {productos_criticos} productos que requieren reabastecimiento.")
    else:
        st.success("Niveles de inventario adecuados.")

# --- Filtros Principales ---
st.markdown("---")
st.markdown("### Filtros de Búsqueda")

col1, col2, col3 = st.columns(3)

with col1:
    modelos = ['Todos'] + sorted(df_catalogo['modelo'].unique().tolist())
    modelo_seleccionado = st.selectbox('Modelo:', modelos)

with col2:
    colores = ['Todos'] + sorted(df_catalogo['color'].dropna().unique().tolist())
    color_seleccionado = st.selectbox('Color:', colores)

with col3:
    stock_minimo = st.number_input('Stock Mínimo:', min_value=0, value=0, step=1)

# Aplicar filtros
df_filtrado = df_catalogo.copy()

if modelo_seleccionado != 'Todos':
    df_filtrado = df_filtrado[df_filtrado['modelo'] == modelo_seleccionado]

if color_seleccionado != 'Todos':
    df_filtrado = df_filtrado[df_filtrado['color'] == color_seleccionado]

df_filtrado = df_filtrado[df_filtrado['stock_actual'] >= stock_minimo]

# --- Resultados ---
st.markdown("---")
st.markdown(f"### Resultados de Búsqueda: {len(df_filtrado)} productos")

if df_filtrado.empty:
    st.info("No hay productos que coincidan con los criterios de búsqueda.")
else:
    # Tabla principal
    display_df = df_filtrado[['sku', 'modelo', 'descripcion', 'talla', 'color', 'precio_soles', 'stock_actual', 'url_foto']].copy()
    display_df.columns = ['SKU', 'Modelo', 'Descripción', 'Talla', 'Color', 'Precio (S/)', 'Stock', 'Imagen']
    
    st.dataframe(
        display_df,
        use_container_width=True,
        hide_index=True,
        column_config={
            "Stock": st.column_config.ProgressColumn(
                "Stock",
                help="Unidades disponibles en almacén",
                format="%d",
                min_value=0,
                max_value=int(df_catalogo['stock_actual'].max())
            ),
            "Precio (S/)": st.column_config.NumberColumn(
                "Precio (S/)",
                format="S/ %.2f"
            ),
            "Imagen": st.column_config.LinkColumn(
                "Imagen",
                display_text="Ver"
            )
        }
    )
    
    # Alertas
    col_a, col_b = st.columns(2)
    
    with col_a:
        agotados = df_filtrado[df_filtrado['stock_actual'] == 0]
        if not agotados.empty:
            st.error(f"ALERTA: {len(agotados)} productos sin stock disponible")
    
    with col_b:
        criticos = df_filtrado[(df_filtrado['stock_actual'] > 0) & (df_filtrado['stock_actual'] <= 5)]
        if not criticos.empty:
            st.warning(f"ADVERTENCIA: {len(criticos)} productos con stock crítico (≤5 unidades)")

# --- Visualización Analytics ---
if not df_filtrado.empty:
    st.markdown("---")
    st.markdown("### Análisis de Inventario")
    
    col_chart1, col_chart2 = st.columns(2)
    
    with col_chart1:
        # Top productos por valor de inventario
        df_filtrado['valor_stock'] = df_filtrado['precio_soles'] * df_filtrado['stock_actual']
        top_valor = df_filtrado.nlargest(5, 'valor_stock')[['modelo', 'valor_stock']]
        
        fig1 = px.bar(
            top_valor, 
            x='valor_stock', 
            y='modelo',
            orientation='h',
            title='Top 5 Productos por Valor en Inventario',
            labels={'valor_stock': 'Valor (S/)', 'modelo': 'Modelo'}
        )
        st.plotly_chart(fig1, use_container_width=True)
    
    with col_chart2:
        # Distribución de stock por modelo
        stock_por_modelo = df_filtrado.groupby('modelo')['stock_actual'].sum().reset_index()
        
        fig2 = px.pie(
            stock_por_modelo,
            values='stock_actual',
            names='modelo',
            title='Distribución de Stock por Modelo'
        )
        st.plotly_chart(fig2, use_container_width=True)

# --- Footer ---
st.markdown("---")
st.caption("""
Arquitectura: Supabase (PostgreSQL) | Integración ERP | Analytics Pipeline  
Sistema desarrollado con principios Cloud-Native para escalabilidad y alta disponibilidad
""")
