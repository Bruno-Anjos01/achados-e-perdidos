# Definir os Modelos do Banco de Dados
from manager import db, login_manager
from datetime import datetime
from flask_login import UserMixin


@login_manager.user_loader
def load_usuario(id_usuario):
    try:
        return Usuario.query.get(int(id_usuario))
    except Exception:
        return None


class Usuario(db.Model, UserMixin):
    __tablename__ = "usuario"

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), nullable=False, unique=True, index=True)
    email = db.Column(db.String(120), nullable=False, unique=True, index=True)
    senha = db.Column(db.String(128), nullable=False)
    tipo = db.Column(db.String(20), nullable=False, default="aluno")

    fotos = db.relationship(
        "Foto", backref="usuario", lazy=True, cascade="all, delete-orphan"
    )

    def __repr__(self):
        return f"<Usuario id={self.id} username={self.username}>"


class Foto(db.Model):
    __tablename__ = "foto"

    id = db.Column(db.Integer, primary_key=True)
    titulo = db.Column(db.String(120), nullable=False)
    descricao = db.Column(db.Text, nullable=True)
    local = db.Column(db.String(120), nullable=True)
    data_item = db.Column(db.String(40), nullable=True)

    caminho_imagem = db.Column(db.String(255), nullable=False)
    data_postagem = db.Column(db.DateTime, default=datetime.utcnow)

    usuario_id = db.Column(db.Integer, db.ForeignKey("usuario.id"), nullable=False)

    def __repr__(self):
        return f"<Foto id={self.id} titulo={self.titulo}>"
