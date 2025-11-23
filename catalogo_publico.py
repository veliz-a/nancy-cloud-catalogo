"""
Catálogo Público - Nancy's Collection
Aplicación elegante para clientes con estética inspirada en el logo cursivo
"""

import streamlit as st
import pandas as pd
from datetime import datetime
from supabase import create_client, Client

# --- Configuración ---
st.set_page_config(
    page_title="Nancy's Collection",
    layout="wide",
    initial_sidebar_state="collapsed",
    page_icon="🖤"
)

# --- CSS Elegante (Black & White, cursivo, femenino) ---
st.markdown("""
<style>
    /* Forzar tema claro */
    [data-testid="stAppViewContainer"] {
        background-color: #FAFAFA;
    }
    [data-testid="stHeader"] {
        background-color: #FFFFFF;
    }
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    
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
    
    /* Carrito flotante - siempre visible */
    .floating-cart {
        position: fixed;
        top: 120px;
        right: 30px;
        z-index: 999;
        background: #1A1A1A;
        color: #FFFFFF !important;
        padding: 20px;
        border-radius: 15px;
        box-shadow: 0 8px 30px rgba(0,0,0,0.25);
        cursor: pointer;
        transition: all 0.3s;
        min-width: 180px;
        text-align: center;
    }
    .floating-cart:hover {
        transform: translateY(-5px);
        box-shadow: 0 12px 40px rgba(0,0,0,0.35);
    }
    .floating-cart * {
        color: #FFFFFF !important;
    }
    .cart-icon {
        font-size: 36px;
        margin-bottom: 10px;
    }
    .cart-total-float {
        font-family: 'Playfair Display', serif;
        font-size: 22px;
        font-weight: 600;
        margin: 10px 0;
        color: #FFFFFF !important;
    }
    
    /* Product cards */
    .product-card {
        background: white;
        border: 1px solid #E5E5E5;
        border-radius: 12px;
        padding: 0;
        overflow: hidden;
        transition: all 0.3s;
        box-shadow: 0 2px 10px rgba(0,0,0,0.06);
    }
    .product-card:hover {
        transform: translateY(-8px);
        box-shadow: 0 12px 30px rgba(0,0,0,0.12);
        border-color: #1A1A1A;
    }
    
    /* Contenedor de imagen estandarizado */
    .product-img-container {
        width: 100%;
        height: 380px;
        overflow: hidden;
        display: flex;
        align-items: center;
        justify-content: center;
        background: #F8F8F8;
    }
    .product-img-container img {
        width: 100%;
        height: 100%;
        object-fit: cover;
    }
    
    /* Precio elegante */
    .price-tag {
        font-family: 'Playfair Display', serif;
        font-size: 28px;
        font-weight: 600;
        color: #1A1A1A;
        letter-spacing: 0.5px;
    }
    
    /* Badge de stock */
    .stock-badge {
        display: inline-block;
        padding: 6px 14px;
        border-radius: 20px;
        font-size: 11px;
        font-weight: 500;
        letter-spacing: 0.5px;
        margin: 8px 0;
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
    
    /* Botones elegantes */
    .stButton button {
        background: white !important;
        color: #1A1A1A !important;
        border: 2px solid #1A1A1A !important;
        border-radius: 25px !important;
        padding: 12px 28px !important;
        font-weight: 600 !important;
        letter-spacing: 1.2px !important;
        transition: all 0.3s !important;
        font-family: 'Playfair Display', serif !important;
        font-style: italic !important;
        font-size: 14px !important;
    }
    .stButton button:hover {
        background: #1A1A1A !important;
        color: white !important;
        transform: translateY(-2px);
        box-shadow: 0 8px 25px rgba(0,0,0,0.2) !important;
    }
    
    /* Botón de agregar al carrito - destacado */
    .stButton button[kind="primary"] {
        background: #1A1A1A !important;
        color: #FFFFFF !important;
        border: 2px solid #1A1A1A !important;
        font-style: normal !important;
        letter-spacing: 1px !important;
        font-family: 'Lato', sans-serif !important;
    }
    .stButton button[kind="primary"]:hover {
        background: #000000 !important;
        border-color: #000000 !important;
        color: #FFFFFF !important;
    }
    
    /* Forzar color blanco en todos los textos del botón primary */
    .stButton button[kind="primary"] p {
        color: #FFFFFF !important;
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
    
    /* Selectbox y inputs elegantes */
    .stSelectbox label, .stNumberInput label {
        font-family: 'Lato', sans-serif !important;
        font-weight: 500 !important;
        color: #2C2C2C !important;
        font-size: 14px !important;
    }
    
    /* Dropdown menus con fondo blanco */
    [data-baseweb="select"] > div {
        background-color: #FFFFFF !important;
        border: 1px solid #E5E5E5 !important;
        font-family: 'Lato', sans-serif !important;
    }
    
    /* Opciones del dropdown */
    [role="listbox"] {
        background-color: #FFFFFF !important;
        font-family: 'Lato', sans-serif !important;
    }
    
    [role="option"] {
        background-color: #FFFFFF !important;
        font-family: 'Lato', sans-serif !important;
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
    
    /* Input numbers */
    input[type="number"] {
        font-family: 'Lato', sans-serif !important;
        background-color: white !important;
        border: 1px solid #E5E5E5 !important;
        color: #1A1A1A !important;
    }
    
    /* Botones de incremento/decremento en inputs numéricos */
    button[kind="icon"] {
        background-color: #1A1A1A !important;
        color: white !important;
        border: 1px solid #1A1A1A !important;
        font-family: 'Lato', sans-serif !important;
        font-style: normal !important;
        font-weight: 600 !important;
    }
    
    button[kind="icon"]:hover {
        background-color: #000000 !important;
        color: white !important;
    }
    
    /* Botones pequeños (+ y -) en el carrito */
    div[data-testid="stNumberInput"] button {
        background-color: #1A1A1A !important;
        color: #FFFFFF !important;
        border: 1px solid #1A1A1A !important;
        border-radius: 6px !important;
        font-family: 'Lato', sans-serif !important;
        font-style: normal !important;
        font-weight: 700 !important;
        font-size: 18px !important;
        min-width: 40px !important;
        height: 40px !important;
        line-height: 1 !important;
    }
    
    div[data-testid="stNumberInput"] button:hover {
        background-color: #000000 !important;
        color: #FFFFFF !important;
        transform: scale(1.05);
    }
    
    /* Input de cantidad - centrado y más grande */
    div[data-testid="stNumberInput"] input {
        text-align: center !important;
        font-size: 16px !important;
        font-weight: 600 !important;
        height: 40px !important;
    }
    
    /* Botones con borde - estilo secundario */
    .stButton button[kind="secondary"] {
        background: white !important;
        color: #DC3545 !important;
        border: 2px solid #DC3545 !important;
        font-family: 'Lato', sans-serif !important;
        font-style: normal !important;
        font-weight: 600 !important;
        letter-spacing: 1px !important;
    }
    .stButton button[kind="secondary"]:hover {
        background: #DC3545 !important;
        color: white !important;
    }
    
    /* Botón de eliminar individual (X) */
    .stButton button[key^="del_"] {
        background: white !important;
        color: #DC3545 !important;
        border: 2px solid #DC3545 !important;
        border-radius: 50% !important;
        width: 44px !important;
        height: 44px !important;
        padding: 0 !important;
        font-family: 'Arial', sans-serif !important;
        font-style: normal !important;
        font-weight: 700 !important;
        font-size: 20px !important;
        line-height: 1 !important;
        display: flex !important;
        align-items: center !important;
        justify-content: center !important;
    }
    
    .stButton button[key^="del_"]:hover {
        background: #DC3545 !important;
        color: #FFFFFF !important;
        transform: scale(1.1) !important;
    }
    
    /* Success messages */
    .stSuccess {
        background-color: #E8F5E9 !important;
        color: #2E7D32 !important;
        font-family: 'Lato', sans-serif !important;
        border-left: 4px solid #2E7D32 !important;
    }
    
    /* Warning messages */
    .stWarning {
        background-color: #FFF3E0 !important;
        color: #E65100 !important;
        font-family: 'Lato', sans-serif !important;
    }
    
    /* Caption text */
    .stCaption {
        font-family: 'Lato', sans-serif !important;
        color: #666 !important;
    }
</style>
""", unsafe_allow_html=True)

# --- Session State: Carrito ---
if 'carrito' not in st.session_state:
    st.session_state.carrito = []

# --- Conexión Supabase ---
@st.cache_resource
def init_supabase():
    try:
        url = st.secrets["supabase"]["url"]
        key = st.secrets["supabase"]["key"]
        return create_client(url, key)
    except Exception as e:
        st.error(f"Error de conexión: {e}")
        st.stop()

supabase = init_supabase()

# --- Funciones del Carrito ---
def agregar_al_carrito(producto):
    for item in st.session_state.carrito:
        if item['sku'] == producto['sku']:
            if item['cantidad'] < producto['stock_actual']:
                item['cantidad'] += 1
            return
    st.session_state.carrito.append({
        'sku': producto['sku'],
        'modelo': producto['modelo'],
        'color': producto['color'],
        'talla': producto['talla'],
        'precio': producto['precio_soles'],
        'cantidad': 1,
        'stock_disponible': producto['stock_actual'],
        'imagen': producto.get('url_foto')
    })

def calcular_total():
    return sum(item['precio'] * item['cantidad'] for item in st.session_state.carrito)

def generar_mensaje_whatsapp():
    if not st.session_state.carrito:
        return ""
    mensaje = "🖤 *Nuevo Pedido - Nancy's Collection*\n\n"
    for item in st.session_state.carrito:
        mensaje += f"• {item['modelo']}\n"
        mensaje += f"  Color: {item['color']} | Talla: {item['talla']}\n"
        mensaje += f"  {item['cantidad']} x S/ {item['precio']:.2f}\n\n"
    total = calcular_total()
    mensaje += f"💰 *TOTAL: S/ {total:.2f}*\n\n"
    mensaje += "Confirmar disponibilidad y coordinar entrega 🚚"
    return mensaje

# --- Cargar Productos ---
@st.cache_data(ttl=300)
def load_productos():
    try:
        response = supabase.table('tb_catalogo_stock')\
            .select('*')\
            .gt('stock_actual', 0)\
            .order('modelo')\
            .execute()
        return pd.DataFrame(response.data)
    except Exception as e:
        st.error(f"Error: {e}")
        return pd.DataFrame()

# ========== HEADER CON LOGO ==========
st.markdown("""
<div style='display: flex; align-items: center; justify-content: center; padding: 20px 0; gap: 20px;'>
    <img src='data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNk+M9QDwADhgGAWjR9awAAAABJRU5ErkJggg==' 
         style='width: 100px; height: auto;' 
         onerror="this.style.display='none';"
         onload="this.src='logo/logoNancy\'s Collection.jpg';" />
    <div style='text-align: center;'>
        <div style='font-family: \"Playfair Display\", serif; font-style: italic; 
                    font-size: 42px; color: #1A1A1A; letter-spacing: 2px; margin: 0;'>
            Nancy's Collection
        </div>
        <div style='font-family: \"Lato\", sans-serif; font-size: 12px; color: #666; 
                    letter-spacing: 2px; margin-top: 5px;'>
            MODA FEMENINA • ELEGANCIA PERUANA
        </div>
    </div>
</div>
<hr style='border: none; border-top: 1px solid #E5E5E5; margin: 20px 0;'>
""", unsafe_allow_html=True)

# ========== CARRITO FLOTANTE ==========
if len(st.session_state.carrito) > 0:
    total_items = len(st.session_state.carrito)
    total_precio = calcular_total()
    
    # Generar JavaScript para cambiar a la segunda tab
    st.markdown(f"""
    <div class='floating-cart' id='floating-cart-btn'>
        <div class='cart-icon'>🛒</div>
        <div style='font-weight: 600; font-size: 15px; font-family: "Lato", sans-serif;'>{total_items} productos</div>
        <div class='cart-total-float'>S/ {total_precio:.2f}</div>
        <div style='font-size: 11px; color: #CCC; margin-top: 8px; font-family: "Lato", sans-serif;'>VER CARRITO</div>
    </div>
    
    <script>
        document.addEventListener('DOMContentLoaded', function() {{
            const cartBtn = document.getElementById('floating-cart-btn');
            if (cartBtn) {{
                cartBtn.addEventListener('click', function() {{
                    const tabs = parent.document.querySelectorAll('[data-baseweb="tab"]');
                    if (tabs.length > 1) {{
                        tabs[1].click();
                    }}
                }});
            }}
        }});
        
        // Backup: intentar cada segundo durante 5 segundos
        let attempts = 0;
        const interval = setInterval(function() {{
            const cartBtn = document.getElementById('floating-cart-btn');
            if (cartBtn && !cartBtn.hasAttribute('data-listener')) {{
                cartBtn.setAttribute('data-listener', 'true');
                cartBtn.addEventListener('click', function() {{
                    const tabs = parent.document.querySelectorAll('[data-baseweb="tab"]');
                    if (tabs.length > 1) {{
                        tabs[1].click();
                    }}
                }});
                clearInterval(interval);
            }}
            attempts++;
            if (attempts > 5) clearInterval(interval);
        }}, 1000);
    </script>
    """, unsafe_allow_html=True)

# ========== TABS: CATÁLOGO / CARRITO ==========
tab1, tab2 = st.tabs([
    "🛍️ Catálogo",
    f"🛒 Mi Carrito ({len(st.session_state.carrito)})"
])

# ========== TAB 1: CATÁLOGO ==========
with tab1:
    df = load_productos()
    
    if df.empty:
        st.warning("No hay productos disponibles.")
        st.stop()
    
    # Filtros
    st.markdown("""
    <div style='font-family: "Playfair Display", serif; font-style: italic; 
                font-size: 32px; color: #1A1A1A; margin: 30px 0 20px 0; text-align: center;'>
        Explora Nuestra Colección
    </div>
    """, unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns(3)
    with col1:
        modelos = ['Todos'] + sorted(df['modelo'].unique().tolist())
        modelo_filtro = st.selectbox('🏷️ Tipo de Prenda', modelos, key='modelo_filter')
    with col2:
        colores = ['Todos'] + sorted(df['color'].dropna().unique().tolist())
        color_filtro = st.selectbox('🎨 Color', colores, key='color_filter')
    with col3:
        tallas = ['Todos'] + sorted(df['talla'].dropna().unique().tolist())
        talla_filtro = st.selectbox('📏 Talla', tallas, key='talla_filter')
    
    # Aplicar filtros
    df_filtrado = df.copy()
    if modelo_filtro != 'Todos':
        df_filtrado = df_filtrado[df_filtrado['modelo'] == modelo_filtro]
    if color_filtro != 'Todos':
        df_filtrado = df_filtrado[df_filtrado['color'] == color_filtro]
    if talla_filtro != 'Todos':
        df_filtrado = df_filtrado[df_filtrado['talla'] == talla_filtro]
    
    st.markdown(f"""
    <div style='text-align: center; padding: 20px; font-size: 15px; color: #666;'>
        <b style='color: #1A1A1A; font-size: 18px;'>{len(df_filtrado)}</b> productos disponibles
    </div>
    """, unsafe_allow_html=True)
    
    # Galería - 3 columnas
    cols = st.columns(3)
    
    for idx, (_, prod) in enumerate(df_filtrado.iterrows()):
        with cols[idx % 3]:
            # Imagen con tamaño fijo 380px
            if pd.notna(prod['url_foto']) and prod['url_foto']:
                st.markdown(f"""
                <div class='product-img-container'>
                    <img src='{prod['url_foto']}' alt='{prod['modelo']}' 
                         onerror="this.onerror=null; this.parentElement.innerHTML='<div style=\\'font-size:80px; color:#CCC;\\'>📷</div>';">
                </div>
                """, unsafe_allow_html=True)
            else:
                st.markdown("""
                <div class='product-img-container'>
                    <div style='font-size: 80px; color: #CCC;'>📷</div>
                </div>
                """, unsafe_allow_html=True)
            
            # Info
            st.markdown(f"""
            <div style='padding: 20px;'>
                <div style='font-family: "Playfair Display", serif; font-style: italic; 
                            font-size: 20px; color: #1A1A1A; margin-bottom: 8px;'>
                    {prod['modelo']}
                </div>
                <div class='price-tag'>S/ {prod['precio_soles']:.2f}</div>
                <div style='font-size: 13px; color: #666; margin: 10px 0;'>
                    {prod['color']} • Talla {prod['talla']}
                </div>
            </div>
            """, unsafe_allow_html=True)
            
            # Stock badge
            if prod['stock_actual'] <= 3:
                st.markdown(f"<center><span class='stock-badge stock-low'>Últimas {prod['stock_actual']} unidades</span></center>", unsafe_allow_html=True)
            else:
                st.markdown(f"<center><span class='stock-badge stock-ok'>En stock</span></center>", unsafe_allow_html=True)
            
            # Botón
            if st.button("AGREGAR AL CARRITO", key=f"add_{prod['sku']}", use_container_width=True, type="primary"):
                agregar_al_carrito(prod)
                st.success(f"✓ {prod['modelo']} agregado")
                st.rerun()
            
            st.markdown("<br>", unsafe_allow_html=True)

# ========== TAB 2: CARRITO ==========
with tab2:
    if not st.session_state.carrito:
        st.markdown("""
        <div style='text-align: center; padding: 100px 20px;'>
            <div style='font-size: 100px;'>🛒</div>
            <div style='font-family: "Playfair Display", serif; font-style: italic; 
                        font-size: 32px; color: #1A1A1A; margin: 20px 0;'>
                Tu carrito está vacío
            </div>
            <div style='color: #666;'>Descubre nuestras piezas únicas</div>
        </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown("""
        <div style='font-family: "Playfair Display", serif; font-style: italic; 
                    font-size: 32px; color: #1A1A1A; margin-bottom: 30px;'>
            Resumen de tu Pedido
        </div>
        """, unsafe_allow_html=True)
        
        # Items del carrito
        for idx, item in enumerate(st.session_state.carrito):
            # Contenedor con padding uniforme
            st.markdown("<div style='padding: 10px 0;'>", unsafe_allow_html=True)
            
            col1, col2, col3, col4, col5 = st.columns([1, 3, 1.3, 1.2, 0.7])
            
            with col1:
                if item.get('imagen'):
                    st.image(item['imagen'], width=80)
                else:
                    st.markdown("<div style='font-size: 50px; text-align: center; line-height: 80px;'>📦</div>", unsafe_allow_html=True)
            
            with col2:
                st.markdown("<div style='padding-top: 8px;'>", unsafe_allow_html=True)
                st.markdown(f"<div style='font-family: \"Playfair Display\", serif; font-style: italic; font-size: 18px; color: #1A1A1A; font-weight: 600; margin-bottom: 5px;'>{item['modelo']}</div>", unsafe_allow_html=True)
                st.markdown(f"<div style='font-family: \"Lato\", sans-serif; font-size: 13px; color: #666;'>{item['color']} • Talla {item['talla']}</div>", unsafe_allow_html=True)
                st.markdown(f"<div style='font-family: \"Lato\", sans-serif; font-size: 12px; color: #999; margin-top: 5px;'>S/ {item['precio']:.2f} c/u</div>", unsafe_allow_html=True)
                st.markdown("</div>", unsafe_allow_html=True)
            
            with col3:
                st.markdown("<div style='padding-top: 4px;'>", unsafe_allow_html=True)
                nueva_cant = st.number_input(
                    "Cantidad",
                    min_value=1,
                    max_value=item['stock_disponible'],
                    value=item['cantidad'],
                    key=f"qty_{idx}",
                    label_visibility="collapsed"
                )
                if nueva_cant != item['cantidad']:
                    st.session_state.carrito[idx]['cantidad'] = nueva_cant
                    st.rerun()
                st.markdown("</div>", unsafe_allow_html=True)
            
            with col4:
                st.markdown(f"<div style='font-family: \"Playfair Display\", serif; font-size: 24px; font-weight: 600; color: #1A1A1A; padding-top: 20px;'>S/ {item['precio'] * item['cantidad']:.2f}</div>", unsafe_allow_html=True)
            
            with col5:
                st.markdown("<div style='padding-top: 12px;'>", unsafe_allow_html=True)
                if st.button("✕", key=f"del_{idx}", help="Eliminar producto", use_container_width=True):
                    st.session_state.carrito.pop(idx)
                    st.rerun()
                st.markdown("</div>", unsafe_allow_html=True)
            
            st.markdown("</div>", unsafe_allow_html=True)
            st.markdown("<hr style='border-top: 1px solid #E5E5E5; margin: 15px 0;'>", unsafe_allow_html=True)
        
        # Total
        total = calcular_total()
        st.markdown(f"""
        <div style='background: #F8F8F8; padding: 30px; border-radius: 12px; 
                    border: 2px solid #1A1A1A; margin: 30px 0;'>
            <div style='text-align: center; color: #666; margin-bottom: 10px;'>Total del Pedido</div>
            <div style='font-family: "Playfair Display", serif; font-size: 42px; 
                        font-weight: 600; text-align: center; color: #1A1A1A;'>
                S/ {total:.2f}
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        # Acciones
        col_a1, col_a2 = st.columns(2)
        
        with col_a1:
            if st.button("VACIAR CARRITO", use_container_width=True, type="secondary"):
                st.session_state.carrito = []
                st.rerun()
        
        with col_a2:
            mensaje = generar_mensaje_whatsapp()
            try:
                whatsapp_number = st.secrets["contact"]["whatsapp_number"]
            except:
                whatsapp_number = "51980907493"  # Fallback
            
            whatsapp_url = f"https://wa.me/{whatsapp_number}?text={mensaje.replace(' ', '%20').replace('\n', '%0A')}"
            
            st.markdown(f"""
            <a href="{whatsapp_url}" target="_blank" style="text-decoration: none;">
                <button style="background: #25D366; color: white; padding: 14px 28px; 
                               border-radius: 25px; border: 2px solid #25D366; width: 100%; 
                               font-weight: 600; font-size: 15px; cursor: pointer;
                               letter-spacing: 1px; box-shadow: 0 4px 15px rgba(37,211,102,0.35);
                               font-family: 'Lato', sans-serif; font-style: normal;
                               transition: all 0.3s;">
                    ENVIAR POR WHATSAPP
                </button>
            </a>
            """, unsafe_allow_html=True)

# ========== FOOTER ==========
st.markdown("<br><br><br>", unsafe_allow_html=True)
st.markdown("""
<div style='background: #1A1A1A; color: white; padding: 50px 20px; text-align: center; 
            border-radius: 12px; margin-top: 60px;'>
    <div style='font-family: "Playfair Display", serif; font-style: italic; 
                font-size: 36px; margin-bottom: 20px; letter-spacing: 2px;'>
        Nancy's Collection
    </div>
    <div style='font-size: 14px; color: #CCC; line-height: 2;'>
        Elegancia & Feminidad<br>
        📱 WhatsApp • 💳 Yape • Plin • Transferencias<br>
        📍 Lima, Perú
    </div>
    <div style='margin-top: 30px; font-size: 11px; color: #999; letter-spacing: 1px;'>
        © 2025 Nancy's Collection • Todos los derechos reservados
    </div>
</div>
""", unsafe_allow_html=True)
