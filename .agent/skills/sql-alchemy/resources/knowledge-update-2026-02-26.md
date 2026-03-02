# Actualización de Conocimiento: SQLAlchemy
**URL de origen:** 
- https://docs.sqlalchemy.org/en/20/orm/quickstart.html
- https://docs.sqlalchemy.org/en/20/orm/relationship_api.html

**Fecha de captura:** 2026-02-26

## Diferencias con la versión anterior
- Especificación profunda de `cascade="all, delete-orphan"` para borrado en cascada.
- Profundización en Lazy Loading explícito en ORM: el acceso a colecciones (como `usuario.direcciones`) emite queries automáticamente y puede ajustarse mediante *Loader Strategies*.
- Especificación en el uso de `back_populates` en `relationship()`. La documentación remarca que en Python moderno (y PEP 484 type hints), el uso de `back_populates` es obligado y más estricto frente al uso legacy (ahora obsoleto) de `backref()` para evitar problemas con MyPy.
- Explicación táctica del Unit of Work en Deletes: `session.delete(obj)` no borra de la BD inmediatamente; marca el objeto como *expired*. Se requiere `session.flush()` o `session.commit()` para efectuar el SQL `DELETE`.

## Contenido Técnico Nuevo
### Manejo de Estados y Flush (Unit Of Work Avanzado)
```python
sandy = session.get(User, 2)
# Elimina un hijo de la colección asumiendo cascade delete-orphan configurado
sandy.addresses.remove(sandy_address)

# Fuerza emisión de los SQL DELETE en la base de datos sin convalidar transacción final todavía
session.flush()

# Marca el padre para borrado completo. (Lazy loads los hijos primero para aplicar cascade).
session.delete(patrick)

# Finaliza transacción (emite todos los deletes en bloque).
session.commit()
```

### Reglas para Relationship() moderno
La API exige que se defina bidireccionalmente:
```python
class SomeClass(Base):
    # La variable es recomendada con colección typing moderno (PEP 484)
    related_items: Mapped[List["RelatedItem"]] = relationship(back_populates="parent")

class RelatedItem(Base):
    parent: Mapped["SomeClass"] = relationship(back_populates="related_items")
```
- No usar `backref` como string mágico, usar `back_populates` obligatoriamente entre las dos clases para integrarlo correctamente a las anotaciones `Mapped[T]`.
