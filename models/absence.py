from . import db


class Absence(db.Model):
    __tablename__ = 'absence'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    date_abs = db.Column(db.Date, nullable=False)
    motif = db.Column(db.String(200))

    # nullable=False : empêche de supprimer un étudiant ayant des absences (IntegrityError)
    nce = db.Column(db.String(20), db.ForeignKey('etudiant.nce'), nullable=False)
    etudiant_r = db.relationship("Etudiant", back_populates="absences")

    def __repr__(self):
        return f"<Absence {self.id} {self.nce}>"
