---
name: SQLAlchemy 2.0 ORM & Core
description: Guía, convenciones y mejores prácticas para integrar SQLAlchemy 2.0 (ORM y manejo de Engines) en aplicaciones Python.
---

# Skill: SQLAlchemy 2.0

## Propósito
Este skill permite diseñar, mapear e interactuar con bases de datos relacionales en Python de forma moderna, utilizando la API 2.0 de SQLAlchemy, tipado estricto (Type Hinting) en modelos ORM y manejo correcto de Sesiones (Unit of Work).

## Cuándo Usar
Activa este skill cuando necesites:
- Definir un nuevo esquema de base de datos relacional usando el paradigma `DeclarativeBase` y `Mapped[...]`.
- Conectarte a una base de datos PostgreSQL, SQLite u otras usando `create_engine`.
- Generar consultas tipo `SELECT`, `INSERT`, `UPDATE` o `JOIN` programáticamente.
- Manejar transacciones limpias dentro de bloques `with Session(engine) as session:`.

## Instrucciones

1. **Definir el Motor (Engine)**: Inicia la conectividad construyendo una URL de conexión válida (`dialect+driver://usuario:password@host/nombre_db`) y utiliza `create_engine()`. Usa `echo=True` sólo en entornos de depuración.
2. **Crear la Clase Base Declarativa**: Todos los modelos deben derivar de una clase vacía que herede de `sqlalchemy.orm.DeclarativeBase`.
3. **Mapeo de Tipos 2.0**: Utiliza siempre `Mapped[<Type>]` junto con `mapped_column()` para atributos de la tabla de la BD. Para nulos, utiliza `Optional[Type]`.
4. **Relaciones Estrictas**: Usa `relationship()` indicando `back_populates` (nunca `backref` legacy) en ambos sentidos para integridad de Mypy en memoria, y la colección envuelta en tipados genéricos `List["ClaseDestino"]`. Utiliza `cascade="all, delete-orphan"` en el padre si los hijos dependen estrictamente de él.
5. **Sesiones, Borrados y Flushes**: 
   - Abre siempre la conexión con `with Session(engine) as session:` (Context Manager).
   - Para insertar usa `session.add()`. 
   - Para borrar usa `session.delete(objeto)`. Esto no borra de la BD de inmediato, solo pre-expira el objeto en la memoria (Unit of Work).
   - Puedes usar `session.flush()` si necesitas que SQLAlchemy force el INSERT/DELETE al motor SQL intermedio para obtener los `ID`s generados sin comitear aún la transacción final.
   - Ejecuta las queries con `session.execute(stmt).scalars().all()`.
   - Finaliza con `session.commit()`.

## Ejemplos
Ver la carpeta `examples/` para casos prácticos como creación de tablas, inserción de datos y operaciones con JOINs.

## Resources
Ver `resources/knowledge-source.md` para la documentación completa obtenida de SQLAlchemy official documentation 2.0.

## Logs Requeridos en tu código
Si implementas lógica usando este skill en un proyecto, recuerda:
- Usar un bloque try-except rodeando operaciones transaccionales para aplicar `session.rollback()` si ocurre un error antes de un `session.commit()`.
