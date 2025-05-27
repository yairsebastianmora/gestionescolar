import sys
import os


script_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.abspath(os.path.join(script_dir, '..'))
sys.path.insert(0, project_root)


from database import Session
from models import Autor, Libro


session = Session()


nuevo_autor = Autor(nombre="Gabriel García Márquez")
nuevo_libro = Libro(titulo="Cien años de soledad", autor=nuevo_autor)


session.add(nuevo_autor)
session.add(nuevo_libro)
session.commit()

print("Autor y libro añadidos exitosamente.")



