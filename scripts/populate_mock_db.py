import os
import sys
import datetime
import random
from sqlalchemy.orm import Session
from sqlalchemy import text

# Añadir raíz al sys.path para importar librerías internas
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from libs.db_connection import get_engine
from libs.models import Base, VentaRaw, InventarioRaw, ClienteRaw

def recreate_mock_data():
    engine = get_engine()
    if not engine:
        print("ERROR: No se pudo conectar a la base de datos para generar Mocks.")
        return

    # 1. Productos Fakes
    productos_obj = [
        InventarioRaw(producto="Zapatilla Deportiva Xtreme", categoria="Zapatillas", talla="40", color="Negro", stock_actual=150, precio_adquisicion=120.0, precio_venta_unitario=180.0),
        InventarioRaw(producto="Zapatilla Deportiva Xtreme", categoria="Zapatillas", talla="42", color="Blanco", stock_actual=100, precio_adquisicion=120.0, precio_venta_unitario=180.0),
        InventarioRaw(producto="Polo Algodón Premium", categoria="Polos", talla="M", color="Azul", stock_actual=200, precio_adquisicion=25.0, precio_venta_unitario=45.0),
        InventarioRaw(producto="Polo Algodón Premium", categoria="Polos", talla="L", color="Rojo", stock_actual=40, precio_adquisicion=25.0, precio_venta_unitario=45.0),
        InventarioRaw(producto="Pantalón Jean Clásico", categoria="Pantalones", talla="32", color="Celeste", stock_actual=80, precio_adquisicion=60.0, precio_venta_unitario=110.0),
        InventarioRaw(producto="Pantalón Jean Clásico", categoria="Pantalones", talla="34", color="Azul Oscuro", stock_actual=15, precio_adquisicion=60.0, precio_venta_unitario=110.0),
        InventarioRaw(producto="Gorra Urban Style", categoria="Accesorios", talla="Única", color="Negro", stock_actual=50, precio_adquisicion=15.0, precio_venta_unitario=35.0),
        InventarioRaw(producto="Casaca Térmica", categoria="Invierno", talla="XL", color="Plomo", stock_actual=25, precio_adquisicion=90.0, precio_venta_unitario=150.0)
    ]
    
    # 2. Clientes Fakes
    clientes_obj = [
        ClienteRaw(nombre_cliente="Juan Pérez", ubicacion_cliente="Lima", genero="M", fecha_registro=datetime.date(2025, 1, 15), canal_preferido="Web"),
        ClienteRaw(nombre_cliente="María Gomez", ubicacion_cliente="Arequipa", genero="F", fecha_registro=datetime.date(2025, 2, 10), canal_preferido="Tienda Física"),
        ClienteRaw(nombre_cliente="Carlos Ruiz", ubicacion_cliente="Cusco", genero="M", fecha_registro=datetime.date(2026, 2, 1), canal_preferido="WhatsApp"),
        ClienteRaw(nombre_cliente="Ana Torres", ubicacion_cliente="Trujillo", genero="F", fecha_registro=datetime.date(2024, 11, 20), canal_preferido="Web")
    ]
    
    try:
        with Session(engine) as session:
            # En local, aseguramos que el esquema 'raw' exista
            print("Asegurando existencia del esquema 'raw'...")
            session.execute(text("CREATE SCHEMA IF NOT EXISTS raw"))
            session.commit()
            
            # Crear tablas si no existen (Basado en los modelos)
            print("Sincronizando modelos con la base de datos...")
            Base.metadata.create_all(engine)

            # En SQLAlchemy, para limpiar tablas rapido usamos un execute text en lugar de delete() ORM
            print("Limpiando tablas de datos anteriores ('raw')...")
            try:
                session.execute(text("TRUNCATE TABLE raw.ventas_raw RESTART IDENTITY CASCADE"))
                session.execute(text("TRUNCATE TABLE raw.inventario_raw RESTART IDENTITY CASCADE"))
                session.execute(text("TRUNCATE TABLE raw.clientes_raw RESTART IDENTITY CASCADE"))
            except Exception as e:
                print("Advertencia de Truncate o Permisos:", e)
                # OJO: Si estás apuntando a Aiven y falla, se imprimirá la excepción y se abortará el bloque (Unit of Work).
                # Para evitar esto, si sabemos que puede fallar en Aiven, removemos y lo hacemos por Delete ORM,
                # pero PostgreSQL tira error global si falla el TRUNCATE por ende se hace rollback automático.
                session.rollback()
                print(">>> Asegúrate de tener tu URL local en el archivo .env <<<")
                return
            
            print("Insertando Inventario Mock...")
            session.add_all(productos_obj)
            session.flush() # Forzamos commit intermedio para obtener los IDS generados
            
            print("Insertando Clientes Mock...")
            session.add_all(clientes_obj)
            session.flush()
            
            print("Insertando Ventas Aleatorias Mock...")
            medios_pago = ["Efectivo", "Tarjeta", "Yape", "Transferencia"]
            ventas_obj = []
            
            for i in range(20):
                # Extraer un ID aleatorio usando el objeto ORM insertado
                p = random.choice(productos_obj)
                c = random.choice(clientes_obj)
                
                cantidad = random.randint(1, 3)
                medio = random.choice(medios_pago)
                fecha = datetime.datetime.now() - datetime.timedelta(days=random.randint(0, 30))
                
                v = VentaRaw(
                    id_producto=p.id_producto,
                    id_cliente=c.id_cliente,
                    fecha=fecha,
                    cantidad=cantidad,
                    medio_pago=medio,
                    fecha_carga=fecha
                )
                ventas_obj.append(v)
            
            session.add_all(ventas_obj)
            
            # Commit de todo en un bloque Unit Of Work
            session.commit()
            print("¡Datos MOCK generados y cargados exitosamente usando SQLAlchemy 2.0!")
            
    except Exception as e:
        print(f"Error generando datos mock general: {e}")

if __name__ == "__main__":
    recreate_mock_data()
