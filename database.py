import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Ruta absoluta para la base de datos
basedir = os.path.abspath(os.path.dirname(__file__))
db_path = os.path.join(basedir, 'instance', 'tus_datos.db')
engine = create_engine(f'sqlite:///{db_path}', echo=True)

Session = sessionmaker(bind=engine)