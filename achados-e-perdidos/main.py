# Iniciar a Aplicação Flask
from manager import app
import os

if __name__ == "__main__":
    debug = os.getenv("FLASK_DEBUG", "1") == "1"
    host = os.getenv("FLASK_RUN_HOST", "127.0.0.1")
    port = int(os.getenv("FLASK_RUN_PORT", 5000))
    app.run(host=host, port=port, debug=debug)
