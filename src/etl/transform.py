import pandas as pd

def clean_dataframe(df):
    """
    Detecta automáticamente si el DataFrame es de Ventas, Inventario o Clientes
    y aplica las reglas de limpieza correspondientes.
    """
    if df.empty:
        return df

    # --- IDENTIFICACIÓN POR COLUMNAS ---
    cols = df.columns.tolist()

    # 1. LÓGICA PARA VENTAS
    if 'id_venta' in cols or 'precio_venta_unitario' in cols:
        print("✨ Limpiando datos de Ventas...")
        df = df.drop_duplicates(subset=['id_venta']) if 'id_venta' in cols else df.drop_duplicates()
        df['fecha'] = pd.to_datetime(df['fecha'], errors='coerce')
        df['cantidad'] = pd.to_numeric(df['cantidad'], errors='coerce').fillna(1)
        df['precio_venta_unitario'] = pd.to_numeric(df['precio_venta_unitario'], errors='coerce').fillna(0.0)
        # Limpieza de texto en medio de pago
        if 'medio_pago' in cols:
            df['medio_pago'] = df['medio_pago'].str.strip().str.capitalize()

    # 2. LÓGICA PARA INVENTARIO
    elif 'id_producto' in cols or 'stock_actual' in cols:
        print("📦 Limpiando datos de Inventario...")
        df = df.drop_duplicates(subset=['id_producto']) if 'id_producto' in cols else df.drop_duplicates()
        # Estandarización de Categoría, Talla y Color
        for col in ['categoria', 'talla', 'color']:
            if col in cols:
                df[col] = df[col].astype(str).str.strip().str.upper()
        # Validar que los stocks no sean negativos
        df['stock_actual'] = pd.to_numeric(df['stock_actual'], errors='coerce').clip(lower=0).fillna(0)
        df['precio_adquisicion'] = pd.to_numeric(df['precio_adquisicion'], errors='coerce').fillna(0.0)

    # 3. LÓGICA PARA CLIENTES
    elif 'id_cliente' in cols or 'nombre_cliente' in cols:
        print("👥 Limpiando datos de Clientes...")
        df = df.drop_duplicates(subset=['id_cliente']) if 'id_cliente' in cols else df.drop_duplicates()
        df['nombre_cliente'] = df['nombre_cliente'].str.strip().str.title()
        # Normalizar género a una sola letra (M, F, U)
        if 'genero' in cols:
            df['genero'] = df['genero'].str.strip().str.upper().str[0]
        # Limpiar ubicación (Quitar ", Lima" si existe)
        if 'ubicacion_cliente' in cols:
            df['ubicacion_cliente'] = df['ubicacion_cliente'].str.replace(r'(?i),?\s*lima', '', regex=True).str.strip().str.title()

    else:
        print("⚠️ Advertencia: No se reconoció el esquema de la tabla. Se devuelve sin cambios.")

    return df