import pandas as pd
import numpy as np
import os
import sys
import random
from datetime import datetime, timedelta

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from dotenv import load_dotenv
from libs.db_connection import get_db_connection
import psycopg2
from psycopg2 import sql

env_path = os.path.join(os.path.dirname(__file__), '..', '.env')
load_dotenv(env_path)

def reseed():
    conn = get_db_connection()
    if not conn: 
        print("Saliendo. No hay conexion.")
        return
        
    schema = os.getenv("DB_SCHEMA", "raw")
    print(f"Usando esquema: {schema}")
    
    print("Vaciando tablas...")
    with conn.cursor() as cur:
        # Cascade truncates todo y resetea IDs
        cur.execute(sql.SQL("TRUNCATE TABLE {}.ventas_raw, {}.inventario_raw, {}.clientes_raw RESTART IDENTITY CASCADE").format(
            sql.Identifier(schema), sql.Identifier(schema), sql.Identifier(schema)
        ))
        conn.commit()

    print("Creando 20 Productos de Inventario...")
    productos = [
        ("Polo Básico Algodón", "Ropa", "S", "Blanco", 50, 20.0, 45.0),
        ("Polo Básico Algodón", "Ropa", "M", "Negro", 50, 20.0, 45.0),
        ("Polo Básico Algodón", "Ropa", "L", "Azul", 30, 20.0, 45.0),
        ("Camisa Oxford", "Ropa", "M", "Celeste", 20, 35.0, 75.0),
        ("Camisa Oxford", "Ropa", "L", "Blanco", 15, 35.0, 75.0),
        ("Pantalón Jean Clásico", "Ropa", "30", "Azul", 40, 45.0, 95.0),
        ("Pantalón Jean Clásico", "Ropa", "32", "Azul", 40, 45.0, 95.0),
        ("Pantalón Jean Clásico", "Ropa", "34", "Negro", 25, 45.0, 95.0),
        ("Casaca Cortaviento", "Ropa", "M", "Verde", 10, 60.0, 120.0),
        ("Casaca Cortaviento", "Ropa", "L", "Negro", 15, 60.0, 120.0),
        
        ("Zapatilla Urbana", "Calzado", "40", "Blanco", 30, 80.0, 150.0),
        ("Zapatilla Urbana", "Calzado", "41", "Negro", 30, 80.0, 150.0),
        ("Zapatilla Urbana", "Calzado", "42", "Blanco", 20, 80.0, 150.0),
        ("Botín de Cuero", "Calzado", "41", "Marrón", 10, 120.0, 250.0),
        ("Botín de Cuero", "Calzado", "42", "Negro", 15, 120.0, 250.0),
        
        ("Gorra Trucker", "Accesorio", "Única", "Negro", 40, 15.0, 35.0),
        ("Gorra Trucker", "Accesorio", "Única", "Azul", 30, 15.0, 35.0),
        ("Cinturón de Cuero", "Accesorio", "Única", "Marrón", 25, 25.0, 60.0),
        ("Cinturón de Cuero", "Accesorio", "Única", "Negro", 20, 25.0, 60.0),
        ("Mochila Urbana", "Accesorio", "Única", "Gris", 12, 40.0, 90.0),
    ]
    
    with conn.cursor() as cur:
        query_prod = sql.SQL('''
            INSERT INTO {}.inventario_raw 
            (producto, categoria, talla, color, stock_actual, precio_adquisicion, precio_venta_unitario)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
            RETURNING id_producto
        ''').format(sql.Identifier(schema))
        
        for p in productos:
            cur.execute(query_prod, p)
            
    print("Creando 9 Clientes...")
    clientes = [
        ("Juan Perez", "Lima", "M"),
        ("Maria Garcia", "Arequipa", "F"),
        ("Carlos Rojas", "Cusco", "M"),
        ("Ana Martinez", "Trujillo", "F"),
        ("Luis Silva", "Piura", "M"),
        ("Elena Fernandez", "Chiclayo", "F"),
        ("Jorge Chavez", "Lima", "M"),
        ("Rosa Linares", "Cusco", "F"),
        ("Cliente Frecuente S.A.C.", "Lima", "U")
    ]
    
    with conn.cursor() as cur:
        query_cli = sql.SQL('''
            INSERT INTO {}.clientes_raw 
            (nombre_cliente, ubicacion_cliente, genero, fecha_registro, canal_preferido)
            VALUES (%s, %s, %s, CURRENT_DATE, 'WhatsApp')
            RETURNING id_cliente
        ''').format(sql.Identifier(schema))
        
        for c in clientes:
            cur.execute(query_cli, c)
            
    print("Generando 100 Ventas...")
    medios_pago = ["Efectivo", "Yape", "Plin", "Tarjeta", "Transferencia"]
    hoy = datetime.now()
    
    with conn.cursor() as cur:
        query_ven = sql.SQL('''
            INSERT INTO {}.ventas_raw 
            (fecha, id_producto, id_cliente, cantidad, medio_pago, fecha_carga)
            VALUES (%s, %s, %s, %s, %s, CURRENT_TIMESTAMP)
        ''').format(sql.Identifier(schema))
        
        for i in range(100):
            id_prod = random.randint(1, 20)
            id_cli = random.randint(1, 9)
            cant = random.choices([1, 2, 3], weights=[0.7, 0.2, 0.1])[0]
            medio = random.choice(medios_pago)
            dias_atras = random.randint(0, 30)
            fecha_venta = hoy - timedelta(days=dias_atras)
            
            cur.execute(query_ven, (fecha_venta, id_prod, id_cli, cant, medio))
            
    conn.commit()
    conn.close()
    print("¡Base de datos re-sembrada con éxito!")

if __name__ == '__main__':
    reseed()
