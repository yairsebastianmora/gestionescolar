from database import Session
from flask import Flask, render_template, request, redirect, url_for
from models import Libro, Usuario, Prestamo, Autor
from datetime import datetime, date
from sqlalchemy import func, desc

app = Flask(__name__)
session = Session()  

# Página principal
@app.route('/')
def index():
    query = request.args.get('q', '').strip()  
    if query:
        libros = session.query(Libro).join(Autor).filter(
            Libro.titulo.ilike(f'%{query}%') |  
            Autor.nombre.ilike(f'%{query}%')   
        ).all()
    else:
        libros = session.query(Libro).all()  
    return render_template('index.html', libros=libros, query=query)
@app.route('/autor_top')
def autor_top():
    # Consulta para obtener los autores con el total de libros registrados
    resultados = session.query(Autor.nombre, func.count(Libro.id).label("total"))\
                        .join(Libro).group_by(Autor.id)\
                        .order_by(desc("total")).all()
    return render_template('autor_top.html', resultados=resultados)
# Registrar un nuevo libro
@app.route('/registrar_libro', methods=['GET', 'POST'])
def registrar_libro():
    if request.method == 'POST':
        titulo = request.form['titulo']
        nombre_autor = request.form['autor']

        # Verificar si el autor ya existe
        autor = session.query(Autor).filter_by(nombre=nombre_autor).first()
        if not autor:
            autor = Autor(nombre=nombre_autor)
            session.add(autor)
            session.commit()

        # Registrar el libro con el autor
        nuevo_libro = Libro(titulo=titulo, autor_id=autor.id)
        session.add(nuevo_libro)
        session.commit()

        mensaje = {'texto': 'Libro registrado correctamente.', 'categoria': 'success'}
        return render_template('registrar_libro.html', libros=session.query(Libro).all(), mensaje=mensaje)

    return render_template('registrar_libro.html')

# Prestar un libro
@app.route('/registrar-prestamo', methods=['GET', 'POST'])
def registrar_prestamo():
    libros_disponibles = session.query(Libro).filter_by(disponible=True).all()

    if request.method == 'POST':
        libro_id = request.form['libro_id']
        documento_identidad = request.form['documento_identidad']
        nombre = request.form['nombre']
        correo = request.form['correo']

        # Verificar si el usuario ya existe
        usuario = session.query(Usuario).filter_by(documento_identidad=documento_identidad).first()
        if not usuario:
            usuario = Usuario(documento_identidad=documento_identidad, nombre=nombre, correo=correo)
            session.add(usuario)
            session.commit()

        # Registrar el préstamo
        libro = session.query(Libro).get(libro_id)
        if libro and libro.disponible:
            libro.disponible = False
            nuevo_prestamo = Prestamo(libro_id=libro_id, usuario_id=usuario.id)
            session.add(nuevo_prestamo)
            session.commit()
            mensaje = {'texto': 'Préstamo registrado correctamente.', 'categoria': 'success'}
            return render_template('prestados.html', prestamos=session.query(Prestamo).filter(Prestamo.fecha_devolucion == None).all(), mensaje=mensaje)
        else:
            mensaje = {'texto': 'El libro no está disponible.', 'categoria': 'danger'}
            return render_template('registrar_prestamo.html', libros=libros_disponibles, mensaje=mensaje)

    return render_template('registrar_prestamo.html', libros=libros_disponibles)

# Devolver un préstamo
@app.route('/devolver-prestamo/<int:prestamo_id>', methods=['POST'])
def devolver_prestamo(prestamo_id):
    prestamo = session.query(Prestamo).get(prestamo_id)
    if not prestamo:
        mensaje = {'texto': 'El préstamo no existe.', 'categoria': 'danger'}
    elif prestamo.fecha_devolucion:
        mensaje = {'texto': 'El préstamo ya fue devuelto.', 'categoria': 'warning'}
    else:
        prestamo.libro.disponible = True
        prestamo.fecha_devolucion = datetime.now()
        session.commit()
        mensaje = {'texto': 'Libro devuelto correctamente.', 'categoria': 'success'}
    return redirect(url_for('prestados', mensaje=mensaje))
# Gestionar libros
@app.route('/prestados')
def prestados():
    prestamos = session.query(Prestamo).filter(Prestamo.fecha_devolucion == None).all()
    mensaje = request.args.get('mensaje', None)  # Obtener mensaje si existe, o None por defecto
    return render_template('prestados.html', prestamos=prestamos, mensaje=mensaje)
@app.route('/gestionar_libros')
def gestionar_libros():
    libros = session.query(Libro).all()
    return render_template('gestionar_libros.html', libros=libros)

# Eliminar un libro
@app.route('/eliminar_libro/<int:libro_id>', methods=['POST'])
def eliminar_libro(libro_id):
    libro = session.query(Libro).get(libro_id)
    if libro:
        session.delete(libro)
        session.commit()
        mensaje = {'texto': 'Libro eliminado correctamente.', 'categoria': 'success'}
    else:
        mensaje = {'texto': 'El libro no existe.', 'categoria': 'danger'}
    return render_template('gestionar_libros.html', libros=session.query(Libro).all(), mensaje=mensaje)

# Editar un libro
@app.route('/editar_libro/<int:libro_id>', methods=['GET', 'POST'])
def editar_libro(libro_id):
    libro = session.query(Libro).get(libro_id)
    if request.method == 'POST':
        titulo = request.form['titulo']
        nombre_autor = request.form['autor']

        # Verificar si el autor ya existe
        autor = session.query(Autor).filter_by(nombre=nombre_autor).first()
        if not autor:
            autor = Autor(nombre=nombre_autor)
            session.add(autor)
            session.commit()

        # Actualizar el libro
        libro.titulo = titulo
        libro.autor_id = autor.id
        session.commit()

        mensaje = {'texto': 'Libro editado correctamente.', 'categoria': 'success'}
        return render_template('gestionar_libros.html', libros=session.query(Libro).all(), mensaje=mensaje)

    return render_template('editar_libro.html', libro=libro)

if __name__ == '__main__':
    app.run(debug=True)