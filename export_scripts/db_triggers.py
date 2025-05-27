from sqlalchemy import create_engine, text

DATABASE_URL = "sqlite:///db.sqlite3"  
engine = create_engine(DATABASE_URL)

def crear_triggers(engine):
    print("Ejecutando creación de triggers...")  
    with engine.begin() as connection:  
        connection.execute(text("""
            CREATE TRIGGER IF NOT EXISTS actualizar_disponibilidad_al_prestar
            AFTER INSERT ON prestamos
            BEGIN
                UPDATE libros
                SET disponible = 0
                WHERE id = NEW.libro_id;
            END;
        """))
        connection.execute(text("""
            CREATE TRIGGER IF NOT EXISTS actualizar_disponibilidad_al_devolver
            AFTER UPDATE ON prestamos
            WHEN NEW.fecha_devolucion IS NOT NULL
            BEGIN
                UPDATE libros
                SET disponible = 1
                WHERE id = NEW.libro_id;
            END;
        """))
    print("Triggers creados correctamente.")
