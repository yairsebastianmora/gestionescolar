import sqlite3
import os

# Ruta absoluta a la base de datos
basedir = os.path.abspath(os.path.dirname(__file__))
db_path = os.path.join(basedir, 'instance', 'tus_datos.db')

conn = sqlite3.connect(db_path)
c = conn.cursor()

try:
    c.execute("ALTER TABLE tareas ADD COLUMN archivo TEXT;")
    print("Columna 'archivo' agregada correctamente a la tabla tareas.")
except sqlite3.OperationalError as e:
    if 'duplicate column name' in str(e):
        print("La columna 'archivo' ya existe.")
    else:
        print("Error al agregar la columna:", e)

conn.commit()
conn.close()
