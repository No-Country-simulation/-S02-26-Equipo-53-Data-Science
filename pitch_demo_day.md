# ⏱️ Pitch de 4 Minutos - Demo Day Datamark

*(Este guion está cronometrado a una velocidad de habla normal-pausada. Las palabras en **negrita** son para hacer énfasis en la entonación).*

---

### [Minuto 0:00 - 0:45] El Gancho y El Problema 🪝

"Hola a todos. Imaginen por un momento a María. María es dueña de una tienda de ropa en Arequipa. Trabaja 12 horas al día, atiende clientes, recibe mercancía y, al final de la jornada, tiene que cuadrar su caja registradora usando papel, lápiz y, con suerte, un Excel desordenado que casi nunca actualiza. 

Esa es la realidad de miles de pequeños y medianos emprendedores en provincias del Perú. Toman decisiones de negocio **completamente a ciegas** porque no tienen métricas claras, sufren de quiebres de stock y pierden muchísimo tiempo en tareas operativas propensas a errores humanos. 

¿Por qué? Porque las licencias de software contable tradicionales son caras, complejas e intimidantes."

### [Minuto 0:45 - 1:15] La Solución y el Objetivo 🎯

"Es aquí donde nace **DATAMARK**, nuestro SaaS B2B en etapa MVP. 

Nuestro objetivo es democratizar la Inteligencia de Negocios y la Ingeniería de Datos para el sector retail local. Actuamos como un **Data Analyst Automatizado** en el bolsillo del emprendedor. Centralizamos sus datos contables sucios y los transformamos, casi por arte de magia, en **dashboards ejecutivos claros** en tiempo real. Reducimos el error operativo casi a cero."

### [Minuto 1:15 - 2:00] Funciones Clave (Cómo lo usa el usuario) 📲

"¿Cómo usamos un sistema complejo de manera sencilla? 
María no necesita aprender complicadas consultas, botones ocultos o macros. 

Simplemente abre nuestra plataforma web en su celular desde el mostrador, toca un botón y le dice en voz alta: *'Vendí dos polos blancos talla M a Fernando por 50 soles'*. **¡Y listo!** 

Ese es nuestro punto diferenciador: la **Ingesta Inteligente de Datos**. Soportamos comandos de voz naturales, textos masivos e importaciones de Excel que el dueño solo arrastra a la pantalla. Además, la plataforma no le permite cometer errores graves: si María intenta vender un pantalón que ya no existe en el sistema, Datamark levanta una barrera por inventario insuficiente. Una vez que aprueba su venta diaria, con un solo click se dibuja su panel de análisis mensual."

### [Minuto 2:00 - 2:45] La Tecnología Sobresaliente y la IA 🧠

"Sabíamos que para lograr esta simplicidad extrema, necesitábamos una capa tecnológica brutal al fondo. 

Para interpretar mágicamente la voz de la vendedora introdujimos la tecnología más vanguardista: The Generative AI. Utilizamos la **API de Google Gemini 1.5 y 2.5 Flash**, que ejerce como el cerebro que procesa lenguaje natural no estructurado (*'dos polos a fernando'*) e infiere qué producto es, qué cantidad, y lo mapea automáticamente en un formato JSON exacto en fracciones de segundo. 

Y como las máquinas pueden equivocarse al entender letras locales, incorporamos algoritmos de coincidencia difusa, o *Fuzzy Matching*, que unen inteligentemente la interpretación de Gemini con el catálogo base de nuestro cliente. Y todo sin que María haya tecleado ni una palabra."

### [Minuto 2:45 - 3:45] La Arquitectura y El Pipeline (Nivel Técnico) 🏗️

"Para que la plataforma soporte cargas de datos continuas y visualice los gráficos analíticos, diseñamos un ecosistema de datos robusto albergado en la nube con **Aiven for PostgreSQL**.

Nuestro **Data Pipeline (ETL)** funciona a través de 5 hitos en 3 capas de esquemas puros en la base de datos:
1. **El RAW Transaccional:** Donde el dictado de María se inserta de forma inmutable a través de SQL puro, garantizando ACID.
2. **La Extracción:** Lee remotamente esas tablas caóticas y las trae a Dataframes.
3. **El Transformer ETL con Pandas:** Donde ejecutamos toda la limpieza de nulos y cast de datos *en memoria RAM*.
4. **La Carga a Staging & Validación:** Puliendo la Calidad y asegurando que ninguna venta pierda a su cliente (*Integridad referencial*).
5. **Y finalmente, el Data Warehouse Estrella:** El modelo dimensional donde alojamos las Tablas de Hechos consolidadas, preparadas exclusivamente para consumo analítico hiper-rápido usando **Streamlit Community Cloud** y gráficos en **Plotly**.

Todo el frontend y servidor es orquestado por **Python**, manteniendo un entorno de altísima escalabilidad pero de extrema pureza de desarrollo."

### [Minuto 3:45 - 4:00] El Cierre 🚀

**Datamark** no es solo una calculadora avanzada. Es devolverle a los emprendedores locales las docenas de horas a la semana que pierden administrando, para que las inviertan en liderar sus negocios, apoyados por el flujo tecnológico gratuito y modular más sofisticado del mercado actual.

Muchas gracias."
