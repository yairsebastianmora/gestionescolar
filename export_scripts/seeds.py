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

# Crear autores y libros de prueba
autor1 = Autor(nombre="Gabriel García Márquez")
autor2 = Autor(nombre="Isabel Allende")

libro1 = Libro(titulo="Cien años de soledad", autor=autor1)
libro2 = Libro(titulo="La casa de los espíritus", autor=autor2)

# Agregar a la sesión
session.add(autor1)
session.add(autor2)
session.add(libro1)
session.add(libro2)

# Confirmar los cambios en la base de datos
session.commit()

print("Datos de prueba añadidos exitosamente.")

session.close()
