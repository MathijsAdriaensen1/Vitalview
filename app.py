from flask import Flask
from app.utils.routes import routes
from app.utils.auth_routes import auth_bp

app = Flask(__name__, template_folder="app/templates")

# Blueprints registreren
app.register_blueprint(routes)
app.register_blueprint(auth_bp)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
