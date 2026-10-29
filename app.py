import os
from flask import Flask, render_template, request, redirect, url_for, session
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.secret_key = 'clave_secreta_eco_reto'

# Configuración de base de datos: Si está en Render lee Neon, si está local usa SQLite
database_url = os.environ.get("DATABASE_URL")
if database_url and database_url.startswith("postgres://"):
    database_url = database_url.replace("postgres://", "postgresql://", 1)

app.config['SQLALCHEMY_DATABASE_URI'] = database_url or 'sqlite:///eco_reto.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# Modelo de Base de Datos compatible
class AccionEco(db.Model):
    __tablename__ = 'accion_eco'
    id = db.Column(db.Integer, primary_key=True)
    fecha = db.Column(db.String(20), nullable=False)
    tipo = db.Column(db.String(50), nullable=False)
    descripcion = db.Column(db.String(200), nullable=False)
    impacto = db.Column(db.Float, nullable=False)
    unidad = db.Column(db.String(20), nullable=False)

with app.app_context():
    db.create_all()

@app.route('/')
def login():
    return render_template('login.html')

@app.route('/dashboard')
def dashboard():
    if 'usuario' not in session:
        return redirect(url_for('login'))
    
    acciones = AccionEco.query.all()
    
    total_acciones = len(acciones)
    agua = sum(a.impacto for a in acciones if a.tipo == 'Ahorro de agua')
    reciclaje = sum(a.impacto for a in acciones if a.tipo == 'Reciclaje')
    co2 = sum(a.impacto for a in acciones if a.tipo in ['Transporte', 'Energía'])
    
    return render_template('dashboard.html', acciones=acciones, total=total_acciones, agua=agua, reciclaje=reciclaje, co2=co2)

@app.route('/login', methods=['POST'])
def hacer_login():
    session['usuario'] = request.form.get('usuario', 'Estudiante')
    return redirect(url_for('dashboard'))

@app.route('/logout')
def logout():
    session.pop('usuario', None)
    return redirect(url_for('login'))

@app.route('/nueva', methods=['GET', 'POST'])
def nueva_accion():
    if request.method == 'POST':
        nueva = AccionEco(
            fecha=request.form['fecha'],
            tipo=request.form['tipo'],
            descripcion=request.form['descripcion'],
            impacto=float(request.form['impacto']),
            unidad=request.form['unidad']
        )
        db.session.add(nueva)
        db.session.commit()
        return redirect(url_for('dashboard'))
    return render_template('nueva.html')

@app.route('/eliminar/<int:id>')
def eliminar(id):
    accion = AccionEco.query.get_or_404(id)
    db.session.delete(accion)
    db.session.commit()
    return redirect(url_for('dashboard'))

if __name__ == '__main__':
    app.run(debug=True)