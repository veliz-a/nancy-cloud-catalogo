"""
Script para generar datos del catálogo desde los archivos en catalogo-nancy's
Crea: 
  1. catalog_seed.sql - SQL para insertar productos
  2. catalog_data.json - Datos estructurados para uso en Python
"""

import os
import re
import json
from pathlib import Path

# Directorio del catálogo
CATALOG_DIR = Path(__file__).parent / "catalogo-nancy's"
PRICES_FILE = CATALOG_DIR / "precios-catalogo.txt"

def parse_prices_file():
    """Parsea el archivo de precios y extrae la información de productos."""
    products = []
    
    with open(PRICES_FILE, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Patrón para extraer códigos y precios
    # Formato: COD XXXX - Descripción\nPEN XXX.XX
    pattern = r'COD\s+(\d+)\s*-\s*([^\n]+)\n(?:Tallas?\s+([^\n]+)\n)?.*?PEN\s+([\d.]+)'
    
    matches = re.finditer(pattern, content, re.IGNORECASE | re.MULTILINE)
    
    seen_codes = {}
    
    for match in matches:
        code = match.group(1).strip()
        description = match.group(2).strip()
        sizes = match.group(3).strip() if match.group(3) else "Única"
        price = float(match.group(4).strip())
        
        # Limpiar descripción
        description_clean = re.sub(r'\s+', ' ', description).strip()
        
        # Buscar imágenes asociadas al código
        images = find_images_for_code(code)
        
        # Si hay múltiples imágenes (variantes de color), crear entrada por cada una
        if images:
            for img_path, color_variant in images:
                sku = f"NC-{code}-{color_variant}" if color_variant else f"NC-{code}"
                
                # Evitar duplicados exactos
                key = f"{code}-{color_variant}"
                if key not in seen_codes:
                    products.append({
                        'sku': sku,
                        'codigo': code,
                        'modelo': description_clean,
                        'descripcion': f"{description_clean} - {sizes}",
                        'talla': sizes,
                        'color': color_variant if color_variant else 'Sin especificar',
                        'precio_soles': price,
                        'stock_actual': 10,  # Stock inicial por defecto
                        'image_file': img_path,
                        'url_foto': None  # Se completará después de subir a Supabase
                    })
                    seen_codes[key] = True
        else:
            # Producto sin imagen detectada
            sku = f"NC-{code}"
            if code not in seen_codes:
                products.append({
                    'sku': sku,
                    'codigo': code,
                    'modelo': description_clean,
                    'descripcion': f"{description_clean} - {sizes}",
                    'talla': sizes,
                    'color': 'Sin especificar',
                    'precio_soles': price,
                    'stock_actual': 10,
                    'image_file': None,
                    'url_foto': None
                })
                seen_codes[code] = True
    
    return products

def find_images_for_code(code):
    """Encuentra todas las imágenes PNG asociadas a un código de producto."""
    images = []
    code_normalized = code.zfill(4)  # Pad con ceros: 253 -> 0253
    
    # Buscar archivos que contengan el código (solo PNG)
    for file in CATALOG_DIR.iterdir():
        if file.is_file():
            filename = file.name.lower()
            # Buscar patrón: cod0253-descripcion-color.png (solo PNG)
            if f"cod{code_normalized}" in filename and file.suffix == '.png':
                # Extraer variante de color del nombre de archivo
                color_variant = extract_color_from_filename(filename, code_normalized)
                images.append((file.name, color_variant))
    
    return images

def extract_color_from_filename(filename, code):
    """Extrae el color/variante del nombre de archivo."""
    # Remover extensión y código
    base = filename.replace(f"cod{code}-", "").rsplit('.', 1)[0]
    
    # Mapeo de palabras clave a colores
    color_map = {
        'azul': 'Azul',
        'rojo': 'Rojo',
        'rosa': 'Rosa',
        'crema': 'Crema',
        'blanca': 'Blanco',
        'blanco': 'Blanco',
        'negro': 'Negro',
        'verde': 'Verde',
        'amarillo': 'Amarillo',
        'morado': 'Morado',
        'gris': 'Gris',
        'marron': 'Marrón',
        'beige': 'Beige',
        'celeste': 'Celeste',
        'marino': 'Azul Marino',
        'roazul': 'Azul',  # Caso especial del archivo
    }
    
    for key, color in color_map.items():
        if key in base:
            return color
    
    # Si no hay color específico, usar el nombre base como variante
    return base.capitalize() if base else None

def generate_sql(products):
    """Genera el archivo SQL de inserción."""
    sql_lines = [
        "-- Datos del catálogo Nancy's Collection",
        "-- Generado automáticamente desde catalogo-nancy's/",
        "-- Fecha: " + str(Path(__file__).stat().st_mtime),
        "",
        "-- Limpiar tabla existente (opcional - comentar si quieres mantener datos)",
        "-- TRUNCATE TABLE public.tb_catalogo_stock RESTART IDENTITY CASCADE;",
        "",
        "-- Insertar productos",
        "INSERT INTO public.tb_catalogo_stock(sku, modelo, descripcion, talla, color, precio_soles, stock_actual, url_foto)",
        "VALUES"
    ]
    
    values = []
    for product in products:
        sku = product['sku']
        modelo = product['modelo'].replace("'", "''")
        descripcion = product['descripcion'].replace("'", "''")
        talla = product['talla'].replace("'", "''")
        color = product['color'].replace("'", "''")
        precio = product['precio_soles']
        stock = product['stock_actual']
        url_foto = "NULL"  # Se actualizará después de subir imágenes
        
        values.append(
            f"    ('{sku}', '{modelo}', '{descripcion}', '{talla}', '{color}', {precio}, {stock}, {url_foto})"
        )
    
    sql_lines.append(",\n".join(values))
    sql_lines.append("ON CONFLICT (sku) DO UPDATE SET")
    sql_lines.append("    modelo = EXCLUDED.modelo,")
    sql_lines.append("    descripcion = EXCLUDED.descripcion,")
    sql_lines.append("    talla = EXCLUDED.talla,")
    sql_lines.append("    color = EXCLUDED.color,")
    sql_lines.append("    precio_soles = EXCLUDED.precio_soles,")
    sql_lines.append("    stock_actual = EXCLUDED.stock_actual;")
    sql_lines.append("")
    
    return "\n".join(sql_lines)

def main():
    """Función principal."""
    print("🔍 Parseando catálogo desde catalogo-nancy's/...")
    
    products = parse_prices_file()
    
    print(f"✅ Se encontraron {len(products)} productos")
    
    # Generar SQL
    sql_content = generate_sql(products)
    sql_file = Path(__file__).parent / "catalog_seed.sql"
    with open(sql_file, 'w', encoding='utf-8') as f:
        f.write(sql_content)
    print(f"📄 Archivo SQL generado: {sql_file}")
    
    # Generar JSON (para script de Python)
    json_file = Path(__file__).parent / "catalog_data.json"
    with open(json_file, 'w', encoding='utf-8') as f:
        json.dump(products, f, indent=2, ensure_ascii=False)
    print(f"📄 Archivo JSON generado: {json_file}")
    
    # Mostrar resumen
    print("\n📊 Resumen del catálogo:")
    print(f"   - Total productos: {len(products)}")
    print(f"   - Productos con imagen: {sum(1 for p in products if p['image_file'])}")
    print(f"   - Productos sin imagen: {sum(1 for p in products if not p['image_file'])}")
    
    print("\n📝 Ejemplo de productos:")
    for i, product in enumerate(products[:5], 1):
        print(f"   {i}. {product['sku']} - {product['modelo']} ({product['color']}) - S/ {product['precio_soles']}")
        if product['image_file']:
            print(f"      Imagen: {product['image_file']}")
    
    print("\n✅ Proceso completado. Archivos listos para usar.")
    print(f"\n📌 Próximos pasos:")
    print(f"   1. Revisar catalog_seed.sql y ejecutarlo en Supabase")
    print(f"   2. Usar upload_images_to_supabase.py para subir las imágenes")

if __name__ == "__main__":
    main()
