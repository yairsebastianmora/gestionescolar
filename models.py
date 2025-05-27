# models.py
from flask_sqlalchemy import SQLAlchemy
from datetime import date

db = SQLAlchemy()

class Usuario(db.Model):
    __tablename__ = 'usuarios'
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String, nullable=False)
    documento_identidad = db.Column(db.String, unique=True, nullable=False)
    correo = db.Column(db.String, unique=True, nullable=False)
    password = db.Column(db.String, nullable=False)

class Materia(db.Model):
    __tablename__ = 'materias'
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String, nullable=False)
    docente = db.Column(db.String)
    horario = db.Column(db.String)
    aula = db.Column(db.String)
    usuario_id = db.Column(db.Integer, db.ForeignKey('usuarios.id'))  # Relaciona la materia con el usuario
    tareas = db.relationship('Tarea', backref='materia', lazy=True)

class Tarea(db.Model):
    __tablename__ = 'tareas'
    id = db.Column(db.Integer, primary_key=True)
    titulo = db.Column(db.String)
    fecha_entrega = db.Column(db.Date)
    estado = db.Column(db.String)
    descripcion = db.Column(db.String)
    materia_id = db.Column(db.Integer, db.ForeignKey('materias.id'))
    usuario_id = db.Column(db.Integer, db.ForeignKey('usuarios.id'))  # Relaciona la tarea con el usuario
    archivo = db.Column(db.String)  # Ruta del archivo adjunto

class EventoPersonalizado(db.Model):
    __tablename__ = 'eventos_personalizados'
    id = db.Column(db.Integer, primary_key=True)
    titulo = db.Column(db.String, nullable=False)
    fecha = db.Column(db.Date, nullable=False)
    descripcion = db.Column(db.String)
    usuario_id = db.Column(db.Integer, db.ForeignKey('usuarios.id'))  # Relaciona el evento con el usuario

class Calificacion(db.Model):
    __tablename__ = 'calificaciones'
    id = db.Column(db.Integer, primary_key=True)
    materia_id = db.Column(db.Integer, db.ForeignKey('materias.id'))
    tarea_id = db.Column(db.Integer, db.ForeignKey('tareas.id'))
    usuario_id = db.Column(db.Integer, db.ForeignKey('usuarios.id'))  # Relaciona la calificación con el usuario
    nota = db.Column(db.Float, nullable=False)
