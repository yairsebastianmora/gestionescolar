import os
from flask import Flask, render_template, request, redirect, url_for, flash, session, send_from_directory
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime, date
from models import db, Usuario, Materia, Tarea, EventoPersonalizado, Calificacion

app = Flask(__name__)
# Ruta absoluta para la base de datos
basedir = os.path.abspath(os.path.dirname(__file__))
db_path = os.path.join(basedir, 'instance', 'tus_datos.db')

# Asegurar que la carpeta 'instance/' existe antes de crear la base de datos
instance_dir = os.path.join(basedir, 'instance')
os.makedirs(instance_dir, exist_ok=True)

# Comprobar si la base de datos ya existe
db_exists = os.path.exists(db_path)

app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{db_path}'
app.secret_key = 'una_clave_secreta_muy_segura_y_larga_12345'
db.init_app(app)

# Crear tablas si no existen
with app.app_context():
    db.create_all()
    if not db_exists:
        print('⚠️  Base de datos creada desde cero. Si ves errores de tablas, reinicia la app.')

# Página principal
@app.route('/')
def index():
    if 'usuario_id' not in session:
        return redirect(url_for('login'))
    usuario_id = session['usuario_id']
    tareas = db.session.query(Tarea).filter_by(usuario_id=usuario_id).all()
    eventos = []
    hoy = datetime.now().date()
    proximos = []
    for tarea in tareas:
        if tarea.fecha_entrega:
            eventos.append({
                'title': tarea.titulo,
                'start': tarea.fecha_entrega.strftime('%Y-%m-%d'),
                'description': tarea.descripcion or '',
                'materia': tarea.materia.nombre if tarea.materia else 'Sin materia',
                'estado': tarea.estado
            })
            if 0 <= (tarea.fecha_entrega - hoy).days <= 3:
                nombre_materia = tarea.materia.nombre if tarea.materia else 'Sin materia'
                proximos.append({
                    'tipo': 'tarea',
                    'id': tarea.id,
                    'materia_id': tarea.materia_id or 0,
                    'texto': f"Tarea '{tarea.titulo}' de {nombre_materia}",
                    'fecha': tarea.fecha_entrega.strftime('%Y-%m-%d'),
                    'estado': tarea.estado
                })
    eventos_personalizados = EventoPersonalizado.query.filter_by(usuario_id=usuario_id).all()
    for ev in eventos_personalizados:
        eventos.append({
            'title': ev.titulo,
            'start': ev.fecha.strftime('%Y-%m-%d'),
            'description': ev.descripcion or '',
            'materia': 'Evento Personalizado',
            'estado': 'personalizado'
        })
        if 0 <= (ev.fecha - hoy).days <= 3:
            proximos.append({
                'tipo': 'evento',
                'id': ev.id,
                'texto': f"Evento '{ev.titulo}'",
                'fecha': ev.fecha.strftime('%Y-%m-%d'),
                'estado': 'personalizado'
            })
    materias = db.session.query(Materia).filter_by(usuario_id=usuario_id).all()
    query = request.args.get('q', '')
    if query:
        materias = db.session.query(Materia).filter(
            (Materia.nombre.ilike(f'%{query}%')) |
            (Materia.docente.ilike(f'%{query}%')),
            Materia.usuario_id==usuario_id
        ).all()
    hoy_str = hoy.strftime('%Y-%m-%d')
    tareas_vencidas = [t for t in tareas if t.estado == 'Pendiente' and t.fecha_entrega and t.fecha_entrega < hoy]
    return render_template('index.html', eventos=eventos, materias=materias, query=query, mostrar_calendario=True, hoy_str=hoy_str, proximos=proximos, tareas=tareas, tareas_vencidas=tareas_vencidas)

@app.route('/registrar_tarea/<int:materia_id>', methods=['GET', 'POST'])
def registrar_tarea(materia_id):
    if 'usuario_id' not in session:
        flash('Debes iniciar sesión para registrar tareas.')
        return redirect(url_for('login'))
    if request.method == 'POST':
        titulo = request.form['titulo']
        fecha_entrega = request.form['fecha_entrega']
        descripcion = request.form['descripcion']
        usuario_id = session['usuario_id']
        nueva_tarea = Tarea(
            titulo=titulo,
            fecha_entrega=datetime.strptime(fecha_entrega, '%Y-%m-%d').date(),
            estado='Pendiente',
            descripcion=descripcion,
            materia_id=materia_id,
            usuario_id=usuario_id,
            archivo=None
        )
        db.session.add(nueva_tarea)
        db.session.commit()
        flash("Tarea registrada correctamente.")
        return redirect(url_for('gestionar_materias'))
    return render_template('registrar_tarea.html', materia_id=materia_id)

@app.route('/tareas')
def listar_tareas():
    if 'usuario_id' not in session:
        return redirect(url_for('login'))
    usuario_id = session['usuario_id']
    tareas = db.session.query(Tarea).filter_by(usuario_id=usuario_id).all()
    return render_template('tareas.html', tareas=tareas)

@app.route('/tareas/<int:materia_id>')
def tareas_por_materia(materia_id):
    if 'usuario_id' not in session:
        return redirect(url_for('login'))
    usuario_id = session['usuario_id']
    tareas = db.session.query(Tarea).filter_by(materia_id=materia_id, usuario_id=usuario_id).all()
    materia = db.session.query(Materia).get(materia_id)
    return render_template('tareas_por_materia.html', tareas=tareas, materia=materia)

@app.route('/editar_tarea/<int:tarea_id>', methods=['GET', 'POST'])
def editar_tarea(tarea_id):
    if 'usuario_id' not in session:
        flash('Debes iniciar sesión para editar tareas.')
        return redirect(url_for('login'))
    tarea = db.session.query(Tarea).get(tarea_id)

    if request.method == 'POST':
        tarea.titulo = request.form['titulo']
        tarea.descripcion = request.form['descripcion']
        fecha_str = request.form['fecha_entrega']
        tarea.fecha_entrega = datetime.strptime(fecha_str, '%Y-%m-%d').date()
        archivo_subido = False
        if 'archivo' in request.files:
            file = request.files['archivo']
            if file and file.filename:
                uploads_dir = os.path.join(basedir, 'uploads')
                os.makedirs(uploads_dir, exist_ok=True)
                file_path = os.path.join(uploads_dir, file.filename)
                file.save(file_path)
                tarea.archivo = file.filename
                archivo_subido = True
        # Si se subió archivo, marcar como 'Entregada', si no, mantener el estado
        if archivo_subido:
            tarea.estado = 'Entregada'
        else:
            tarea.estado = request.form['estado']
        try:
            db.session.commit()
            flash('Tarea actualizada correctamente.')
            return redirect(url_for('listar_tareas'))
        except Exception as e:
            db.session.rollback()
            print(e)
            flash('Error al actualizar la tarea.')
    return render_template('editar_tarea.html', tarea=tarea)

# Eliminar una tarea


@app.route('/eliminar_tarea/<int:tarea_id>', methods=['POST'])
def eliminar_tarea(tarea_id):
    if 'usuario_id' not in session:
        flash('Debes iniciar sesión para eliminar tareas.')
        return redirect(url_for('login'))
    tarea = db.session.query(Tarea).get(tarea_id)
    if tarea:
        materia_id = tarea.materia_id
        db.session.delete(tarea)
        db.session.commit()
        flash('Tarea eliminada correctamente.', 'success')
    else:
        flash('La tarea no existe.', 'danger')
    return redirect(url_for('tareas_por_materia', materia_id=materia_id))

# Rutas de usuario y login
@app.route('/registrar_usuario', methods=['GET', 'POST'])
def registrar_usuario():
    if request.method == 'POST':
        correo = request.form.get('correo')
        password = request.form.get('password')
        confirmar_password = request.form.get('confirmar_password')
        if not correo or not password or not confirmar_password:
            flash('Todos los campos son obligatorios.')
            return render_template('registrar_usuario.html')
        if password != confirmar_password:
            flash('Las contraseñas no coinciden.')
            return render_template('registrar_usuario.html')
        existe = db.session.query(Usuario).filter_by(correo=correo).first()
        if existe:
            flash('El correo ya está registrado.')
            return render_template('registrar_usuario.html')
        hashed_password = generate_password_hash(password)
        nuevo_usuario = Usuario(nombre=correo, documento_identidad=correo, correo=correo, password=hashed_password)
        db.session.add(nuevo_usuario)
        db.session.commit()
        flash('Usuario registrado correctamente. Inicia sesión.')
        return redirect(url_for('login'))
    return render_template('registrar_usuario.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        correo = request.form['correo']
        password = request.form['password']
        usuario = db.session.query(Usuario).filter_by(correo=correo).first()
        if usuario and check_password_hash(usuario.password, password):
            session['usuario_id'] = usuario.id
            session['usuario_nombre'] = usuario.nombre
            flash('Bienvenido, ' + usuario.nombre)
            return redirect(url_for('index'))
        else:
            flash('Credenciales incorrectas.')
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.pop('usuario_id', None)
    session.pop('usuario_nombre', None)
    flash('Sesión cerrada correctamente.')
    return redirect(url_for('login'))

@app.route('/buscar_tareas', methods=['GET'])
def buscar_tareas():
    if 'usuario_id' not in session:
        return redirect(url_for('login'))
    estado = request.args.get('estado', '').strip()
    materia_id = request.args.get('materia_id', '').strip()
    fecha = request.args.get('fecha', '').strip()
    query = db.session.query(Tarea)
    if estado:
        query = query.filter(Tarea.estado.ilike(f'%{estado}%'))
    if materia_id:
        query = query.filter(Tarea.materia_id == materia_id)
    if fecha:
        try:
            fecha_dt = datetime.strptime(fecha, '%Y-%m-%d').date()
            query = query.filter(Tarea.fecha_entrega == fecha_dt)
        except Exception:
            flash('Formato de fecha inválido. Usa AAAA-MM-DD.')
    tareas = query.all()
    return render_template('tareas.html', tareas=tareas)

@app.route('/registrar_materia', methods=['GET', 'POST'])
def registrar_materia():
    if 'usuario_id' not in session:
        flash('Debes iniciar sesión para registrar materias.')
        return redirect(url_for('login'))
    if request.method == 'POST':
        nombre = request.form['nombre']
        docente = request.form.get('docente')
        horario = request.form.get('horario')
        aula = request.form.get('aula')
        usuario_id = session['usuario_id']
        nueva_materia = Materia(nombre=nombre, docente=docente, horario=horario, aula=aula, usuario_id=usuario_id)
        db.session.add(nueva_materia)
        db.session.commit()
        flash('Materia registrada correctamente.')
        return redirect(url_for('gestionar_materias'))
    return render_template('registrar_materia.html')

@app.route('/gestionar_materias')
def gestionar_materias():
    if 'usuario_id' not in session:
        flash('Debes iniciar sesión para gestionar materias.')
        return redirect(url_for('login'))
    usuario_id = session['usuario_id']
    materias = db.session.query(Materia).filter_by(usuario_id=usuario_id).all()
    return render_template('gestionar_materias.html', materias=materias)

@app.route('/eliminar_materia/<int:materia_id>', methods=['POST'])
def eliminar_materia(materia_id):
    if 'usuario_id' not in session:
        flash('Debes iniciar sesión para eliminar materias.')
        return redirect(url_for('login'))
    materia = db.session.query(Materia).get(materia_id)
    if materia:
        db.session.delete(materia)
        db.session.commit()
        flash('Materia eliminada correctamente.', 'success')
    else:
        flash('La materia no existe.', 'danger')
    return redirect(url_for('gestionar_materias'))

@app.route('/editar_materia/<int:materia_id>', methods=['GET', 'POST'])
def editar_materia(materia_id):
    if 'usuario_id' not in session:
        flash('Debes iniciar sesión para editar materias.')
        return redirect(url_for('login'))
    materia = db.session.query(Materia).get(materia_id)
    if request.method == 'POST':
        materia.nombre = request.form['nombre']
        materia.docente = request.form.get('docente')
        materia.horario = request.form.get('horario')
        materia.aula = request.form.get('aula')
        db.session.commit()
        flash('Materia editada correctamente.')
        return redirect(url_for('gestionar_materias'))
    return render_template('registrar_materia.html', materia=materia, editar=True)

@app.route('/agregar_evento', methods=['GET', 'POST'])
def agregar_evento():
    if 'usuario_id' not in session:
        return redirect(url_for('login'))
    if request.method == 'POST':
        titulo = request.form['titulo']
        fecha = request.form['fecha']
        descripcion = request.form.get('descripcion')
        evento = EventoPersonalizado(
            titulo=titulo,
            fecha=datetime.strptime(fecha, '%Y-%m-%d').date(),
            descripcion=descripcion,
            usuario_id=session['usuario_id']
        )
        db.session.add(evento)
        db.session.commit()
        flash('Evento agregado al calendario.')
        return redirect(url_for('calendario'))
    return render_template('agregar_evento.html')

@app.route('/calendario')
def calendario():
    if 'usuario_id' not in session:
        return redirect(url_for('login'))
    usuario_id = session['usuario_id']
    eventos_personalizados = EventoPersonalizado.query.filter_by(usuario_id=usuario_id).all()
    # Limpiar mensajes flash previos excepto los de eventos próximos
    flashes = list(session.get('_flashes', []))
    session['_flashes'] = [f for f in flashes if 'Próximos eventos/tareas:' in f[1]]
    tareas = db.session.query(Tarea).all()
    eventos = []
    hoy = datetime.now().date()
    proximos = []
    for tarea in tareas:
        if tarea.fecha_entrega:
            eventos.append({
                'title': tarea.titulo,
                'start': tarea.fecha_entrega.strftime('%Y-%m-%d'),
                'description': tarea.descripcion or '',
                'materia': tarea.materia.nombre if tarea.materia else 'Sin materia',
                'estado': tarea.estado
            })
            if 0 <= (tarea.fecha_entrega - hoy).days <= 3:
                proximos.append(f"Tarea '{tarea.titulo}' de {tarea.materia.nombre if tarea.materia else ''} vence el {tarea.fecha_entrega}")
    for ev in eventos_personalizados:
        eventos.append({
            'title': ev.titulo,
            'start': ev.fecha.strftime('%Y-%m-%d'),
            'description': ev.descripcion or '',
            'materia': 'Evento Personalizado',
            'estado': 'personalizado'
        })
        if 0 <= (ev.fecha - hoy).days <= 3:
            proximos.append(f"Evento '{ev.titulo}' el {ev.fecha}")
    if proximos:
        flash('Próximos eventos/tareas: ' + ' | '.join(proximos), 'info')
    return render_template('calendario.html', eventos=eventos)

@app.route('/calificaciones', methods=['GET', 'POST'])
def calificaciones():
    if 'usuario_id' not in session:
        return redirect(url_for('login'))
    usuario_id = session['usuario_id']
    materias = db.session.query(Materia).filter_by(usuario_id=usuario_id).all()
    tareas = db.session.query(Tarea).filter_by(usuario_id=usuario_id).all()
    hoy = datetime.now().date()
    tareas_vencidas = db.session.query(Tarea).filter(Tarea.estado=='Pendiente', Tarea.fecha_entrega < hoy, Tarea.usuario_id==usuario_id).all()
    mensaje = None
    if request.method == 'POST':
        materia_id = int(request.form['materia_id'])
        tarea_id = request.form.get('tarea_id')
        nota = float(request.form['nota'])
        if not tarea_id:
            mensaje = 'Debes seleccionar una tarea.'
        else:
            tarea_id = int(tarea_id)
            calif = db.session.query(Calificacion).filter_by(materia_id=materia_id, tarea_id=tarea_id, usuario_id=usuario_id).first()
            if calif:
                calif.nota = nota
                mensaje = 'Calificación actualizada.'
            else:
                calif = Calificacion(materia_id=materia_id, tarea_id=tarea_id, usuario_id=usuario_id, nota=nota)
                db.session.add(calif)
                mensaje = 'Calificación registrada.'
            db.session.commit()
    calificaciones = db.session.query(Calificacion).filter_by(usuario_id=usuario_id).all()
    promedios = {}
    suma = 0
    conteo = 0
    for c in calificaciones:
        materia = db.session.query(Materia).get(c.materia_id)
        if materia:
            if materia.nombre not in promedios:
                promedios[materia.nombre] = []
            promedios[materia.nombre].append(c.nota)
            suma += c.nota
            conteo += 1
    for tarea in tareas_vencidas:
        materia = db.session.query(Materia).get(tarea.materia_id)
        if materia:
            if materia.nombre not in promedios:
                promedios[materia.nombre] = []
            promedios[materia.nombre].append(0)
            suma += 0
            conteo += 1
    promedios_materia = {k: round(sum(v)/len(v),2) for k,v in promedios.items()}
    promedio_general = round(suma / conteo, 2) if conteo else None
    return render_template('calificaciones.html', materias=materias, tareas=tareas, calificaciones=calificaciones, promedios=promedios_materia, promedio_general=promedio_general, mensaje=mensaje, tareas_vencidas=tareas_vencidas)

@app.route('/uploads/<filename>')
def uploaded_file(filename):
    uploads_dir = os.path.join(basedir, 'uploads')
    return send_from_directory(uploads_dir, filename)

@app.route('/ver_tarea/<int:tarea_id>', methods=['GET', 'POST'])
def ver_tarea(tarea_id):
    if 'usuario_id' not in session:
        flash('Debes iniciar sesión para ver tareas.')
        return redirect(url_for('login'))
    tarea = db.session.query(Tarea).get(tarea_id)
    if not tarea:
        flash('La tarea no existe.')
        return redirect(url_for('listar_tareas'))
    hoy = datetime.now().date()
    # Lógica de entrega de archivo (antes en entregar_tarea)
    if request.method == 'POST' and tarea.estado == 'Pendiente' and not tarea.archivo:
        if tarea.fecha_entrega and tarea.fecha_entrega < hoy:
            flash('La fecha de entrega ha vencido. Ya no puedes entregar esta tarea.')
            return redirect(url_for('ver_tarea', tarea_id=tarea_id))
        if 'archivo' in request.files:
            file = request.files['archivo']
            if file and file.filename:
                uploads_dir = os.path.join(basedir, 'uploads')
                os.makedirs(uploads_dir, exist_ok=True)
                file_path = os.path.join(uploads_dir, file.filename)
                file.save(file_path)
                tarea.archivo = file.filename
                tarea.estado = 'Entregada'
                db.session.commit()
                flash('Archivo entregado correctamente.')
                return redirect(url_for('ver_tarea', tarea_id=tarea_id))
            else:
                flash('Debes seleccionar un archivo para entregar.')
    return render_template('ver_tarea.html', tarea=tarea, hoy=hoy)

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))