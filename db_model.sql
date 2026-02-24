CREATE SCHEMA IF NOT EXISTS raw;
CREATE SCHEMA IF NOT EXISTS staging;
CREATE SCHEMA IF NOT EXISTS warehouse;


-- Data cruda o raw
CREATE TABLE raw.ventas_raw (
    id_venta SERIAL,
    fecha TIMESTAMP,
    id_producto INTEGER,
    id_cliente INTEGER,
    cantidad INTEGER,
    medio_pago VARCHAR(50),
    fecha_carga TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);


CREATE TABLE raw.inventario_raw (
    id_producto SERIAL,
    producto VARCHAR(150),
    categoria VARCHAR(100),
    talla VARCHAR(10),
    color VARCHAR(50),
    stock_actual INTEGER,
    precio_adquisicion NUMERIC(10,2),
    precio_venta_unitario NUMERIC(10,2),
    fecha_carga TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);


CREATE TABLE raw.clientes_raw (
    id_cliente SERIAL,
    nombre_cliente VARCHAR(150),
    ubicacion_cliente VARCHAR(150),
    genero VARCHAR(20),
    fecha_registro DATE,
    canal_preferido VARCHAR(50),
    fecha_carga TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);


-- Data intermedia o staging
CREATE TABLE staging.ventas_staging (
    id_venta SERIAL,
    fecha TIMESTAMP,
    id_producto INTEGER,
    id_cliente INTEGER,
    cantidad INTEGER,
    medio_pago VARCHAR(50),
    fecha_carga TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);


CREATE TABLE staging.inventario_staging (
    id_producto SERIAL,
    producto VARCHAR(150),
    categoria VARCHAR(100),
    talla VARCHAR(10),
    color VARCHAR(50),
    stock_actual INTEGER,
    precio_adquisicion NUMERIC(10,2),
    precio_venta_unitario NUMERIC(10,2),
    fecha_carga TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);


CREATE TABLE staging.clientes_staging (
    id_cliente SERIAL,
    nombre_cliente VARCHAR(150),
    ubicacion_cliente VARCHAR(150),
    genero VARCHAR(20),
    fecha_registro DATE,
    canal_preferido VARCHAR(50),
    fecha_carga TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);



-- data procesada 
-- =========================
-- 📅 DIM_FECHA
-- =========================
CREATE TABLE warehouse.dim_fecha (
    id_fecha DATE PRIMARY KEY,
    anio INTEGER NOT NULL,
    mes INTEGER NOT NULL,
    dia INTEGER NOT NULL,
    nombre_mes VARCHAR(20) NOT NULL,
    dia_semana VARCHAR(20) NOT NULL
);

-- =========================
-- 📦 DIM_PRODUCTO
-- =========================
CREATE TABLE warehouse.dim_producto (
    id_producto INTEGER PRIMARY KEY,
    producto VARCHAR(150),
    categoria VARCHAR(100),
    talla VARCHAR(10),
    color VARCHAR(50),
    precio_adquisicion NUMERIC(10,2)
);

-- =========================
-- 👕 DIM_VARIANTE_PRODUCTO (ARREGLADA)
-- =========================

-- =========================
-- 👤 DIM_CLIENTE
-- =========================
CREATE TABLE warehouse.dim_cliente (
    id_cliente INTEGER PRIMARY KEY,
    nombre_cliente VARCHAR(150) NOT NULL,
    ubicacion_cliente VARCHAR(150) NOT NULL,
    genero VARCHAR(20),
    fecha_registro DATE,
    canal_preferido VARCHAR(50)
);

-- =========================
-- 💳 DIM_MEDIO_PAGO
-- =========================
CREATE TABLE warehouse.dim_medio_pago (
    id_medio_pago SERIAL PRIMARY KEY,
    medio_pago VARCHAR(50) UNIQUE NOT NULL
);

-- =========================
-- 📈 FACT_VENTAS
-- =========================
CREATE TABLE warehouse.fact_ventas (
    id_venta INTEGER PRIMARY KEY,
    id_fecha DATE NOT NULL,
    id_cliente INTEGER NOT NULL,
    id_producto INTEGER NOT NULL,
    id_medio_pago INTEGER NOT NULL,

    cantidad INTEGER NOT NULL,
    precio_venta_unitario NUMERIC(10,2) NOT NULL,
    total_venta NUMERIC(12,2) NOT NULL,

    FOREIGN KEY (id_fecha) REFERENCES warehouse.dim_fecha(id_fecha),
    FOREIGN KEY (id_cliente) REFERENCES warehouse.dim_cliente(id_cliente),
    FOREIGN KEY (id_producto) REFERENCES warehouse.dim_producto(id_producto),
    FOREIGN KEY (id_medio_pago) REFERENCES warehouse.dim_medio_pago(id_medio_pago)
);


-- =========================
-- 📦 FACT_INVENTARIO
-- =========================
CREATE TABLE warehouse.fact_inventario (
    id_producto INTEGER NOT NULL,
    stock_actual INTEGER NOT NULL,
    
    PRIMARY KEY (id_producto),

    FOREIGN KEY (id_producto)
        REFERENCES warehouse.dim_producto(id_producto)
);



-- Función para descontar stock en raw
CREATE OR REPLACE FUNCTION raw.descontar_stock()
RETURNS TRIGGER AS $$
DECLARE
    stock_disponible INT;
BEGIN
    -- Bloquear fila de inventario para concurrencia
    SELECT stock_actual
    INTO stock_disponible
    FROM raw.inventario_raw
    WHERE id_producto = NEW.id_producto
    FOR UPDATE;

    -- Validar existencia del producto
    IF stock_disponible IS NULL THEN
        RAISE EXCEPTION 'Producto no existe en inventario_raw';
    END IF;

    -- Validar stock suficiente
    IF stock_disponible < NEW.cantidad THEN
        RAISE EXCEPTION 'Stock insuficiente en inventario_raw';
    END IF;

    -- Descontar stock
    UPDATE raw.inventario_raw
    SET stock_actual = stock_actual - NEW.cantidad
    WHERE id_producto = NEW.id_producto;

    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trigger_descontar_stock_raw
BEFORE INSERT ON raw.ventas_raw
FOR EACH ROW
EXECUTE FUNCTION raw.descontar_stock();



-- optimzacion de la busqueda por indices
CREATE INDEX idx_fact_ventas_fecha
ON warehouse.fact_ventas(id_fecha);

CREATE INDEX idx_fact_ventas_cliente
ON warehouse.fact_ventas(id_cliente);;
