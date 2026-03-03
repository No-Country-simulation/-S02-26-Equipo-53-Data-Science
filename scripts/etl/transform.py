import pandas as pd

def clean_dataframe(df):
    """
    Aplica las reglas de limpieza correspondientes a Ventas, Inventario o Clientes.
    """
    if df.empty:
        return df

    cols = df.columns.tolist()

    # 1. LÓGICA PARA VENTAS
    if 'id_venta' in cols:
        print("✨ Limpiando datos de Ventas...")
        df = df.drop_duplicates(subset=['id_venta'])
        df['fecha'] = pd.to_datetime(df['fecha'], errors='coerce')
        for col_id in ['id_producto', 'id_cliente']:
            if col_id in cols:
                df[col_id] = pd.to_numeric(df[col_id], errors='coerce').fillna(0).astype(int)
        if 'cantidad' in cols:
            df['cantidad'] = pd.to_numeric(df['cantidad'], errors='coerce').fillna(1).astype(int)
        if 'medio_pago' in cols:
            df['medio_pago'] = df['medio_pago'].astype(str).str.strip().str.title()

    # 2. LÓGICA PARA INVENTARIO
    elif 'id_producto' in cols and 'producto' in cols:
        print("📦 Limpiando datos de Inventario...")
        df = df.drop_duplicates(subset=['id_producto'])
        if 'producto' in cols:
            df['producto'] = df['producto'].astype(str).str.strip().str.title()
        for col in ['categoria', 'talla', 'color']:
            if col in cols:
                df[col] = df[col].astype(str).str.strip().str.upper()
        if 'stock_actual' in cols:
            df['stock_actual'] = pd.to_numeric(df['stock_actual'], errors='coerce').clip(lower=0).fillna(0).astype(int)
        for col_precio in ['precio_adquisicion', 'precio_venta_unitario']:
            if col_precio in cols:
                df[col_precio] = pd.to_numeric(df[col_precio], errors='coerce').clip(lower=0).fillna(0.0)

    # 3. LÓGICA PARA CLIENTES (Corregida según image_f70c15.png)
    elif 'id_cliente' in cols:
        print("👥 Limpiando datos de Clientes (Estructura Local)...")
        
        # Eliminar duplicados por ID de cliente
        df = df.drop_duplicates(subset=['id_cliente'])
        
        # Normalizar Nombre (Ej: "Facundo Gomez")
        if 'nombre_cliente' in cols:
            df['nombre_cliente'] = df['nombre_cliente'].astype(str).str.strip().str.title()
            
        # Normalizar Ubicación (Ej: "Buenos Aires")
        if 'ubicacion_cliente' in cols:
            df['ubicacion_cliente'] = df['ubicacion_cliente'].astype(str).str.strip().str.title()
            
        # Normalizar Género: Tomar solo la primera letra en mayúscula (M, F)
        if 'genero' in cols:
            df['genero'] = df['genero'].astype(str).str.strip().str.upper().str[0]
            
        # Validar Fecha de Registro
        if 'fecha_registro' in cols:
            df['fecha_registro'] = pd.to_datetime(df['fecha_registro'], errors='coerce')
            
        # Normalizar Canal Preferido (Ej: "Instagram", "Web")
        if 'canal_preferido' in cols:
            df['canal_preferido'] = df['canal_preferido'].astype(str).str.strip().str.title()

    else:
        print("⚠️ No se reconoció el esquema. Se devuelve sin cambios.")

    return df