# Instrucciones para Cargar el Catálogo a Supabase

## Paso 1: Crear la Tabla en Supabase

1. Ve a tu proyecto en Supabase
2. Abre el SQL Editor
3. Ejecuta el contenido de `supabase_schema.sql`
4. Verifica que la tabla `tb_catalogo_stock` se creó correctamente

## Paso 2: Insertar los Productos

1. En el SQL Editor de Supabase
2. Ejecuta el contenido de `catalog_seed.sql`
3. Esto insertará 21 productos del catálogo

## Paso 3: Configurar Service Role Key (para subir imágenes)

1. Ve a Supabase → Settings → API
2. Copia tu **service_role key** (⚠️ SECRETO - no la compartas)
3. Edita `.streamlit/secrets.toml` y agrega:

```toml
[supabase]
url = "https://tu-proyecto.supabase.co"
key = "tu-anon-key"
service_role_key = "tu-service-role-key-aqui"
```

## Paso 4: Subir las Imágenes PNG

Ejecuta el script de subida de imágenes:

```bash
python upload_images_to_supabase.py
```

Este script:
- Crea el bucket `product-images` en Supabase Storage (si no existe)
- Sube las 17 imágenes PNG del catálogo
- Actualiza automáticamente las URLs en `tb_catalogo_stock`

## Paso 5: Ejecutar la Aplicación

```bash
streamlit run app_catalogo_nancy.py
```

## Resumen del Catálogo

- **Total productos**: 21
- **Productos con imagen PNG**: 17
- **Productos sin imagen**: 4

### Categorías:
- Vestidos (6)
- Enterizos (3 colores)
- Gabardinas (3 variantes)
- Pantalones (3 colores)
- Blusas (1)
- Conjuntos (2)
- Blazers (2)
- Polos (1)

## Archivos Generados

- `catalog_seed.sql` - SQL para insertar productos
- `catalog_data.json` - Datos estructurados (usado por el script de imágenes)
- `generate_catalog_data.py` - Script que generó los archivos (ya ejecutado)
- `upload_images_to_supabase.py` - Script para subir imágenes

## Notas Importantes

⚠️ **Security**: La `service_role_key` tiene acceso completo a tu proyecto. Úsala solo localmente y NUNCA la subas a Git.

📦 **Storage**: Las imágenes se subirán al bucket público `product-images` en Supabase Storage.

🔄 **Actualización**: Si necesitas actualizar los datos, vuelve a ejecutar `catalog_seed.sql` (usa `ON CONFLICT` para upsert).
