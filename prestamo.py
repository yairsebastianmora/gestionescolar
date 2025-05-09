from sqlalchemy import Column, Integer, String, Date, ForeignKey, create_engine, Boolean, func, desc
from sqlalchemy.orm import relationship, sessionmaker, declarative_base
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

def init_db():
    engine = create_engine('sqlite:///biblioteca.db')
    Base.metadata.create_all(engine)
    return engine

def autor_con_mas_libros(session):
    resultado = session.query(Autor.nombre, func.count(Libro.id).label("total"))\
                       .join(Libro).group_by(Autor.id)\
                       .order_by(desc("total")).first()
    if resultado:
        print(f"Autor con más libros: {resultado.nombre} ({resultado.total} libros)")
    else:
        print("No hay autores registrados.")

def menu():
    engine = init_db()
    Session = sessionmaker(bind=engine)
    session = Session()

    while True:
        print("""
        ===== MENÚ BIBLIOTECA =====
        1. Registrar autor
        2. Registrar libro
        3. Registrar usuario
        4. Prestar libro
        5. Devolver libro
        6. Ver libros prestados
        7. Buscar libros por título
        8. Autor con más libros
        9. Salir
        """)
        opcion = input("Selecciona una opción: ")

        if opcion == '1':
            nombre = input("Nombre del autor: ")
            session.add(Autor(nombre=nombre))
            session.commit()

        elif opcion == '2':
            titulo = input("Título del libro: ")
            autor_id = int(input("ID del autor: "))
            session.add(Libro(titulo=titulo, autor_id=autor_id))
            session.commit()

        elif opcion == '3':
            nombre = input("Nombre del usuario: ")
            session.add(Usuario(nombre=nombre))
            session.commit()

        elif opcion == '4':
            libro_id = int(input("ID del libro: "))
            usuario_id = int(input("ID del usuario: "))
            libro = session.query(Libro).get(libro_id)
            if libro and libro.disponible:
                prestamo = Prestamo(libro_id=libro_id, usuario_id=usuario_id)
                libro.disponible = False
                session.add(prestamo)
                session.commit()
                print("Préstamo registrado.")
            else:
                print("Libro no disponible o inexistente.")

        elif opcion == '5':
            prestamo_id = int(input("ID del préstamo a devolver: "))
            prestamo = session.query(Prestamo).get(prestamo_id)
            if prestamo and prestamo.fecha_devolucion is None:
                prestamo.fecha_devolucion = date.today()
                prestamo.libro.disponible = True
                session.commit()
                print("Libro devuelto.")
            else:
                print("Préstamo no válido o ya devuelto.")

        elif opcion == '6':
            prestamos = session.query(Prestamo).filter(Prestamo.fecha_devolucion == None).all()
            for p in prestamos:
                print(f"Libro: {p.libro.titulo}, Usuario: {p.usuario.nombre}, Fecha: {p.fecha_prestamo}")

        elif opcion == '7':
            titulo = input("Título del libro a buscar: ")
            libros = session.query(Libro).filter(Libro.titulo.contains(titulo)).all()
            for libro in libros:
                print(f"ID: {libro.id}, Título: {libro.titulo}, Autor: {libro.autor.nombre}, Disponible: {libro.disponible}")

        elif opcion == '8':
            autor_con_mas_libros(session)

        elif opcion == '9':
            break

        else:
            print("Opción no válida.")

if __name__ == '__main__':
    menu()
