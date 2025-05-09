from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models import Base  # Asegúrate de que esto importa bien tus modelos

# Crear el motor de base de datos
engine = create_engine('sqlite:///biblioteca.db', echo=True)

# Crear la clase Session
Session = sessionmaker(bind=engine)

# Crear las tablas (solo una vez)
Base.metadata.create_all(engine)