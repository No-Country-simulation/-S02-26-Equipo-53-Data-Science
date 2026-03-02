from typing import Optional
import datetime
from sqlalchemy import String, Integer, Numeric, DateTime, Date, text
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column

class Base(DeclarativeBase):
    pass

# Modelos del esquema 'raw'

class VentaRaw(Base):
    __tablename__ = "ventas_raw"
    __table_args__ = {'schema': 'raw'}
    
    id_venta: Mapped[int] = mapped_column(primary_key=True)
    fecha: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime)
    id_producto: Mapped[Optional[int]] = mapped_column(Integer)
    id_cliente: Mapped[Optional[int]] = mapped_column(Integer)
    cantidad: Mapped[Optional[int]] = mapped_column(Integer)
    medio_pago: Mapped[Optional[str]] = mapped_column(String(50))
    fecha_carga: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime, server_default=text("CURRENT_TIMESTAMP"))

class InventarioRaw(Base):
    __tablename__ = "inventario_raw"
    __table_args__ = {'schema': 'raw'}
    
    id_producto: Mapped[int] = mapped_column(primary_key=True)
    producto: Mapped[Optional[str]] = mapped_column(String(150))
    categoria: Mapped[Optional[str]] = mapped_column(String(100))
    talla: Mapped[Optional[str]] = mapped_column(String(10))
    color: Mapped[Optional[str]] = mapped_column(String(50))
    stock_actual: Mapped[Optional[int]] = mapped_column(Integer)
    precio_adquisicion: Mapped[Optional[float]] = mapped_column(Numeric(10, 2))
    precio_venta_unitario: Mapped[Optional[float]] = mapped_column(Numeric(10, 2))
    fecha_carga: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime, server_default=text("CURRENT_TIMESTAMP"))

class ClienteRaw(Base):
    __tablename__ = "clientes_raw"
    __table_args__ = {'schema': 'raw'}
    
    id_cliente: Mapped[int] = mapped_column(primary_key=True)
    nombre_cliente: Mapped[Optional[str]] = mapped_column(String(150))
    ubicacion_cliente: Mapped[Optional[str]] = mapped_column(String(150))
    genero: Mapped[Optional[str]] = mapped_column(String(20))
    fecha_registro: Mapped[Optional[datetime.date]] = mapped_column(Date)
    canal_preferido: Mapped[Optional[str]] = mapped_column(String(50))
    fecha_carga: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime, server_default=text("CURRENT_TIMESTAMP"))
