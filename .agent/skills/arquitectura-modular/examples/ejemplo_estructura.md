# Ejemplo de Estructura de Directorios

```text
/
├── .agent/
├── libs/
│   ├── db_connection.py
│   └── logger.py
├── modules/
│   ├── sales/              <-- Feature A
│   │   ├── __init__.py
│   │   ├── ui.py
│   │   └── logic.py
│   └── inventory/          <-- Feature B
│       ├── __init__.py
│       └── dashboard.py
├── pages/
│   ├── 01_Sales.py         <-- Wrapper A
│   └── 02_Inventory.py     <-- Wrapper B
├── main.py                 <-- Landing Page
└── requirements.txt
```

## Wrapper Example (pages/01_Sales.py)

```python
import streamlit as st
from modules.sales.ui import render_sales_ui

st.set_page_config(page_title="Sales", layout="wide")

if __name__ == "__main__":
    render_sales_ui()
```
