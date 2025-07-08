from flask import Flask, render_template, redirect, url_for, request, session
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.secret_key = 'secretkey'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///reservasi.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# ====================
# Model
# ====================
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), nullable=False, unique=True)
    password = db.Column(db.String(200), nullable=False)

class Dokter(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nama = db.Column(db.String(100), nullable=False)
    spesialis = db.Column(db.String(100), nullable=False)
    jadwal = db.Column(db.String(100), nullable=False)
    foto = db.Column(db.String(200), nullable=False)

class Reservasi(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    dokter_id = db.Column(db.Integer, db.ForeignKey('dokter.id'))
    tanggal = db.Column(db.String(50), nullable=False)
    waktu = db.Column(db.String(50), nullable=False)

# ====================
# Routes
# ====================
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/dokter')
def dokter():
    data_dokter = Dokter.query.all()
    return render_template('dokter.html', dokter=data_dokter)

@app.route('/reservasi', methods=['GET', 'POST'])
def reservasi():
    if 'user_id' not in session:
        return redirect(url_for('login'))

    if request.method == 'POST':
        dokter_id = request.form['dokter_id']
        tanggal = request.form['tanggal']
        waktu = request.form['waktu']
        new_reservasi = Reservasi(
            user_id=session['user_id'],
            dokter_id=dokter_id,
            tanggal=tanggal,
            waktu=waktu
        )
        db.session.add(new_reservasi)
        db.session.commit()
        return redirect(url_for('riwayat'))

    dokter = Dokter.query.all()
    return render_template('reservasi.html', dokter=dokter)

@app.route('/riwayat')
def riwayat():
    if 'user_id' not in session:
        return redirect(url_for('login'))

    data_reservasi = Reservasi.query.filter_by(user_id=session['user_id']).all()
    return render_template('riwayat.html', reservasi=data_reservasi)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()

        if user and check_password_hash(user.password, password):
            session['user_id'] = user.id
            return redirect(url_for('index'))

    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = generate_password_hash(request.form['password'])
        new_user = User(username=username, password=password)
        db.session.add(new_user)
        db.session.commit()
        return redirect(url_for('login'))

    return render_template('register.html')

@app.route('/logout')
def logout():
    session.pop('user_id', None)
    return redirect(url_for('login'))

@app.route('/kontak')
def kontak():
    return render_template('kontak.html')

# ====================
# Jalankan
# ====================
if __name__ == '__main__':
    with app.app_context():
        db.create_all()

        # Tambahkan dokter jika belum ada
        if not Dokter.query.first():
            dokter1 = Dokter(nama="Dr. Asep", spesialis="Spesialis Umum", jadwal="Senin & Rabu", foto="asep.jpg")
            dokter2 = Dokter(nama="Dr. Diaz", spesialis="Spesialis Anak", jadwal="Selasa & Kamis", foto="diaz.jpg")
            dokter3 = Dokter(nama="Dr. Sigit", spesialis="Spesialis Gigi", jadwal="Jumat & Sabtu", foto="hasan.jpg")
            db.session.add_all([dokter1, dokter2, dokter3])
            db.session.commit()
            print("✅ Data dokter berhasil dimasukkan")

    app.run(debug=True)
