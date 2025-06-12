from flask import Blueprint, render_template
import os

# Zorg dat de template_folder juist is (relatief t.o.v. dit bestand)
routes = Blueprint("routes", __name__, template_folder="../templates")

@routes.route("/")
def home():
    return render_template("home.html")

@routes.route("/dashboard")
def dashboard():
    return render_template("dashboard.html")