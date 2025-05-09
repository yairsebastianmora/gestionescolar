import sys
import os

# Asegúrate de que Python pueda acceder a la carpeta raíz del proyecto
script_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.abspath(os.path.join(script_dir, '..'))
sys.path.insert(0, project_root)

from database import Session
from models import Autor, Libro

# Crear una sesión
session = Session()

# Eliminar un autor (y los libros asociados si la relación está configurada con cascada)
autor_id = 1  # Aquí pones el ID del autor que deseas eliminar
autor = session.query(Autor).filter(Autor.id == autor_id).first()

if autor:
    # Eliminar los libros asociados al autor
    for libro in autor.libros:
        session.delete(libro)
    session.delete(autor)
    session.commit()
    print(f"Autor '{autor.nombre}' y sus libros han sido eliminados.")
else:
    print(f"No se encontró el autor con ID {autor_id}.")

session.close()
