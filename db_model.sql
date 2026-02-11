CREATE DATABASE mi_app_db;

DROP DATABASE mi_app_db;

CREATE SCHEMA IF NOT EXISTS raw;
CREATE SCHEMA IF NOT EXISTS warehouse;


-- Data cruda o raw
CREATE TABLE raw.ventas_raw (
    id_venta SERIAL PRIMARY KEY,
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
    id_producto INTEGER,
    producto VARCHAR(150),
    categoria VARCHAR(100),
    talla VARCHAR(10),
    color VARCHAR(50),
    stock_actual INTEGER,
    stock_minimo INTEGER,
    precio_adquisicion NUMERIC(10,2),
    fecha_carga TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);


CREATE TABLE raw.clientes_raw (
    id_cliente INTEGER,
    nombre_cliente VARCHAR(150),
    ubicacion_cliente VARCHAR(150),
    genero VARCHAR(20),
    fecha_registro DATE,
    canal_preferido VARCHAR(50),
    fecha_carga TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);


-- data procesada 
CREATE TABLE warehouse.dim_fecha (
    id_fecha DATE PRIMARY KEY,
    anio INTEGER,
    mes INTEGER,
    dia INTEGER,
    nombre_mes VARCHAR(20),
    dia_semana VARCHAR(20)
);

CREATE TABLE warehouse.dim_producto (
    id_producto INTEGER PRIMARY KEY,
    producto VARCHAR(150),
    categoria VARCHAR(100),
    precio_adquisicion NUMERIC(10,2)
);


CREATE TABLE warehouse.dim_variante_producto (
    id_variante SERIAL PRIMARY KEY,
    id_producto INTEGER,
    talla VARCHAR(10),
    color VARCHAR(50),

    FOREIGN KEY (id_producto)
        REFERENCES warehouse.dim_producto(id_producto)
);


CREATE TABLE warehouse.dim_cliente (
    id_cliente INTEGER PRIMARY KEY,
    nombre_cliente VARCHAR(150),
    ubicacion_cliente VARCHAR(150),
    genero VARCHAR(20),
    fecha_registro DATE,
    canal_preferido VARCHAR(50)
);


CREATE TABLE warehouse.dim_medio_pago (
    id_medio_pago SERIAL PRIMARY KEY,
    medio_pago VARCHAR(50)
);


CREATE TABLE warehouse.fact_ventas (
    id_venta INTEGER PRIMARY KEY,

    id_fecha DATE,
    id_cliente INTEGER,
    id_variante INTEGER,
    id_medio_pago INTEGER,

    cantidad INTEGER,
    precio_venta_unitario NUMERIC(10,2),
    total_venta NUMERIC(12,2),

    FOREIGN KEY (id_fecha)
        REFERENCES warehouse.dim_fecha(id_fecha),

    FOREIGN KEY (id_cliente)
        REFERENCES warehouse.dim_cliente(id_cliente),

    FOREIGN KEY (id_variante)
        REFERENCES warehouse.dim_variante_producto(id_variante),

    FOREIGN KEY (id_medio_pago)
        REFERENCES warehouse.dim_medio_pago(id_medio_pago)
);


CREATE TABLE warehouse.fact_inventario (
    id_variante INTEGER PRIMARY KEY,
    stock_actual INTEGER,
    stock_minimo INTEGER,

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