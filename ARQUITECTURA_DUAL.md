# 🎯 Nancy's Collection - Sistema de Catálogo Cloud-Native

## 📋 Arquitectura del Sistema

Este proyecto consta de **DOS aplicaciones** independientes:

### 1. 🛍️ **Catálogo Público** (`catalogo_publico.py`)
**Usuarios:** Clientes (público general)  
**Acceso:** Abierto (sin autenticación)  
**Funcionalidades:**
- ✅ Visualización de productos con imágenes
- ✅ Filtros por modelo, color y talla
- ✅ Carrito de compras (session local)
- ✅ Generación de pedido vía WhatsApp
- ✅ Solo productos con stock disponible
- ✅ Diseño mobile-friendly

**URL para compartir:** Esta es la URL que compartes en WhatsApp/Instagram

### 2. 🔐 **Panel de Administración** (`admin_panel.py`)
**Usuarios:** Nancy (administradora)  
**Acceso:** Protegido con contraseña  
**Funcionalidades:**
- ✅ Dashboard con métricas de inventario
- ✅ Actualización de stock y precios
- ✅ Alertas de productos agotados/críticos
- ✅ Analytics y reportes
- ✅ Exportación de catálogo (CSV)
- ✅ Vista completa del inventario

---

## 🚀 Despliegue en Streamlit Cloud

### Opción A: Dos Apps Separadas (Recomendado)

#### 1️⃣ Desplegar Catálogo Público
```
App name: nancy-catalogo
Repository: veliz-a/nancy-cloud-catalogo
Branch: main
Main file path: catalogo_publico.py
```

**Secrets (Settings → Secrets):**
```toml
[supabase]
url = "https://tu-proyecto.supabase.co"
key = "tu-anon-key"  # Solo anon key
whatsapp_number = "51987654321"
```

#### 2️⃣ Desplegar Panel Admin
```
App name: nancy-admin
Repository: veliz-a/nancy-cloud-catalogo
Branch: main
Main file path: admin_panel.py
```

**Secrets (Settings → Secrets):**
```toml
[supabase]
url = "https://tu-proyecto.supabase.co"
key = "tu-anon-key"
service_role_key = "tu-service-role-key"  # Key con permisos de escritura
admin_password = "TU_CONTRASEÑA_SEGURA"  # ⚠️ Cambia esto!
```

### URLs Resultantes:
- **Pública (clientes):** `https://nancy-catalogo.streamlit.app`
- **Admin (Nancy):** `https://nancy-admin.streamlit.app`

---

## 🔒 Configuración de Seguridad en Supabase

### Row Level Security (RLS) - Recomendado

```sql
-- Habilitar RLS en la tabla
ALTER TABLE public.tb_catalogo_stock ENABLE ROW LEVEL SECURITY;

-- Política: Lectura pública (para catálogo público)
CREATE POLICY "Enable read access for all users" ON public.tb_catalogo_stock
FOR SELECT USING (true);

-- Política: Escritura solo con service_role_key (para admin)
-- Las operaciones con service_role_key ignoran RLS automáticamente
```

**Ventajas:**
- ✅ Anon key solo puede LEER productos
- ✅ Service role key puede EDITAR/ACTUALIZAR
- ✅ Protección a nivel de base de datos

---

## 📱 Flujo de Uso

### Para Clientes:
1. Nancy comparte link del catálogo en WhatsApp/Instagram
2. Cliente entra al catálogo público
3. Filtra productos por color/talla
4. Agrega productos al carrito
5. Revisa su pedido en el carrito
6. Click en "Enviar por WhatsApp"
7. Se abre WhatsApp con el pedido formateado
8. Cliente envía el mensaje a Nancy

### Para Nancy (Admin):
1. Entra al panel admin (URL privada)
2. Ingresa contraseña
3. Ve dashboard con métricas
4. Actualiza stock cuando vende/recibe productos
5. Revisa alertas de productos agotados
6. Exporta reportes cuando necesita

---

## 🛠️ Ejecución Local

### Catálogo Público:
```bash
streamlit run catalogo_publico.py
```

### Panel Admin:
```bash
streamlit run admin_panel.py
```

---

## ⚙️ Configuración Inicial

1. **Crear tabla en Supabase:**
   ```bash
   # Ejecuta en Supabase SQL Editor
   cat supabase_schema.sql
   ```

2. **Insertar productos:**
   ```bash
   python generate_catalog_data.py
   # Ejecuta el SQL generado en Supabase
   ```

3. **Subir imágenes:**
   ```bash
   python upload_images_to_supabase.py
   ```

4. **Configurar secrets locales:**
   ```bash
   cp .streamlit/secrets.toml.example .streamlit/secrets.toml
   # Edita secrets.toml con tus credenciales
   ```

---

## 🎨 Personalización

### Cambiar número de WhatsApp:
En `.streamlit/secrets.toml`:
```toml
whatsapp_number = "51987654321"
```

### Cambiar contraseña de admin:
En `.streamlit/secrets.toml`:
```toml
admin_password = "tu_nueva_contraseña_segura"
```

### Cambiar colores/estilos:
Edita el CSS en cada archivo `.py` (sección `st.markdown` con `<style>`)

---

## 📊 Ventajas del Sistema de Dos Apps

| Aspecto | Catálogo Público | Panel Admin |
|---------|------------------|-------------|
| **URL** | Pública, compartible | Privada, solo Nancy |
| **Autenticación** | ❌ No requiere | ✅ Contraseña |
| **Funciones** | Ver, filtrar, carrito | CRUD completo |
| **Permisos Supabase** | Anon key (solo lectura) | Service key (escritura) |
| **Deploy** | Separado, optimizado para clientes | Separado, herramientas admin |
| **Rendimiento** | Ligero, rápido | Completo, con analytics |

---

## 🔄 Próximas Mejoras Sugeridas

1. **Autenticación avanzada:**
   - Usar Supabase Auth para admin
   - Login con email/password
   - Recuperación de contraseña

2. **Historial de pedidos:**
   - Tabla `pedidos` en Supabase
   - Guardar pedidos enviados por WhatsApp
   - Dashboard de ventas

3. **Gestión de imágenes:**
   - Upload directo desde admin panel
   - Editor de productos (crear/editar/eliminar)

4. **Notificaciones:**
   - Email cuando stock es crítico
   - Telegram/WhatsApp bot para alertas

5. **Multi-tienda:**
   - Varios vendedores
   - Comisiones
   - Inventario compartido

---

## 📞 Soporte

Para dudas sobre el sistema:
- Revisa `INSTRUCCIONES_CARGA.md`
- Consulta logs en Streamlit Cloud
- Verifica configuración de Supabase RLS

---

**Desarrollado con ❤️ para Nancy's Collection**  
Stack: Streamlit + Supabase + Python
