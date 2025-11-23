"""
Script para subir imágenes del catálogo a Supabase Storage.
Actualiza las URLs en la base de datos después de subir.

IMPORTANTE: Necesitas configurar la Service Role Key en .streamlit/secrets.toml
"""

import os
import json
from pathlib import Path
from supabase import create_client, Client
import streamlit as st

# Directorio del catálogo
CATALOG_DIR = Path(__file__).parent / "catalogo-nancy's"
DATA_FILE = Path(__file__).parent / "catalog_data.json"
BUCKET_NAME = "product-images"

def init_supabase_client() -> Client:
    """Inicializa cliente de Supabase con Service Role Key."""
    try:
        # Intentar cargar desde secrets de Streamlit
        url = st.secrets["supabase"]["url"]
        # Para subir imágenes necesitamos la service_role_key (no la anon key)
        key = st.secrets["supabase"].get("service_role_key") or st.secrets["supabase"]["key"]
        return create_client(url, key)
    except Exception as e:
        print(f"ERROR: Error al inicializar Supabase: {e}")
        print("\nADVERTENCIA: Para subir imágenes necesitas configurar la Service Role Key")
        print("   En .streamlit/secrets.toml agrega:")
        print('   service_role_key = "tu-service-role-key"')
        print("\n   Puedes obtenerla en: Supabase → Settings → API → service_role key")
        raise

def ensure_bucket_exists(supabase: Client):
    """Verifica que el bucket exista, si no lo crea."""
    try:
        # Listar buckets
        buckets = supabase.storage.list_buckets()
        bucket_names = [b.name for b in buckets]
        
        if BUCKET_NAME not in bucket_names:
            print(f"Creando bucket '{BUCKET_NAME}'...")
            supabase.storage.create_bucket(
                BUCKET_NAME,
                options={"public": True}  # Bucket público para imágenes
            )
            print(f"OK: Bucket '{BUCKET_NAME}' creado correctamente")
        else:
            print(f"OK: Bucket '{BUCKET_NAME}' ya existe")
    except Exception as e:
        print(f"ADVERTENCIA: No se pudo verificar/crear bucket: {e}")

def upload_image(supabase: Client, image_path: Path, sku: str) -> str:
    """Sube una imagen a Supabase Storage y retorna la URL pública."""
    try:
        # Nombre del archivo en Storage (usar SKU para organización)
        storage_path = f"{sku}-{image_path.name}"
        
        # Leer archivo
        with open(image_path, 'rb') as f:
            file_data = f.read()
        
        # Subir archivo
        supabase.storage.from_(BUCKET_NAME).upload(
            storage_path,
            file_data,
            file_options={"content-type": "image/png", "upsert": "true"}
        )
        
        # Obtener URL pública
        public_url = supabase.storage.from_(BUCKET_NAME).get_public_url(storage_path)
        
        return public_url
    except Exception as e:
        print(f"   ERROR: Error subiendo {image_path.name}: {e}")
        return None

def update_product_image_url(supabase: Client, sku: str, url: str):
    """Actualiza la URL de imagen en la base de datos."""
    try:
        supabase.table('tb_catalogo_stock').update({'url_foto': url}).eq('sku', sku).execute()
        return True
    except Exception as e:
        print(f"   ERROR: Error actualizando URL para {sku}: {e}")
        return False

def main():
    """Función principal."""
    print("Iniciando subida de imágenes a Supabase Storage...\n")
    
    # Verificar que exista el archivo de datos
    if not DATA_FILE.exists():
        print("ERROR: No se encontró catalog_data.json")
        print("   Ejecuta primero: python generate_catalog_data.py")
        return
    
    # Cargar datos del catálogo
    with open(DATA_FILE, 'r', encoding='utf-8') as f:
        products = json.load(f)
    
    print(f"Se encontraron {len(products)} productos en catalog_data.json")
    products_with_images = [p for p in products if p['image_file']]
    print(f"Productos con imágenes: {len(products_with_images)}\n")
    
    # Inicializar cliente de Supabase
    try:
        supabase = init_supabase_client()
    except:
        return
    
    # Verificar/crear bucket
    ensure_bucket_exists(supabase)
    
    print("\nSubiendo imágenes...\n")
    
    # Subir imágenes y actualizar URLs
    success_count = 0
    error_count = 0
    
    for product in products_with_images:
        sku = product['sku']
        image_file = product['image_file']
        image_path = CATALOG_DIR / image_file
        
        if not image_path.exists():
            print(f"ADVERTENCIA: {sku}: Imagen no encontrada ({image_file})")
            error_count += 1
            continue
        
        print(f"Subiendo {sku}: {image_file}...")
        
        # Subir imagen
        public_url = upload_image(supabase, image_path, sku)
        
        if public_url:
            # Actualizar base de datos
            if update_product_image_url(supabase, sku, public_url):
                print(f"   OK: URL actualizada en DB")
                success_count += 1
            else:
                error_count += 1
        else:
            error_count += 1
    
    # Resumen
    print("\n" + "="*60)
    print("RESUMEN DE SUBIDA")
    print("="*60)
    print(f"OK: Imágenes subidas exitosamente: {success_count}")
    print(f"ERROR: Errores: {error_count}")
    print(f"Bucket usado: {BUCKET_NAME}")
    
    if success_count > 0:
        print("\nProceso completado!")
        print(f"   Las imágenes están disponibles en:")
        print(f"   Supabase → Storage → {BUCKET_NAME}")
        print(f"\n   Las URLs ya están actualizadas en tb_catalogo_stock")
    
    if error_count > 0:
        print(f"\nADVERTENCIA: Hubo {error_count} errores. Revisa los mensajes arriba.")

if __name__ == "__main__":
    main()
