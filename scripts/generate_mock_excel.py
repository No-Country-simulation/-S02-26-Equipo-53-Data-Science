import pandas as pd
import numpy as np
import random
from datetime import datetime, timedelta
import os

def generar_excel():
    # 1. Generar 20 Productos de Inventario
    productos = [
        {"producto": "Polo Básico Algodón", "categoria": "Ropa", "talla": "S", "color": "Blanco", "stock_actual": 50, "precio_adquisicion": 20.0, "precio_venta_unitario": 45.0},
        {"producto": "Polo Básico Algodón", "categoria": "Ropa", "talla": "M", "color": "Negro", "stock_actual": 50, "precio_adquisicion": 20.0, "precio_venta_unitario": 45.0},
        {"producto": "Polo Básico Algodón", "categoria": "Ropa", "talla": "L", "color": "Azul", "stock_actual": 30, "precio_adquisicion": 20.0, "precio_venta_unitario": 45.0},
        {"producto": "Camisa Oxford", "categoria": "Ropa", "talla": "M", "color": "Celeste", "stock_actual": 20, "precio_adquisicion": 35.0, "precio_venta_unitario": 75.0},
        {"producto": "Camisa Oxford", "categoria": "Ropa", "talla": "L", "color": "Blanco", "stock_actual": 15, "precio_adquisicion": 35.0, "precio_venta_unitario": 75.0},
        {"producto": "Pantalón Jean Clásico", "categoria": "Ropa", "talla": "30", "color": "Azul", "stock_actual": 40, "precio_adquisicion": 45.0, "precio_venta_unitario": 95.0},
        {"producto": "Pantalón Jean Clásico", "categoria": "Ropa", "talla": "32", "color": "Azul", "stock_actual": 40, "precio_adquisicion": 45.0, "precio_venta_unitario": 95.0},
        {"producto": "Pantalón Jean Clásico", "categoria": "Ropa", "talla": "34", "color": "Negro", "stock_actual": 25, "precio_adquisicion": 45.0, "precio_venta_unitario": 95.0},
        {"producto": "Casaca Cortaviento", "categoria": "Ropa", "talla": "M", "color": "Verde", "stock_actual": 10, "precio_adquisicion": 60.0, "precio_venta_unitario": 120.0},
        {"producto": "Casaca Cortaviento", "categoria": "Ropa", "talla": "L", "color": "Negro", "stock_actual": 15, "precio_adquisicion": 60.0, "precio_venta_unitario": 120.0},
        
        {"producto": "Zapatilla Urbana", "categoria": "Calzado", "talla": "40", "color": "Blanco", "stock_actual": 30, "precio_adquisicion": 80.0, "precio_venta_unitario": 150.0},
        {"producto": "Zapatilla Urbana", "categoria": "Calzado", "talla": "41", "color": "Negro", "stock_actual": 30, "precio_adquisicion": 80.0, "precio_venta_unitario": 150.0},
        {"producto": "Zapatilla Urbana", "categoria": "Calzado", "talla": "42", "color": "Blanco", "stock_actual": 20, "precio_adquisicion": 80.0, "precio_venta_unitario": 150.0},
        {"producto": "Botín de Cuero", "categoria": "Calzado", "talla": "41", "color": "Marrón", "stock_actual": 10, "precio_adquisicion": 120.0, "precio_venta_unitario": 250.0},
        {"producto": "Botín de Cuero", "categoria": "Calzado", "talla": "42", "color": "Negro", "stock_actual": 15, "precio_adquisicion": 120.0, "precio_venta_unitario": 250.0},
        
        {"producto": "Gorra Trucker", "categoria": "Accesorio", "talla": "Única", "color": "Negro", "stock_actual": 40, "precio_adquisicion": 15.0, "precio_venta_unitario": 35.0},
        {"producto": "Gorra Trucker", "categoria": "Accesorio", "talla": "Única", "color": "Azul", "stock_actual": 30, "precio_adquisicion": 15.0, "precio_venta_unitario": 35.0},
        {"producto": "Cinturón de Cuero", "categoria": "Accesorio", "talla": "Única", "color": "Marrón", "stock_actual": 25, "precio_adquisicion": 25.0, "precio_venta_unitario": 60.0},
        {"producto": "Cinturón de Cuero", "categoria": "Accesorio", "talla": "Única", "color": "Negro", "stock_actual": 20, "precio_adquisicion": 25.0, "precio_venta_unitario": 60.0},
        {"producto": "Mochila Urbana", "categoria": "Accesorio", "talla": "Única", "color": "Gris", "stock_actual": 12, "precio_adquisicion": 40.0, "precio_venta_unitario": 90.0},
    ]
    df_inventario = pd.DataFrame(productos)
    df_inventario.to_excel("mock_inventario.xlsx", index=False)
    print("Creado: mock_inventario.xlsx")

    # 2. Generar 9 Clientes
    clientes = [
        {"nombre_cliente": "Juan Perez", "ubicacion_cliente": "Lima", "genero": "M", "canal_preferido": "WhatsApp"},
        {"nombre_cliente": "Maria Garcia", "ubicacion_cliente": "Arequipa", "genero": "F", "canal_preferido": "Instagram"},
        {"nombre_cliente": "Carlos Rojas", "ubicacion_cliente": "Cusco", "genero": "M", "canal_preferido": "Facebook"},
        {"nombre_cliente": "Ana Martinez", "ubicacion_cliente": "Trujillo", "genero": "F", "canal_preferido": "WhatsApp"},
        {"nombre_cliente": "Luis Silva", "ubicacion_cliente": "Piura", "genero": "M", "canal_preferido": "Tienda Física"},
        {"nombre_cliente": "Elena Fernandez", "ubicacion_cliente": "Chiclayo", "genero": "F", "canal_preferido": "Instagram"},
        {"nombre_cliente": "Jorge Chavez", "ubicacion_cliente": "Lima", "genero": "M", "canal_preferido": "WhatsApp"},
        {"nombre_cliente": "Rosa Linares", "ubicacion_cliente": "Cusco", "genero": "F", "canal_preferido": "Tienda Física"},
        {"nombre_cliente": "Cliente Frecuente S.A.C.", "ubicacion_cliente": "Lima", "genero": "U", "canal_preferido": "Email"}
    ]
    df_clientes = pd.DataFrame(clientes)
    df_clientes.to_excel("mock_clientes.xlsx", index=False)
    print("Creado: mock_clientes.xlsx")

    # 3. Generar 100 Ventas
    ventas = []
    medios_pago = ["Efectivo", "Yape", "Plin", "Tarjeta", "Transferencia"]
    hoy = datetime.now()
    
    for _ in range(100):
        prod = random.choice(productos)
        cli = random.choice(clientes)
        
        cant = random.choices([1, 2, 3], weights=[0.7, 0.2, 0.1])[0]
        medio = random.choice(medios_pago)
        dias_atras = random.randint(0, 30)
        fecha_venta = (hoy - timedelta(days=dias_atras)).strftime("%Y-%m-%d")
        
        # En la hoja de Ventas el cliente no provee todos los detalles a veces, 
        # pero para que cruce con inventario le pondremos producto, talla y color correctos.
        # Categoría y precio lo puede deducir la app, dejaremos algunos en blanco para probar!
        
        incluir_cat = random.choice([True, False])
        incluir_precio = random.choice([True, False])
        
        ventas.append({
            "fecha": fecha_venta,
            "producto": prod["producto"],
            "talla": prod["talla"],
            "color": prod["color"],
            "categoria": prod["categoria"] if incluir_cat else "",
            "precio": prod["precio_venta_unitario"] if incluir_precio else "",
            "cantidad": cant,
            "nombre_cliente": cli["nombre_cliente"],
            "medio_pago": medio
        })
        
    df_ventas = pd.DataFrame(ventas)
    df_ventas.to_excel("mock_ventas.xlsx", index=False)
    print("Creado: mock_ventas.xlsx")

if __name__ == '__main__':
    generar_excel()
