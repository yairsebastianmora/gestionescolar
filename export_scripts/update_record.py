import sys
import os

# Asegúrate de que Python pueda acceder a la carpeta raíz del proyecto
script_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.abspath(os.path.join(script_dir, '..'))
sys.path.insert(0, project_root)

from database import Session
from models import Libro

# Crear una sesión
session = Session()

# Actualizar la disponibilidad de un libro
libro_id = 1  # Aquí pones el ID del libro que deseas actualizar
libro = session.query(Libro).filter(Libro.id == libro_id).first()

if libro:
    libro.disponible = not libro.disponible  # Cambiar disponibilidad
    session.commit()
    print(f"Libro '{libro.titulo}' actualizado. Disponibilidad ahora: {'Sí' if libro.disponible else 'No'}")
else:
    print(f"No se encontró el libro con ID {libro_id}.")

session.close()
