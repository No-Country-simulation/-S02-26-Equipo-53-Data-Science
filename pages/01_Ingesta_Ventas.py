from modules.ingesta_ventas.app import main

if __name__ == "__main__":
    st.set_page_config(
        page_title="Ingesta de Ventas",
        page_icon="🎙️",
        layout="wide"
    )
    main()
