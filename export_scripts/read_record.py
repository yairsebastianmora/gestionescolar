import sys
import os


script_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.abspath(os.path.join(script_dir, '..'))
sys.path.insert(0, project_root)

from database import Session
from models import Autor, Libro


session = Session()


autores = session.query(Autor).all()
for autor in autores:
    print(f"Autor: {autor.nombre}")


libros = session.query(Libro).all()
for libro in libros:
    print(f"Libro: {libro.titulo}, Autor: {libro.autor.nombre}, Disponible: {'Sí' if libro.disponible else 'No'}")

session.close()

