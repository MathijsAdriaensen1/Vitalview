"""
Hoofdtoepassing van VitalView.
- Initialiseert Flask-app
- Verbindt met PostgreSQL via SQLAlchemy
- Registreert Blueprints (routes)
- Laadt Auth0-config uit .env
"""

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from dotenv import load_dotenv
import os

load_dotenv()

app = Flask(__name__)
app.config["SECRET_KEY"] = os.getenv("SECRET_KEY")
app.config["SQLALCHEMY_DATABASE_URI"] = "postgresql://postgres:postgres@localhost/vitalview"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db = SQLAlchemy(app)
migrate = Migrate(app, db)

# Blueprint importeren en registreren
from app.routes.auth_routes import auth_bp
app.register_blueprint(auth_bp)

# Start de app
if __name__ == "__main__":
    app.run(debug=True)
