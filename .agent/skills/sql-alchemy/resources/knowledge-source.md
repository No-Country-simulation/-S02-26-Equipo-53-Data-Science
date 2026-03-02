# Documentación Capturada: SQLAlchemy

**URL de origen:** 
- https://docs.sqlalchemy.org/en/20/orm/quickstart.html
- https://docs.sqlalchemy.org/en/20/core/engines.html

**Fecha de captura:** 2026-02-26

## ORM Quick Start & Declarative Models
SQLAlchemy 2.0 defines database structure using `DeclarativeBase` and `Mapped` column typing.
```python
from typing import List, Optional
from sqlalchemy import ForeignKey, String
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship

class Base(DeclarativeBase):
    pass

class User(Base):
    __tablename__ = "user_account"
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(30))
    fullname: Mapped[Optional[str]]
    addresses: Mapped[List["Address"]] = relationship(back_populates="user", cascade="all, delete-orphan")

class Address(Base):
    __tablename__ = "address"
    id: Mapped[int] = mapped_column(primary_key=True)
    email_address: Mapped[str]
    user_id: Mapped[int] = mapped_column(ForeignKey("user_account.id"))
    user: Mapped["User"] = relationship(back_populates="addresses")
```

## Creating an Engine (Connectivity)
The `Engine` is the starting point for any SQLAlchemy application. It’s a factory for `Connection` and holds a `Connection Pool`.
```python
from sqlalchemy import create_engine
engine = create_engine("sqlite+pysqlite:///:memory:", echo=True)
```
*Note: Depending on DB dialect, URLs follow `dialect+driver://user:pass@host:port/dbname`.*

## Persisting and Selecting Data 
Objects are persisted to DB using `Session`. `select()` function builds the Core `Select` statement, and `session.scalars()` iterates objects.
```python
from sqlalchemy.orm import Session
from sqlalchemy import select

with Session(engine) as session:
    # Inserts
    spongebob = User(name="spongebob", fullname="Spongebob Squarepants")
    session.add(spongebob)
    session.commit()
    
    # Selects
    stmt = select(User).where(User.name.in_(["spongebob", "sandy"]))
    for user in session.scalars(stmt):
        print(user)
        
    # Joins
    stmt = select(Address).join(Address.user).where(User.name == "sandy")
    sandy_address = session.scalars(stmt).one()
```
