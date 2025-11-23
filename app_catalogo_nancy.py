import streamlit as st
import pandas as pd
from datetime import datetime
import plotly.express as px
from supabase import create_client, Client

# --- Configuración de la Aplicación ---
st.set_page_config(
    page_title="Nancy's Collection - Sistema de Inventario",
    layout="wide",
    initial_sidebar_state="expanded",
    page_icon="👗"
)

# CSS personalizado para mejorar la apariencia
st.markdown("""
<style>
    .product-card {
        border: 1px solid #e0e0e0;
        border-radius: 10px;
        padding: 15px;
        margin: 10px 0;
        background: white;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        transition: transform 0.2s;
    }
    .product-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 4px 8px rgba(0,0,0,0.2);
    }
    .metric-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 20px;
        border-radius: 10px;
        color: white;
        text-align: center;
    }
    .price-tag {
        font-size: 24px;
        font-weight: bold;
        color: #667eea;
    }
    .stock-badge {
        display: inline-block;
        padding: 5px 10px;
        border-radius: 5px;
        font-weight: bold;
        font-size: 12px;
    }
    .stock-ok { background-color: #4caf50; color: white; }
    .stock-low { background-color: #ff9800; color: white; }
    .stock-out { background-color: #f44336; color: white; }
    
    /* Mejorar título principal */
    h1 {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
    }
</style>
""", unsafe_allow_html=True)

st.title("👗 Nancy's Collection - Catálogo Digital")
st.markdown("""
<div style='background: linear-gradient(90deg, #667eea 0%, #764ba2 100%); padding: 15px; border-radius: 10px; color: white; margin-bottom: 20px;'>
    <b>Plataforma Cloud-Native</b> • Inventario en Tiempo Real • Integración ERP TumiSoft
</div>
""", unsafe_allow_html=True)


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
st.markdown("### 🔍 Filtros de Búsqueda")

col1, col2, col3, col4 = st.columns(4)

with col1:
    modelos = ['Todos'] + sorted(df_catalogo['modelo'].unique().tolist())
    modelo_seleccionado = st.selectbox('📦 Modelo:', modelos)

with col2:
    colores = ['Todos'] + sorted(df_catalogo['color'].dropna().unique().tolist())
    color_seleccionado = st.selectbox('🎨 Color:', colores)

with col3:
    stock_minimo = st.number_input('📊 Stock Mínimo:', min_value=0, value=0, step=1)

with col4:
    vista = st.selectbox('👁️ Vista:', ['Galería', 'Tabla'])

# Aplicar filtros
df_filtrado = df_catalogo.copy()

if modelo_seleccionado != 'Todos':
    df_filtrado = df_filtrado[df_filtrado['modelo'] == modelo_seleccionado]

if color_seleccionado != 'Todos':
    df_filtrado = df_filtrado[df_filtrado['color'] == color_seleccionado]

df_filtrado = df_filtrado[df_filtrado['stock_actual'] >= stock_minimo]

# --- Resultados ---
st.markdown("---")
st.markdown(f"### 📦 Resultados: {len(df_filtrado)} productos encontrados")

if df_filtrado.empty:
    st.info("🔍 No hay productos que coincidan con los criterios de búsqueda. Intenta ajustar los filtros.")
else:
    # Alertas (antes de mostrar productos)
    col_a, col_b = st.columns(2)
    
    with col_a:
        agotados = df_filtrado[df_filtrado['stock_actual'] == 0]
        if not agotados.empty:
            st.error(f"⚠️ ALERTA: {len(agotados)} productos sin stock disponible")
    
    with col_b:
        criticos = df_filtrado[(df_filtrado['stock_actual'] > 0) & (df_filtrado['stock_actual'] <= 5)]
        if not criticos.empty:
            st.warning(f"🔔 ADVERTENCIA: {len(criticos)} productos con stock crítico (≤5 unidades)")
    
    st.markdown("")  # Espacio
    
    # Vista según selección
    if vista == 'Galería':
        # Vista de galería con cards
        cols = st.columns(3)
        for idx, row in df_filtrado.iterrows():
            with cols[idx % 3]:
                # Determinar estado del stock
                if row['stock_actual'] == 0:
                    stock_class = "stock-out"
                    stock_text = "AGOTADO"
                elif row['stock_actual'] <= 5:
                    stock_class = "stock-low"
                    stock_text = f"BAJO STOCK ({row['stock_actual']})"
                else:
                    stock_class = "stock-ok"
                    stock_text = f"DISPONIBLE ({row['stock_actual']})"
                
                # Card del producto
                with st.container():
                    # Imagen
                    if pd.notna(row['url_foto']) and row['url_foto']:
                        st.image(row['url_foto'], use_container_width=True)
                    else:
                        st.markdown("""
                        <div style='background: linear-gradient(135deg, #e0e0e0 0%, #f5f5f5 100%); 
                                    height: 200px; display: flex; align-items: center; 
                                    justify-content: center; border-radius: 10px;'>
                            <span style='font-size: 48px;'>📷</span>
                        </div>
                        """, unsafe_allow_html=True)
                    
                    # Información del producto
                    st.markdown(f"**{row['modelo']}**")
                    st.markdown(f"<span class='price-tag'>S/ {row['precio_soles']:.2f}</span>", unsafe_allow_html=True)
                    
                    col_info1, col_info2 = st.columns(2)
                    with col_info1:
                        st.caption(f"🎨 {row['color']}")
                    with col_info2:
                        st.caption(f"📏 {row['talla']}")
                    
                    st.markdown(f"<span class='stock-badge {stock_class}'>{stock_text}</span>", unsafe_allow_html=True)
                    
                    # Expandible con más detalles
                    with st.expander("Ver detalles"):
                        st.write(f"**SKU:** {row['sku']}")
                        st.write(f"**Descripción:** {row['descripcion']}")
                        if pd.notna(row['url_foto']) and row['url_foto']:
                            st.markdown(f"[🔗 Ver imagen completa]({row['url_foto']})")
                
                st.markdown("")  # Espacio entre cards
    
    else:
        # Vista de tabla con imágenes como miniaturas
        display_df = df_filtrado[['url_foto', 'sku', 'modelo', 'talla', 'color', 'precio_soles', 'stock_actual']].copy()
        display_df.columns = ['Imagen', 'SKU', 'Modelo', 'Talla', 'Color', 'Precio (S/)', 'Stock']
        
        st.dataframe(
            display_df,
            use_container_width=True,
            hide_index=True,
            column_config={
                "Imagen": st.column_config.ImageColumn(
                    "Foto",
                    help="Imagen del producto",
                    width="small"
                ),
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
                )
            },
            height=600
        )

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
st.markdown("""
<div style='text-align: center; padding: 20px; color: #666;'>
    <p><b>Nancy's Collection</b> - Sistema de Gestión de Inventario Cloud-Native</p>
    <p style='font-size: 12px;'>
        🔧 Supabase (PostgreSQL) | 🔗 API REST | 📊 Analytics | ⚡ Real-time sync con ERP TumiSoft
    </p>
    <p style='font-size: 11px; color: #999;'>
        Desarrollado con Streamlit • Deploy-ready para Streamlit Cloud
    </p>
</div>
""", unsafe_allow_html=True)
