# models.py
from sqlalchemy import Column, Integer, String, Date, ForeignKey, Boolean
from sqlalchemy.orm import relationship, declarative_base
from sqlalchemy.ext.declarative import declarative_base
from datetime import date

Base = declarative_base()

class Autor(Base):
    __tablename__ = 'autores'
    id = Column(Integer, primary_key=True)
    nombre = Column(String, nullable=False)
    libros = relationship("Libro", back_populates="autor")

class Libro(Base):
    __tablename__ = 'libros'
    id = Column(Integer, primary_key=True)
    titulo = Column(String, nullable=False)
    autor_id = Column(Integer, ForeignKey('autores.id'))
    disponible = Column(Boolean, default=True)
    autor = relationship("Autor", back_populates="libros")
    prestamos = relationship("Prestamo", back_populates="libro")

class Usuario(Base):
    __tablename__ = 'usuarios'
    id = Column(Integer, primary_key=True)
    nombre = Column(String, nullable=False)
    documento_identidad = Column(String, unique=True, nullable=False)  # Nuevo campo
    correo = Column(String, unique=True, nullable=False)  # Nuevo campo
    prestamos = relationship("Prestamo", back_populates="usuario")
class Prestamo(Base):
    __tablename__ = 'prestamos'
    id = Column(Integer, primary_key=True)
    libro_id = Column(Integer, ForeignKey('libros.id'))
    usuario_id = Column(Integer, ForeignKey('usuarios.id'))
    fecha_prestamo = Column(Date, default=date.today)
    fecha_devolucion = Column(Date, nullable=True)

    libro = relationship("Libro", back_populates="prestamos")
    usuario = relationship("Usuario", back_populates="prestamos")
