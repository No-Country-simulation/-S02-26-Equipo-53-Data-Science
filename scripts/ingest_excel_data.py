import pandas as pd
import os
import sys
import re
from sqlalchemy import text
from sqlalchemy.orm import Session

# Añadir raíz al sys.path para importar librerías internas
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from libs.db_connection import get_engine
from libs.models import Base, VentaRaw, InventarioRaw, ClienteRaw

def clean_id(id_val):
    """Extrae solo los números de un ID tipo 'P101' o 'V001' y lo convierte a int."""
    if pd.isna(id_val):
        return None
    if isinstance(id_val, (int, float)):
        return int(id_val)
    # Regex para buscar dígitos
    match = re.search(r'\d+', str(id_val))
    if match:
        return int(match.group())
    return None

def ingest_data(file_path):
    if not os.path.exists(file_path):
        print(f"Error: No se encuentra el archivo {file_path}")
        return

    engine = get_engine()
    if not engine:
        print("Error: No se pudo conectar a la base de datos.")
        return

    try:
        # 1. Leer Excel
        print(f"Leyendo {file_path}...")
        df_ventas = pd.read_excel(file_path, sheet_name='ventas')
        df_inventario = pd.read_excel(file_path, sheet_name='inventario')
        df_clientes = pd.read_excel(file_path, sheet_name='clientes')

        with Session(engine) as session:
            # 2. Limpiar tablas existentes
            print("Limpiando tablas del esquema 'raw'...")
            session.execute(text("TRUNCATE TABLE raw.ventas_raw RESTART IDENTITY CASCADE"))
            session.execute(text("TRUNCATE TABLE raw.inventario_raw RESTART IDENTITY CASCADE"))
            session.execute(text("TRUNCATE TABLE raw.clientes_raw RESTART IDENTITY CASCADE"))
            session.commit()

            # 3. Mapeo de precios de venta (Extraído de la hoja ventas)
            print("Mapeando precios de venta desde la hoja de ventas...")
            # Limpiamos los IDs de productos en el DataFrame de ventas para el cruce
            df_ventas['id_prod_clean'] = df_ventas['id_producto'].apply(clean_id)
            # Creamos un diccionario {id_producto: precio_venta_unitario}
            # Tomamos el primer precio encontrado por producto
            price_map = df_ventas.drop_duplicates('id_prod_clean').set_index('id_prod_clean')['precio_venta_unitario'].to_dict()

            # 4. Procesar Clientes
            print("Procesando Clientes...")
            clientes = []
            for _, row in df_clientes.iterrows():
                clientes.append(ClienteRaw(
                    id_cliente=clean_id(row['id_cliente']),
                    nombre_cliente=row['nombre_cliente'],
                    ubicacion_cliente=row['ubicacion_cliente'],
                    genero=row['genero'],
                    fecha_registro=pd.to_datetime(row['fecha_registro']).date() if not pd.isna(row['fecha_registro']) else None,
                    canal_preferido=row['canal_preferido']
                ))
            session.add_all(clientes)

            # 5. Procesar Inventario
            print("Procesando Inventario...")
            inventario = []
            for _, row in df_inventario.iterrows():
                pid = clean_id(row['id_producto'])
                # Buscamos el precio en nuestro mapa extraído de ventas
                precio_venta = price_map.get(pid, None)
                
                inventario.append(InventarioRaw(
                    id_producto=pid,
                    producto=row['producto'],
                    categoria=row['categoria'],
                    talla=row['talla'],
                    color=row['color'],
                    stock_actual=row['stock_actual'],
                    precio_adquisicion=row['precio_adquisicion'],
                    precio_venta_unitario=precio_venta
                ))
            session.add_all(inventario)

            # 6. Procesar Ventas
            print("Procesando Ventas...")
            ventas = []
            for _, row in df_ventas.iterrows():
                ventas.append(VentaRaw(
                    # id_venta=clean_id(row['id_venta']), # SERIAL, lo dejamos autogenerar o forzamos?
                    # Si el usuario quiere mantener el ID del Excel:
                    id_venta=clean_id(row['id_venta']),
                    fecha=pd.to_datetime(row['fecha']) if not pd.isna(row['fecha']) else None,
                    id_producto=clean_id(row['id_producto']),
                    id_cliente=clean_id(row['id_cliente']),
                    cantidad=row['cantidad'],
                    medio_pago=row['medio_pago']
                ))
            session.add_all(ventas)

            # 6. Finalizar
            session.commit()
            print("¡Ingesta de datos desde Excel completada exitosamente!")

    except Exception as e:
        print(f"Error durante la ingesta: {e}")

if __name__ == "__main__":
    file_path = "data fake (1).xlsx"
    ingest_data(file_path)
