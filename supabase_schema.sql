-- Schema: Nancy's Collection Inventory System
-- Table: tb_catalogo_stock
-- Database: Supabase (PostgreSQL)

CREATE TABLE IF NOT EXISTS public.tb_catalogo_stock (
    id serial PRIMARY KEY,
    sku varchar(64) UNIQUE NOT NULL,
    modelo varchar(200) NOT NULL,
    descripcion text,
    talla varchar(32),
    color varchar(64),
    precio_soles numeric(10,2) DEFAULT 0.00,
    stock_actual integer DEFAULT 0,
    url_foto text,
    updated_at timestamptz DEFAULT now(),
    created_at timestamptz DEFAULT now()
);

-- Indexes
CREATE INDEX IF NOT EXISTS idx_tb_catalogo_modelo ON public.tb_catalogo_stock(modelo);
CREATE INDEX IF NOT EXISTS idx_tb_catalogo_sku ON public.tb_catalogo_stock(sku);
CREATE INDEX IF NOT EXISTS idx_tb_catalogo_stock ON public.tb_catalogo_stock(stock_actual);

-- Auto-update timestamp trigger
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = now();
    RETURN NEW;
END;
$$ language 'plpgsql';

DROP TRIGGER IF EXISTS update_tb_catalogo_stock_updated_at ON public.tb_catalogo_stock;
CREATE TRIGGER update_tb_catalogo_stock_updated_at
    BEFORE UPDATE ON public.tb_catalogo_stock
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- Sample data (optional)
-- INSERT INTO public.tb_catalogo_stock(sku, modelo, descripcion, talla, color, precio_soles, stock_actual, url_foto)
-- VALUES 
--     ('NC-BLS-001-S', 'Blusa Floral Verano', 'Blusa ligera con estampado floral', 'S', 'Multicolor', 79.90, 12, 'https://via.placeholder.com/300'),
--     ('NC-VST-002-M', 'Vestido Casual Botones', 'Vestido veraniego con botones', 'M', 'Azul Claro', 129.50, 7, 'https://via.placeholder.com/300'),
--     ('NC-PNT-004-30', 'Pantalón Jean Clásico', 'Jean de corte recto', '30', 'Azul Denim', 149.90, 18, 'https://via.placeholder.com/300');
