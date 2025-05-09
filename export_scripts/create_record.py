import sys
import os

# Asegurarte de que Python pueda acceder a la carpeta raíz del proyecto
script_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.abspath(os.path.join(script_dir, '..'))
sys.path.insert(0, project_root)

# Ahora puedes importar tus módulos
from database import Session
from models import Autor, Libro

# Crear una sesión
session = Session()

# Crear un nuevo autor y libro
nuevo_autor = Autor(nombre="Gabriel García Márquez")
nuevo_libro = Libro(titulo="Cien años de soledad", autor=nuevo_autor)

# Agregar y guardar
session.add(nuevo_autor)
session.add(nuevo_libro)
session.commit()

print("Autor y libro añadidos exitosamente.")



