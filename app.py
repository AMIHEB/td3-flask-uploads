import os
from datetime import date, datetime

from flask import Flask, render_template, request, redirect, flash
from flask_uploads import UploadSet, configure_uploads, IMAGES, UploadNotAllowed
from sqlalchemy import event
from sqlalchemy.engine import Engine
from sqlalchemy.exc import IntegrityError

from models import db, Etudiant, Classe, Absence

BASE_DIR = os.path.abspath(os.path.dirname(__file__))

app = Flask(__name__)
app.config["SECRET_KEY"] = "td3-flask-uploads"
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///" + os.path.join(BASE_DIR, "school.db")
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["UPLOADED_PHOTOS_DEST"] = os.path.join(BASE_DIR, "static", "image")
app.config["MAX_CONTENT_LENGTH"] = 5 * 1024 * 1024  # 5 Mo max

os.makedirs(app.config["UPLOADED_PHOTOS_DEST"], exist_ok=True)

db.init_app(app)

# "photos" = nom de l'ensemble d'uploads, IMAGES = types d'images autorisés
photos = UploadSet("photos", IMAGES)
configure_uploads(app, photos)


# SQLite : activer les clés étrangères (pour obtenir l'IntegrityError)
@event.listens_for(Engine, "connect")
def _set_sqlite_pragma(dbapi_connection, connection_record):
    if dbapi_connection.__class__.__module__.startswith("sqlite3"):
        cur = dbapi_connection.cursor()
        cur.execute("PRAGMA foreign_keys=ON")
        cur.close()


def allowed_image(filename):
    allowed_extensions = {'png', 'jpg', 'jpeg', 'gif'}
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in allowed_extensions


def parse_date(value):
    try:
        return datetime.strptime(value, "%Y-%m-%d").date() if value else None
    except ValueError:
        return None


# ------------------------------------------------------------------ routes
@app.route("/")
def index():
    return redirect("/students")


@app.route("/students")
def students():
    liste = Etudiant.query.order_by(Etudiant.nom, Etudiant.prenom).all()
    return render_template("students.html", etudiants=liste)


@app.route("/addStudent/", methods=["GET", "POST"])
def addStudent():
    classes = Classe.query.order_by(Classe.cod_class).all()
    if request.method == "POST":
        try:
            form = request.form
            nce = form["nce"].strip()
            nom = form["nom"].strip()
            prenom = form["prenom"].strip()
            date_nais = parse_date(form.get("date_nais"))
            lieu_nais = form.get("lieu_nais", "").strip()
            cod_class = form["cod_class"]

            photo = request.files.get("photo")
            photo_name = ""
            # Un fichier a-t-il été envoyé et est-il autorisé ?
            if photo and photo.filename:
                if allowed_image(photo.filename):
                    photo_name = photos.save(photo)   # enregistrement via Flask-Uploads
                else:
                    flash('File type not allowed.', 'danger')

            if not nce or not nom or not prenom:
                flash('Field(s) cannot be empty.', 'danger')
            elif db.session.get(Etudiant, nce):
                flash(f'Student {nce} already exists.', 'danger')
            else:
                etu = Etudiant(nce=nce, nom=nom, prenom=prenom, date_nais=date_nais,
                               lieu_nais=lieu_nais, cod_class=cod_class,
                               photo=photo_name, is_active=True)
                db.session.add(etu)
                db.session.commit()
                flash('Student added successfully', 'success')
                return redirect("/students")
        except Exception as e:
            db.session.rollback()
            flash(f'Failed operation: {str(e)}', 'danger')
    return render_template("addStudent.html", classes=classes)


@app.route("/editStudent/<string:student_nce>", methods=["GET", "POST"])
def editStudent(student_nce):
    etu = db.session.get(Etudiant, student_nce)
    if not etu:
        flash('Student not found', 'danger')
        return redirect("/students")

    if request.method == "POST":
        try:
            etu.nom = request.form["nom"].strip()
            etu.prenom = request.form["prenom"].strip()
            etu.date_nais = parse_date(request.form.get("date_nais"))
            etu.lieu_nais = request.form.get("lieu_nais", "").strip()
            etu.cod_class = request.form["cod_class"]

            photo = request.files.get("photo")
            if photo and photo.filename:
                try:
                    if not allowed_image(photo.filename):
                        flash('File type not allowed.', 'danger')
                        return redirect(request.url)
                    etu.photo = photos.save(photo)   # nouvelle photo
                except UploadNotAllowed:
                    flash('Upload not allowed.', 'danger')
                    return redirect(request.url)
            # sinon : on conserve l'ancienne photo

            db.session.commit()
            flash('Student information updated successfully', 'success')
        except Exception as e:
            db.session.rollback()
            flash(f'Failed operation: {str(e)}', 'danger')
        return redirect("/students")

    classes = Classe.query.order_by(Classe.cod_class).all()
    return render_template("editStudent.html", etudiant=etu, classes=classes)


@app.route("/deleteStudent/<string:student_id>")
def delete_student(student_id):
    try:
        etu = db.session.get(Etudiant, student_id)
        if etu:
            db.session.delete(etu)
            db.session.commit()
            flash('Student deleted successfully', 'success')
        else:
            flash('Student not found', 'danger')
    except IntegrityError:
        db.session.rollback()
        flash('Cannot delete the student. It is linked to other records.', 'danger')
    return redirect('/students')


# ------------------------------------------------------------ initialisation
def init_db():
    db.create_all()
    if Classe.query.count() == 0:
        db.session.add_all([
            Classe(cod_class="INGTA1-S1", libelle="Ingénierie 1ère année - S1"),
            Classe(cod_class="INGTA2-S1", libelle="Ingénierie 2ème année - S1"),
            Classe(cod_class="INGTA3-S1", libelle="Ingénierie 3ème année - S1"),
        ])
        # Étudiant de démo avec une absence : sa suppression déclenche l'IntegrityError
        demo = Etudiant(nce="12345678", nom="Ben Salah", prenom="Ahmed",
                        date_nais=date(2003, 5, 14), lieu_nais="Tunis",
                        cod_class="INGTA2-S1", is_active=True)
        db.session.add(demo)
        db.session.flush()
        db.session.add(Absence(date_abs=date(2026, 10, 12), motif="Maladie", nce="12345678"))
        db.session.commit()


with app.app_context():
    init_db()

if __name__ == "__main__":
    app.run(debug=True)
