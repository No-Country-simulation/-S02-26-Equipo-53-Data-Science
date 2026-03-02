# Ejemplo: Creación, Inserción y Consulta Básica (SQLAlchemy 2.0)

## Contexto
Este ejemplo demuestra cómo declarar dos entidades relacionales (Usuario y Dirección) utilizando sintaxis moderna `Mapped`, y cómo usar `Session` y constructores `select()` para insertar y extraer información.

## Proceso

```python
from typing import List, Optional
from sqlalchemy import create_engine, select, String, ForeignKey
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship, Session

# 1. Base declarativa
class Base(DeclarativeBase):
    pass

# 2. Definición de Modelos fuertemente tipados
class User(Base):
    __tablename__ = "users"
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(30))
    fullname: Mapped[Optional[str]]
    
    addresses: Mapped[List["Address"]] = relationship(back_populates="user", cascade="all, delete-orphan")

class Address(Base):
    __tablename__ = "addresses"
    id: Mapped[int] = mapped_column(primary_key=True)
    email: Mapped[str]
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    
    user: Mapped["User"] = relationship(back_populates="addresses")

# 3. Creación del motor en memoria y tablas
engine = create_engine("sqlite:///:memory:", echo=False)
Base.metadata.create_all(engine)

# 4. Transaccionalidad
with Session(engine) as session:
    # --- Insertar ---
    new_user = User(name="alice", fullname="Alice Smith")
    new_address = Address(email="alice@example.com", user=new_user)
    
    session.add(new_user) # new_address se agrega implícitamente por el relationship cascade
    session.commit()
    
    # --- Consultar ---
    stmt = select(User).where(User.name == "alice")
    alice_db = session.scalars(stmt).first()
    
    print(f"Encontrado: {alice_db.fullname} con {len(alice_db.addresses)} direcciones.")
```

## Puntos Destacados
- Se utiliza `Session()` en bloque estricto `with` para controlar el auto-cierre del pool.
- Modelos 100% compatibles con `mypy` usando `Mapped[T]`.
- Se usa `scalars().first()` para evitar recibir tuplas de resultado en lugar de instancias limpias de ORM.
