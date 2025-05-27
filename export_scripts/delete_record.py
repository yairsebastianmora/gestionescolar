import sys
import os


script_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.abspath(os.path.join(script_dir, '..'))
sys.path.insert(0, project_root)

from database import Session
from models import Autor, Libro


session = Session()


autor_id = 1  
autor = session.query(Autor).filter(Autor.id == autor_id).first()

if autor:
    
    for libro in autor.libros:
        session.delete(libro)
    session.delete(autor)
    session.commit()
    print(f"Autor '{autor.nombre}' y sus libros han sido eliminados.")
else:
    print(f"No se encontró el autor con ID {autor_id}.")

session.close()
