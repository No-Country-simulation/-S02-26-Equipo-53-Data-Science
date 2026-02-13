CREATE SCHEMA IF NOT EXISTS raw;
CREATE SCHEMA IF NOT EXISTS warehouse;


-- Data cruda o raw
CREATE TABLE raw.ventas_raw (
    id_venta SERIAL,
    fecha TIMESTAMP,
    id_producto INTEGER,
    id_cliente INTEGER,
    cantidad INTEGER,
    talla VARCHAR(10),
    color VARCHAR(50),
    precio_venta_unitario NUMERIC(10,2),
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
    producto VARCHAR(150) NOT NULL,
    categoria VARCHAR(100) NOT NULL,
    precio_adquisicion NUMERIC(10,2) NOT NULL
);

-- =========================
-- 👕 DIM_VARIANTE_PRODUCTO (ARREGLADA)
-- =========================
CREATE TABLE warehouse.dim_variante_producto (
    id_variante SERIAL PRIMARY KEY,
    
    id_producto INTEGER NOT NULL,
    talla VARCHAR(10) NOT NULL,
    color VARCHAR(50) NOT NULL,

    CONSTRAINT fk_producto
        FOREIGN KEY (id_producto)
        REFERENCES warehouse.dim_producto(id_producto),

    -- 🔥 Esto evita duplicados reales
    CONSTRAINT unique_variante
        UNIQUE (id_producto, talla, color)
);

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
    id_variante INTEGER NOT NULL,
    id_medio_pago INTEGER NOT NULL,

    cantidad INTEGER NOT NULL,
    precio_venta_unitario NUMERIC(10,2) NOT NULL,
    total_venta NUMERIC(12,2) NOT NULL,

    CONSTRAINT fk_fecha
        FOREIGN KEY (id_fecha)
        REFERENCES warehouse.dim_fecha(id_fecha),

    CONSTRAINT fk_cliente
        FOREIGN KEY (id_cliente)
        REFERENCES warehouse.dim_cliente(id_cliente),

    CONSTRAINT fk_variante
        FOREIGN KEY (id_variante)
        REFERENCES warehouse.dim_variante_producto(id_variante),

    CONSTRAINT fk_medio_pago
        FOREIGN KEY (id_medio_pago)
        REFERENCES warehouse.dim_medio_pago(id_medio_pago)
);

-- =========================
-- 📦 FACT_INVENTARIO
-- =========================
CREATE TABLE warehouse.fact_inventario (
    id_variante INTEGER PRIMARY KEY,
    stock_actual INTEGER NOT NULL,

    CONSTRAINT fk_variante_inventario
        FOREIGN KEY (id_variante)
        REFERENCES warehouse.dim_variante_producto(id_variante)
);




-- optimzacion de la busqueda por indices
CREATE INDEX idx_fact_ventas_fecha
ON warehouse.fact_ventas(id_fecha);

CREATE INDEX idx_fact_ventas_cliente
ON warehouse.fact_ventas(id_cliente);

CREATE INDEX idx_fact_ventas_variante
ON warehouse.fact_ventas(id_variante);

