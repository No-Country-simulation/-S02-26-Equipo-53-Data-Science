# 🧪 Guía Práctica de Pruebas Integrales (Local)

Esta guía te ayudará a probar el flujo completo ("End-to-End") de la aplicación: desde que ingresas un dato (tu desarrollo) hasta que se refleja en los gráficos (desarrollo de tus compañeros).

---

## 🚀 PASO 1: Iniciar la Aplicación

1.  Abre tu terminal.
2.  Asegúrate de estar en el entorno virtual (`.env`).
3.  Ejecuta el archivo principal:
    ```bash
    streamlit run main.py
    ```
4.  Se abrirá tu navegador web mostrando la **Página Principal (Landing Page)** que hicieron tus compañeros. 
    * _Aquí puedes probar que el texto y los botones de inicio cargan correctamente._

---

## 📥 PASO 2: Ingesta de Datos (Tu Parte)

Desde la barra lateral (menú de la izquierda), navega a: **`01_Ingesta_Ventas`**.

Aquí es donde tu magia (resolución determinista, regex, alertas visuales) sucede. Prueba los siguientes escenarios:

### Escenario A: Ingesta por Lotes (Excel)
1. Ve a la pestaña de **Carga Inteligente por Lotes**.
2. Sube el archivo de prueba: `test_data/ventas_muestra.csv` (o cualquier otro Excel/CSV).
3. **Punto de control interactivo:** Verifica que el Data Editor (grilla) aparezca.
4. **Verifica tus validaciones:** ¿Aparecen celdas rojas para datos faltantes? ¿Aparece la columna `_warning` alertando si un producto es ambiguo (ej. varias tallas disponibles)?
5. Haz clic en **Guardar Registros RAW**. 
    * _Con esto, los datos quedan en tu esquema transaccional: `raw.ventas_raw`._

### Escenario B: Ingreso Manual tradicional (Opcional)
1. Ve a la pestaña **👆 Ingreso Manual**.
2. Llena un formulario usando el botón "Seleccionar Producto Existente". Elige un producto, pon una cantidad y un ID de cliente.
3. Haz clic en Guardar.
    * _Verifica que no salgan errores rojos tipo "KeyError" o "Stock Insuficiente" (a menos que lo fuerces a fallar)._

---

## ⚙️ PASO 3: Ejecutar el ETL (Parte de tus Compañeros)

Ahora los datos están crudos (`raw`). Hay que transformarlos y moverlos al almacén (`warehouse`) para que los gráficos los lean.

Desde la barra lateral, navega a: **`dashboard`**.

1. Verás el panel vacío o con datos antiguos.
2. En la parte superior, busca el botón **"🔄 Actualizar datos"**. *(Este botón fue creado por tus compañeros en `modules/dashboard/dashboard_logic.py`)*.
3. Haz clic en él.
    * _Lo que hace por debajo es: Ejecutar el orquestador (`scripts/orchestrator.py`) -> Extraer de tus tablas `raw` -> Limpiar (Transform) -> Cargar en `staging` -> Cargar al `warehouse`._
4. Espera a que el mensaje diga **"✅ Datos actualizados correctamente"**.

---

## 📈 PASO 4: Validar el Analista Visual (Parte de tus Compañeros)

Ya en el **`dashboard`**, con el ETL ejecutado exitosamente, prueba lo siguiente:

1. **Selector de Fechas:** Cambia el rango de fechas en la parte superior. 
    * _Verifica que los números de los 4 KPIs (Ventas Totales, Unidades, etc.) cambien dinámicamente según la fecha._
2. **Gráfico Top 10 Productos:** ¿El producto que ingresaste manualmente o por Excel en el Paso 2 aparece aquí si tú fuiste quien más lo vendió?
3. **Gráficos de Dona/Barras:** Revisa si la "Venta por Talla" o "Venta por Color" tienen sentido (los colores y tallas que rescatamos con tu Regex ahora se grafican aquí).

---

## 🕵️‍♂️ PASO 5: Diagnóstico Interno

Si en el Paso 4 algo no cuadra (por ejemplo, el gráfico está vacío), puedes revisar directamente la base de datos sin salir de tu código.

Navega a: **`02_Gestion_Dueño`**.
1. En la pestaña principal, puedes ver la grilla interactiva de **Inventario y Ventas Actuales** (tu desarrollo).
2. Asegúrate de que las columnas `talla` y `color` no estén vacías (tu Regex funcionó).
3. Asegúrate de que tu columna `⚠️ Aviso` marque los productos correctamente insertados o observe si hay alguna advertencia.

---

### Resumen del Flujo de la Prueba:
`main.py` -> `01_Ingesta_Ventas` (TU PARTE) -> `dashboard` -> Clic en `Actualizar datos` (SU PARTE ETL) -> Ver Gráficos (SU PARTE VISUAL).
