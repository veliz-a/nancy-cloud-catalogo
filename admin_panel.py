import streamlit as st
import pandas as pd
from datetime import datetime
import plotly.express as px
from supabase import create_client, Client

# --- Configuración de la Aplicación ---
st.set_page_config(
    page_title="Admin - Nancy's Collection",
    layout="wide",
    initial_sidebar_state="expanded",
    page_icon="👗"
)

# --- Sistema de Autenticación Simple ---
def check_password():
    """Verifica contraseña de administrador."""
    def password_entered():
        """Callback cuando se ingresa la contraseña."""
        try:
            admin_password = st.secrets["auth"]["admin_password"]
        except KeyError:
            admin_password = "admin123"  # Fallback
        
        if st.session_state["password"] == admin_password:
            st.session_state["password_correct"] = True
            del st.session_state["password"]  # No almacenar contraseña
        else:
            st.session_state["password_correct"] = False

    if "password_correct" not in st.session_state:
        # Primera vez, mostrar input
        st.markdown("""
        <div style='max-width: 450px; margin: 100px auto; padding: 50px; 
                    background: white; border-radius: 15px; box-shadow: 0 8px 30px rgba(0,0,0,0.12);
                    border: 1px solid #E5E5E5;'>
            <div style='text-align: center; margin-bottom: 30px;'>
                <div style='font-family: "Playfair Display", serif; font-style: italic; 
                            font-size: 36px; color: #1A1A1A; letter-spacing: 2px;'>
                    Nancy's Collection
                </div>
                <div style='font-family: "Lato", sans-serif; font-size: 14px; color: #666; 
                            letter-spacing: 2px; margin-top: 10px;'>
                    PANEL DE ADMINISTRACIÓN
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        st.text_input(
            "Contraseña", 
            type="password", 
            on_change=password_entered, 
            key="password",
            placeholder="Ingresa la contraseña de administrador"
        )
        st.info("🔑 Ingresa tu contraseña de administrador")
        return False
    elif not st.session_state["password_correct"]:
        # Contraseña incorrecta
        st.text_input(
            "Contraseña", 
            type="password", 
            on_change=password_entered, 
            key="password",
            placeholder="Ingresa la contraseña de administrador"
        )
        st.error("😕 Contraseña incorrecta")
        return False
    else:
        # Contraseña correcta
        return True

if not check_password():
    st.stop()

# --- Configuración de la Aplicación (después de auth) ---

# CSS personalizado - Estética elegante Nancy's Collection
st.markdown("""
<style>
    /* Forzar tema claro */
    [data-testid="stAppViewContainer"] {
        background-color: #FAFAFA;
    }
    
    /* Fuentes elegantes */
    @import url('https://fonts.googleapis.com/css2?family=Playfair+Display:ital,wght@0,400;0,600;1,400;1,600&family=Lato:wght@300;400;600&display=swap');
    
    body, p, div, span, label {
        font-family: 'Lato', sans-serif;
        color: #2C2C2C;
    }
    
    h1, h2, h3, h4 {
        font-family: 'Playfair Display', serif;
        font-style: italic;
        color: #1A1A1A;
        letter-spacing: 1px;
    }
    
    /* Product cards elegantes */
    .product-card {
        border: 1px solid #E5E5E5;
        border-radius: 12px;
        padding: 20px;
        margin: 10px 0;
        background: white;
        box-shadow: 0 2px 10px rgba(0,0,0,0.06);
        transition: all 0.3s;
    }
    .product-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 12px 30px rgba(0,0,0,0.12);
        border-color: #1A1A1A;
    }
    
    /* Metric cards con estética Nancy's */
    .metric-card {
        background: linear-gradient(135deg, #1A1A1A 0%, #2C2C2C 100%);
        padding: 25px;
        border-radius: 12px;
        color: white;
        text-align: center;
        box-shadow: 0 4px 15px rgba(0,0,0,0.15);
    }
    
    /* Price tag elegante */
    .price-tag {
        font-family: 'Playfair Display', serif;
        font-size: 28px;
        font-weight: 600;
        color: #1A1A1A;
        letter-spacing: 0.5px;
    }
    
    /* Stock badges */
    .stock-badge {
        display: inline-block;
        padding: 6px 14px;
        border-radius: 20px;
        font-weight: 500;
        font-size: 11px;
        letter-spacing: 0.5px;
    }
    .stock-ok { 
        background: #E8F5E9; 
        color: #2E7D32; 
        border: 1px solid #A5D6A7;
    }
    .stock-low { 
        background: #FFF3E0; 
        color: #E65100; 
        border: 1px solid #FFCC80;
    }
    .stock-out { 
        background: #FFEBEE; 
        color: #C62828; 
        border: 1px solid #EF9A9A;
    }
    
    /* Botones elegantes */
    .stButton button {
        background: white !important;
        color: #1A1A1A !important;
        border: 2px solid #1A1A1A !important;
        border-radius: 25px !important;
        padding: 10px 24px !important;
        font-weight: 600 !important;
        letter-spacing: 1px !important;
        font-family: 'Lato', sans-serif !important;
        font-style: normal !important;
    }
    .stButton button:hover {
        background: #1A1A1A !important;
        color: white !important;
        transform: translateY(-2px);
        box-shadow: 0 6px 20px rgba(0,0,0,0.2) !important;
    }
    
    /* Botón primary (seleccionado) - fondo negro, letra blanca */
    .stButton button[kind="primary"] {
        background: #1A1A1A !important;
        color: #FFFFFF !important;
        border: 2px solid #1A1A1A !important;
    }
    
    .stButton button[kind="primary"]:hover {
        background: #000000 !important;
        color: #FFFFFF !important;
    }
    
    /* Forzar texto blanco en botones primary */
    .stButton button[kind="primary"] p {
        color: #FFFFFF !important;
    }
    
    /* Botón secondary */
    .stButton button[kind="secondary"] {
        background: white !important;
        color: #1A1A1A !important;
        border: 2px solid #E5E5E5 !important;
    }
    
    /* Tabs elegantes */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
        border-bottom: 2px solid #E5E5E5;
    }
    .stTabs [data-baseweb="tab"] {
        font-family: 'Lato', sans-serif;
        font-weight: 500;
        padding: 12px 24px;
        color: #666;
    }
    .stTabs [aria-selected="true"] {
        color: #1A1A1A;
        border-bottom: 3px solid #1A1A1A;
    }
    
    /* Selectbox y dropdowns con fondo blanco */
    [data-baseweb="select"] > div {
        background-color: #FFFFFF !important;
        border: 1px solid #E5E5E5 !important;
        font-family: 'Lato', sans-serif !important;
    }
    
    [role="listbox"] {
        background-color: #FFFFFF !important;
    }
    
    [role="option"] {
        background-color: #FFFFFF !important;
        color: #2C2C2C !important;
    }
    
    [role="option"]:hover {
        background-color: #F8F8F8 !important;
    }
    
    /* Sidebar con fondo blanco */
    [data-testid="stSidebar"] {
        background-color: #FFFFFF !important;
    }
    
    [data-testid="stSidebar"] > div:first-child {
        background-color: #FFFFFF !important;
    }
</style>
""", unsafe_allow_html=True)

# --- Header elegante ---
st.markdown("""
<div style='text-align: center; padding: 30px 0 20px 0;'>
    <div style='font-family: "Playfair Display", serif; font-style: italic; 
                font-size: 42px; color: #1A1A1A; letter-spacing: 2px;'>
        Nancy's Collection
    </div>
    <div style='font-family: "Lato", sans-serif; font-size: 12px; color: #666; 
                letter-spacing: 2px; margin-top: 5px;'>
        PANEL DE ADMINISTRACIÓN • GESTIÓN DE INVENTARIO
    </div>
</div>
<hr style='border: none; border-top: 1px solid #E5E5E5; margin: 20px 0;'>
""", unsafe_allow_html=True)

# Inicializar estado de navegación
if 'current_view' not in st.session_state:
    st.session_state.current_view = 'inventario'


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

# --- Sidebar: Navegación y Métricas ---
with st.sidebar:
    st.markdown("""
    <div style='text-align: center; padding: 20px 0; border-bottom: 2px solid #E5E5E5;'>
        <div style='font-family: "Playfair Display", serif; font-style: italic; 
                    font-size: 24px; color: #1A1A1A;'>
            Nancy's Collection
        </div>
        <div style='font-family: "Lato", sans-serif; font-size: 10px; color: #666; 
                    letter-spacing: 1px; margin-top: 5px;'>
            PANEL DE ADMINISTRACIÓN
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Botones de navegación
    if st.button("INVENTARIO", use_container_width=True, type="primary" if st.session_state.current_view == 'inventario' else "secondary"):
        st.session_state.current_view = 'inventario'
        st.rerun()
    
    if st.button("ANALYTICS", use_container_width=True, type="primary" if st.session_state.current_view == 'analytics' else "secondary"):
        st.session_state.current_view = 'analytics'
        st.rerun()
    
    st.markdown("---")
    
    # Métricas rápidas
    st.markdown("### Resumen Rápido")
    
    total_productos = len(df_catalogo)
    valor_inventario = (df_catalogo['precio_soles'] * df_catalogo['stock_actual']).sum()
    productos_agotados = len(df_catalogo[df_catalogo['stock_actual'] == 0])
    productos_criticos = len(df_catalogo[df_catalogo['stock_actual'] <= 5])
    
    st.metric("Total Productos", total_productos)
    st.metric("Valor Inventario", f"S/ {valor_inventario:,.2f}")
    st.metric("Productos Agotados", productos_agotados, delta_color="inverse")
    st.metric("Stock Crítico (≤5)", productos_criticos, delta_color="inverse")
    
    if productos_criticos > 0:
        st.warning(f"Hay {productos_criticos} productos que requieren reabastecimiento.")
    else:
        st.success("Niveles de inventario adecuados.")
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    if st.button("CERRAR SESIÓN", use_container_width=True):
        st.session_state["password_correct"] = False
        st.rerun()

# --- Filtros Principales ---
st.markdown("---")
st.markdown("### Filtros de Búsqueda")

col1, col2, col3, col4 = st.columns(4)

with col1:
    modelos = ['Todos'] + sorted(df_catalogo['modelo'].unique().tolist())
    modelo_seleccionado = st.selectbox('Modelo:', modelos)

with col2:
    colores = ['Todos'] + sorted(df_catalogo['color'].dropna().unique().tolist())
    color_seleccionado = st.selectbox('Color:', colores)

with col3:
    stock_minimo = st.number_input('Stock Mínimo:', min_value=0, value=0, step=1)

with col4:
    vista = st.selectbox('Vista:', ['Galería', 'Tabla'])

# --- Vista según navegación ---
if st.session_state.current_view == 'analytics':
    # VISTA DE ANALYTICS
    st.markdown("---")
    st.markdown("### Análisis de Inventario")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown("""
        <div class='metric-card'>
            <h3 style='margin:0; color: white;'>PRODUCTOS</h3>
            <h1 style='margin:10px 0; color: white;'>{}</h1>
        </div>
        """.format(len(df_catalogo)), unsafe_allow_html=True)
    
    with col2:
        valor_total = (df_catalogo['precio_soles'] * df_catalogo['stock_actual']).sum()
        st.markdown("""
        <div class='metric-card'>
            <h3 style='margin:0; color: white;'>VALOR INVENTARIO</h3>
            <h1 style='margin:10px 0; color: white;'>S/ {:.0f}</h1>
        </div>
        """.format(valor_total), unsafe_allow_html=True)
    
    with col3:
        stock_total = df_catalogo['stock_actual'].sum()
        st.markdown("""
        <div class='metric-card'>
            <h3 style='margin:0; color: white;'>STOCK TOTAL</h3>
            <h1 style='margin:10px 0; color: white;'>{}</h1>
        </div>
        """.format(stock_total), unsafe_allow_html=True)
    
    with col4:
        agotados = len(df_catalogo[df_catalogo['stock_actual'] == 0])
        st.markdown("""
        <div class='metric-card' style='background: linear-gradient(135deg, #DC3545 0%, #C62828 100%);'>
            <h3 style='margin:0; color: white;'>AGOTADOS</h3>
            <h1 style='margin:10px 0; color: white;'>{}</h1>
        </div>
        """.format(agotados), unsafe_allow_html=True)
    
    # Gráficos
    st.markdown("<br>", unsafe_allow_html=True)
    
    col_g1, col_g2 = st.columns(2)
    
    with col_g1:
        # Stock por modelo
        stock_por_modelo = df_catalogo.groupby('modelo')['stock_actual'].sum().reset_index()
        fig1 = px.bar(stock_por_modelo, x='modelo', y='stock_actual', 
                      title='Stock por Modelo',
                      labels={'stock_actual': 'Unidades', 'modelo': 'Modelo'})
        fig1.update_traces(marker_color='#1A1A1A')
        st.plotly_chart(fig1, use_container_width=True)
    
    with col_g2:
        # Valor por modelo
        df_catalogo['valor'] = df_catalogo['precio_soles'] * df_catalogo['stock_actual']
        valor_por_modelo = df_catalogo.groupby('modelo')['valor'].sum().reset_index()
        fig2 = px.pie(valor_por_modelo, values='valor', names='modelo',
                      title='Valor de Inventario por Modelo')
        st.plotly_chart(fig2, use_container_width=True)
    
    st.stop()

# VISTA DE INVENTARIO (por defecto)
# Aplicar filtros
df_filtrado = df_catalogo.copy()

if modelo_seleccionado != 'Todos':
    df_filtrado = df_filtrado[df_filtrado['modelo'] == modelo_seleccionado]

if color_seleccionado != 'Todos':
    df_filtrado = df_filtrado[df_filtrado['color'] == color_seleccionado]

df_filtrado = df_filtrado[df_filtrado['stock_actual'] >= stock_minimo]

# --- Resultados ---
st.markdown("---")
st.markdown(f"### Resultados: {len(df_filtrado)} productos encontrados")

if df_filtrado.empty:
    st.info("No hay productos que coincidan con los criterios de búsqueda. Intenta ajustar los filtros.")
else:
    # Alertas (antes de mostrar productos)
    col_a, col_b = st.columns(2)
    
    with col_a:
        agotados = df_filtrado[df_filtrado['stock_actual'] == 0]
        if not agotados.empty:
            st.error(f"ALERTA: {len(agotados)} productos sin stock disponible")
    
    with col_b:
        criticos = df_filtrado[(df_filtrado['stock_actual'] > 0) & (df_filtrado['stock_actual'] <= 5)]
        if not criticos.empty:
            st.warning(f"ADVERTENCIA: {len(criticos)} productos con stock crítico (≤5 unidades)")
    
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
