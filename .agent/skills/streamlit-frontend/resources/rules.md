# Reglas: Streamlit Frontend

1. **Responsividad:** Siempre asume que la app puede verse en diferentes tamaños. Usa `layout="wide"` solo si la cantidad de datos lo justifica.
2. **Naming de Widgets:** Los `key` de los widgets deben ser descriptivos y usar `snake_case` (Ej: `st.text_input("Nombre", key="user_name_input")`).
3. **Icons:** Usa emojis o iconos integrados para mejorar la navegación en `st.navigation`.
4. **No HTML sucio:** Evita inyectar HTML complejo. Si necesitas algo muy avanzado, considera un Componente Personalizado.
5. **Labels Claras:** Todos los inputs deben tener labels claras y, preferiblemente, `help` text para guiar al usuario.
