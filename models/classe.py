from . import db


class Classe(db.Model):
    __tablename__ = 'classe'
    cod_class = db.Column(db.String(20), primary_key=True)
    libelle = db.Column(db.String(100), nullable=False)

    etudiants = db.relationship("Etudiant", back_populates="classe_r")

    def __repr__(self):
        return f"<Classe {self.cod_class}>"
