from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

from .classe import Classe      # noqa: E402,F401
from .etudiant import Etudiant  # noqa: E402,F401
from .absence import Absence    # noqa: E402,F401
