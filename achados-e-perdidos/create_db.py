# Script para criar o banco de dados
try:
    from manager import app, db
    from manager import models
except Exception:
    from manager import app, db
    import models as models


def create_db():
    with app.app_context():
        db.create_all()


if __name__ == "__main__":
    create_db()
