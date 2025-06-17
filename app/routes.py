import os
import re
import json
import requests
from flask import Blueprint, render_template, redirect, url_for, request, session, flash, send_file
from werkzeug.security import generate_password_hash, check_password_hash
from app import db
from app.database.models import User, ContactBericht, HealthData
from dotenv import load_dotenv
from datetime import datetime, timedelta
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import io
import base64
import csv
from werkzeug.utils import secure_filename


load_dotenv()

bp = Blueprint("routes", __name__)

# ===================== PUBLIEKE PAGINA'S =====================

@bp.route("/")
def home():
    return render_template("index.html")

@bp.route("/about")
def about():
    return render_template("about.html")

@bp.route("/how")
def how():
    return render_template("how.html")

@bp.route("/target")
def target():
    return render_template("target.html")

@bp.route("/contact", methods=["GET", "POST"])
def contact():
    if request.method == "POST":
        naam = request.form.get("naam", "").strip()
        emailadres = request.form.get("emailadres", "").strip()
        onderwerp = request.form.get("onderwerp", "").strip()
        telefoonnummer = request.form.get("telefoonnummer", "").strip()
        bericht = request.form.get("bericht", "").strip()

        if not all([naam, emailadres, onderwerp, bericht]):
            flash("Alle verplichte velden moeten ingevuld zijn.")
            return render_template("contact.html")

        nieuw_bericht = ContactBericht(
            naam=naam,
            emailadres=emailadres,
            onderwerp=onderwerp,
            telefoonnummer=telefoonnummer or None,
            bericht=bericht
        )
        try:
            db.session.add(nieuw_bericht)
            db.session.commit()
            return redirect(url_for("routes.contact_bevestiging"))
        except Exception as e:
            db.session.rollback()
            flash("Er is iets fout gegaan bij het verzenden van je bericht.")
            print(f"Contact fout: {e}")
            return render_template("contact.html")

    return render_template("contact.html")

@bp.route("/contact/bevestiging")
def contact_bevestiging():
    return render_template("contact_bevestiging.html")


# ===================== LOGIN/REGISTER FORM (GET) =====================

@bp.route("/login", methods=["GET"])
def login():
    # Gewone loginpagina (social + e-mail login)
    return render_template("login.html")


# ===================== LOGIN VIA E-MAIL EN WACHTWOORD =====================

@bp.route("/login_email", methods=["POST"])
def login_email():
    email = request.form.get("email")
    password = request.form.get("password")

    # Regex validatie
    EMAIL_REGEX = r"^[\w\.-]+@[\w\.-]+\.\w{2,}$"
    PASSWORD_REGEX = r"^(?=.*[A-Z])(?=.*\d)(?=.*[!@#$%^&*]).{8,}$"

    if not re.match(EMAIL_REGEX, email):
        flash("Ongeldig e-mailadres.")
        return redirect(url_for("routes.login"))

    if not re.match(PASSWORD_REGEX, password):
        flash("Wachtwoord moet minstens 8 tekens bevatten, met hoofdletter, cijfer en speciaal teken.")
        return redirect(url_for("routes.login"))

    user = User.query.filter_by(email=email).first()

    if user and check_password_hash(user.hashed_password, password):
        session["user_id"] = user.id
        session["user_email"] = user.email
        flash("Inloggen gelukt!")
        return redirect(url_for("routes.dashboard"))
    else:
        flash("Gebruiker niet gevonden. Je wordt doorgestuurd naar registratie.")
        return redirect(url_for("routes.login"))


# ===================== REGISTRATIE =====================

# === REGISTRATIEPAGINA GET + POST ===
@bp.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "GET":
        return render_template("register.html")

    email = request.form.get("email")
    password = request.form.get("password")

    EMAIL_REGEX = r"^[\w\.-]+@[\w\.-]+\.\w{2,}$"
    PASSWORD_REGEX = r"^(?=.*[A-Z])(?=.*\d)(?=.*[!@#$%^&*]).{8,}$"

    if not re.match(EMAIL_REGEX, email):
        flash("Ongeldig e-mailadres.")
        return redirect(url_for("routes.register"))

    if not re.match(PASSWORD_REGEX, password):
        flash("Wachtwoord moet minstens 8 tekens bevatten, met hoofdletter, cijfer en speciaal teken.")
        return redirect(url_for("routes.register"))

    existing_user = User.query.filter_by(email=email).first()
    if existing_user:
        flash("E-mailadres bestaat al.")
        return redirect(url_for("routes.register"))

    hashed_pw = generate_password_hash(password)
    new_user = User(email=email, hashed_password=hashed_pw)
    db.session.add(new_user)
    db.session.commit()

    # Automatisch inloggen
    session["user_id"] = new_user.id
    session["user_email"] = new_user.email
    flash("Welkom! Je bent nu ingelogd.")

    # (Stap 6) Registratie-e-mail wordt later hier ingevoegd
    # send_registration_email(new_user.email)

    return redirect(url_for("routes.dashboard"))

# ===================== CALLBACK VAN AUTH0 =====================

@bp.route("/callback")
def callback():
    code = request.args.get("code")
    domain = os.getenv("AUTH0_DOMAIN")
    client_id = os.getenv("AUTH0_CLIENT_ID")
    client_secret = os.getenv("AUTH0_CLIENT_SECRET")
    redirect_uri = url_for("routes.callback", _external=True)

    # Haal tokens op
    token_url = f"https://{domain}/oauth/token"
    token_payload = {
        "grant_type": "authorization_code",
        "client_id": client_id,
        "client_secret": client_secret,
        "code": code,
        "redirect_uri": redirect_uri
    }

    token_response = requests.post(token_url, json=token_payload)
    tokens = token_response.json()

    # Haal gebruikersinfo op
    userinfo_url = f"https://{domain}/userinfo"
    headers = {"Authorization": f"Bearer {tokens['access_token']}`"}
    userinfo_response = requests.get(userinfo_url, headers=headers)
    userinfo = userinfo_response.json()

    email = userinfo["email"]
    user = User.query.filter_by(email=email).first()

    # Voeg toe aan DB indien nieuw
    if not user:
        user = User(email=email)
        db.session.add(user)
        db.session.commit()

    # Start sessie
    session["user_id"] = user.id
    session["user_email"] = user.email

    return redirect(url_for("routes.dashboard"))


# ===================== UITLOGGEN =====================

@bp.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("routes.home"))


# ===================== DASHBOARD =====================

@bp.route("/dashboard", methods=["GET", "POST"])
def dashboard():
    if "user_id" not in session:
        flash("Log eerst in.")
        return redirect(url_for("routes.login"))

    user = User.query.get(session["user_id"])
    data = HealthData.query.filter_by(user_id=user.id).all()
    laatste_data = HealthData.query.filter_by(user_id=user.id).order_by(HealthData.date.desc()).first()

    # POST: gebruiker wijzigt info of gezondheidsdata
    if request.method == "POST":
        if "update_user" in request.form:
            user.voornaam = request.form["voornaam"]
            user.achternaam = request.form["achternaam"]
            user.email = request.form["email"]
            user.telefoonnummer = request.form["telefoonnummer"]
            db.session.commit()
            flash("Accountgegevens bijgewerkt.")
            return redirect(url_for("routes.dashboard"))

        elif "update_health" in request.form:
            if not laatste_data:
                laatste_data = HealthData(user_id=user.id, date=datetime.utcnow().date())
                db.session.add(laatste_data)

            sleep_val = request.form.get("sleep_hours")
            steps_val = request.form.get("steps")
            heart_val = request.form.get("heart_rate")
            stress_val = request.form.get("stress_level")

            laatste_data.sleep_hours = float(sleep_val) if sleep_val else None
            laatste_data.steps = int(steps_val) if steps_val else None
            laatste_data.heart_rate = int(heart_val) if heart_val else None
            laatste_data.stress_level = stress_val or None

            db.session.commit()
            flash("Gezondheidsgegevens opgeslagen.")
            return redirect(url_for("routes.dashboard"))

    # Gemiddelde berekening
    slaap_avg = round(sum(d.sleep_hours for d in data if d.sleep_hours) / len(data), 1) if data else 0
    stappen_avg = round(sum(d.steps for d in data if d.steps) / len(data), 1) if data else 0
    hartslag_avg = round(sum(d.heart_rate for d in data if d.heart_rate) / len(data), 1) if data else 0

    return render_template("dashboard.html",
                           user=user,
                           slaap_avg=slaap_avg,
                           stappen_avg=stappen_avg,
                           hartslag_avg=hartslag_avg,
                           laatste_data=laatste_data)


@bp.route("/my-data", methods=["GET", "POST"])
def my_data():
    if "user_id" not in session:
        flash("Log eerst in.")
        return redirect(url_for("routes.login"))

    user_id = session["user_id"]
    latest = HealthData.query.filter_by(user_id=user_id).order_by(HealthData.date.desc()).first()

    if request.method == "POST":
        # Handmatige invoer
        if "manual_entry" in request.form:
            new = HealthData(
                user_id=user_id,
                date=datetime.utcnow().date(),
                sleep_hours=request.form.get("sleep_hours"),
                steps=request.form.get("steps"),
                heart_rate=request.form.get("heart_rate"),
                stress_level=request.form.get("stress_level"),
            )
            db.session.add(new)
            db.session.commit()
            flash("Gezondheidsgegevens succesvol toegevoegd.")
            return redirect(url_for("routes.my_data"))

        # Bestand uploaden
        elif "file_upload" in request.files:
            file = request.files["file_upload"]
            if not file:
                flash("Geen bestand gekozen.")
                return redirect(url_for("routes.my_data"))

            try:
                if file.filename.endswith(".csv"):
                    df = pd.read_csv(file)
                elif file.filename.endswith(".json"):
                    df = pd.read_json(file)
                else:
                    flash("Alleen .csv en .json bestanden zijn toegestaan.")
                    return redirect(url_for("routes.my_data"))

                for _, row in df.iterrows():
                    record = HealthData(
                        user_id=user_id,
                        date=row.get("date", datetime.utcnow().date()),
                        sleep_hours=row.get("sleep_hours"),
                        steps=row.get("steps"),
                        heart_rate=row.get("heart_rate"),
                        stress_level=row.get("stress_level"),
                    )
                    db.session.add(record)
                db.session.commit()
                flash(f"{len(df)} records geïmporteerd.")
                return redirect(url_for("routes.my_data"))

            except Exception as e:
                flash(f"Fout bij uploaden: {str(e)}")
                return redirect(url_for("routes.my_data"))

    return render_template("my_data.html", laatste_data=latest)


@bp.route('/data_analysis', methods=["GET"])
def data_analysis():
    if "user_id" not in session:
        flash("Log eerst in.")
        return redirect(url_for("routes.login"))

    user_id = session["user_id"]
    filter_days = request.args.get("filter", "all")

    # Data ophalen
    data = HealthData.query.filter_by(user_id=user_id).all()
    if not data:
        return render_template("data_analysis.html", message="Geen gegevens beschikbaar.")

    # Data omzetten naar DataFrame
    df = pd.DataFrame([{
        "date": d.date,
        "sleep_hours": d.sleep_hours,
        "steps": d.steps,
        "heart_rate": d.heart_rate,
        "stress_level": d.stress_level
    } for d in data])

    df["date"] = pd.to_datetime(df["date"])
    df.sort_values(by="date", inplace=True)

    # Filter toepassen
    if filter_days == "7":
        df = df[df["date"] >= datetime.now() - timedelta(days=7)]
    elif filter_days == "30":
        df = df[df["date"] >= datetime.now() - timedelta(days=30)]

    # AI-aanbeveling
    recommendations = []
    if df["sleep_hours"].mean() < 6:
        recommendations.append("Je slaapt gemiddeld minder dan 6u. Overweeg een vast slaapritme.")
    if df["steps"].mean() < 5000:
        recommendations.append("Je stappengemiddelde ligt onder de 5.000. Meer wandelen kan stress verlagen.")

    # Grafieken genereren
    def make_plot(y, title, ylabel):
        img = io.BytesIO()
        plt.figure(figsize=(8, 3.5))
        plt.plot(df["date"], df[y], marker="o")
        plt.title(title)
        plt.xlabel("Datum")
        plt.ylabel(ylabel)
        plt.xticks(rotation=45)
        plt.tight_layout()
        plt.grid(True)
        plt.savefig(img, format="png")
        plt.close()
        img.seek(0)
        return base64.b64encode(img.getvalue()).decode()

    slaap_plot = make_plot("sleep_hours", "Slaapduur", "Uren slaap")
    stappen_plot = make_plot("steps", "Stappen per dag", "Aantal stappen")
    hartslag_plot = make_plot("heart_rate", "Gemiddelde hartslag", "Hartslagen/min")

    return render_template("data_analysis.html",
                           selected=filter_days,
                           graph_slaap=slaap_plot,
                           graph_stappen=stappen_plot,
                           graph_hartslag=hartslag_plot,
                           recommendations=recommendations,
                           filter=filter_days)

@bp.route('/export_csv')
def export_csv():
    if "user_id" not in session:
        flash("Log eerst in.")
        return redirect(url_for("routes.login"))

    user_id = session["user_id"]
    data = HealthData.query.filter_by(user_id=user_id).all()

    df = pd.DataFrame([{
        "date": d.date,
        "sleep_hours": d.sleep_hours,
        "steps": d.steps,
        "heart_rate": d.heart_rate,
        "stress_level": d.stress_level
    } for d in data])

    output = io.StringIO()
    df.to_csv(output, index=False)
    output.seek(0)

    return send_file(io.BytesIO(output.getvalue().encode()),
                     mimetype="text/csv",
                     as_attachment=True,
                     download_name="vitalview_data.csv")

@bp.route("/recommendations")
def recommendations():
    if "user_id" not in session:
        flash("Log eerst in om aanbevelingen te bekijken.")
        return redirect(url_for("routes.login"))

    user = User.query.get(session["user_id"])
    data = HealthData.query.filter_by(user_id=user.id).all()

    recommendations = []

    if data:
        slaapgem = round(sum(d.sleep_hours for d in data if d.sleep_hours) / len(data), 1)
        stappen = round(sum(d.steps for d in data if d.steps) / len(data), 1)
        hartslag = round(sum(d.heart_rate for d in data if d.heart_rate) / len(data), 1)
        # Stresslevels kunnen zowel numeriek als tekstueel opgeslagen zijn.
        # Enkel numerieke waarden worden gemiddeld om fouten te voorkomen.
        stress_values = [
            int(d.stress_level)
            for d in data
            if d.stress_level is not None and str(d.stress_level).isdigit()
        ]
        stress = round(sum(stress_values) / len(stress_values), 1) if stress_values else 0

        if slaapgem < 6:
            recommendations.append("Je slaapt gemiddeld minder dan 6 uur. Probeer vroeger te gaan slapen.")
        if stappen < 5000:
            recommendations.append("Je zet minder dan 5.000 stappen per dag. Overweeg meer dagelijkse beweging.")
        if stress > 6:
            recommendations.append("Je stressniveau is hoog. Probeer ontspanningstechnieken zoals ademhaling of yoga.")
        if hartslag > 90:
            recommendations.append("Je hartslag is gemiddeld vrij hoog. Raadpleeg eventueel je arts.")

    return render_template("recommendations.html", recommendations=recommendations)

@bp.route("/upload_data", methods=["GET", "POST"])
def upload_data():
    if "user_id" not in session:
        flash("Log eerst in om gegevens te uploaden.")
        return redirect(url_for("routes.login"))

    if request.method == "POST":
        file = request.files.get("file")
        if not file:
            flash("Geen bestand geselecteerd.")
            return redirect(request.url)

        filename = secure_filename(file.filename)
        user_id = session["user_id"]
        count = 0

        try:
            if filename.endswith(".csv"):
                stream = file.stream.read().decode("utf-8").splitlines()
                reader = csv.DictReader(stream)
                for row in reader:
                    new_entry = HealthData(
                        user_id=user_id,
                        date=datetime.strptime(row["date"], "%Y-%m-%d").date(),
                        sleep_hours=float(row.get("sleep_hours", 0)),
                        steps=int(row.get("steps", 0)),
                        heart_rate=int(row.get("heart_rate", 0)),
                        stress_level=int(row.get("stress_level", 0))
                    )
                    db.session.add(new_entry)
                    count += 1

            elif filename.endswith(".json"):
                data = json.load(file)
                for entry in data:
                    new_entry = HealthData(
                        user_id=user_id,
                        date=datetime.strptime(entry["date"], "%Y-%m-%d").date(),
                        sleep_hours=float(entry.get("sleep_hours", 0)),
                        steps=int(entry.get("steps", 0)),
                        heart_rate=int(entry.get("heart_rate", 0)),
                        stress_level=int(entry.get("stress_level", 0))
                    )
                    db.session.add(new_entry)
                    count += 1

            else:
                flash("Ongeldig bestandstype. Enkel .csv of .json is toegestaan.")
                return redirect(request.url)

            db.session.commit()
            return redirect(url_for("routes.dashboard"))

        except Exception as e:
            db.session.rollback()
            flash(f"Fout bij het verwerken van het bestand: {str(e)}")

    return render_template("upload_data.html")


from flask_mail import Message
from app import mail

@bp.route("/forgot_password")
def forgot_password():
    flash("Wachtwoord vergeten-functionaliteit is nog niet geïmplementeerd.")
    return redirect(url_for("routes.login"))
