from . import db


class Etudiant(db.Model):
    __tablename__ = 'etudiant'
    nce = db.Column(db.String(20), primary_key=True)
    nom = db.Column(db.String(100), nullable=False)
    prenom = db.Column(db.String(100), nullable=False)
    date_nais = db.Column(db.Date)
    lieu_nais = db.Column(db.String(100))

    is_active = db.Column(db.Boolean(), default=False)
    created_at = db.Column(db.TIMESTAMP,
                           server_default=db.func.current_timestamp(), nullable=True)
    updated_at = db.Column(db.TIMESTAMP, server_onupdate=db.func.now(),
                           nullable=True)

    # Nom du fichier image (stocké dans static/image)
    photo = db.Column(db.String(255))

    # Clé étrangère vers Classe
    cod_class = db.Column(db.String(20),
                          db.ForeignKey('classe.cod_class',
                                        onupdate="CASCADE", ondelete='CASCADE'),
                          nullable=False)
    classe_r = db.relationship("Classe", back_populates="etudiants")

    # Relation vers les absences
    absences = db.relationship("Absence", back_populates="etudiant_r")

    # ---- méthodes utiles ----
    @property
    def photo_path(self):
        """Chemin relatif au dossier static, ou None s'il n'y a pas de photo."""
        return f"image/{self.photo}" if self.photo else None

    def to_dict(self):
        return {
            "nce": self.nce,
            "nom": self.nom,
            "prenom": self.prenom,
            "date_nais": self.date_nais.isoformat() if self.date_nais else None,
            "lieu_nais": self.lieu_nais,
            "cod_class": self.cod_class,
            "photo": self.photo,
        }

    def __repr__(self):
        return f"<Etudiant {self.nce} {self.nom} {self.prenom}>"
