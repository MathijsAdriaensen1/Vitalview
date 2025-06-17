from app import db
from datetime import datetime

class User(db.Model):
    __tablename__ = "inlog_gegevens"

    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    voornaam = db.Column(db.String(100))
    achternaam = db.Column(db.String(100))
    telefoonnummer = db.Column(db.String(20))
    date_joined = db.Column(db.DateTime, default=datetime.utcnow)
    role = db.Column(db.String(20), default="user")
    hashed_password = db.Column(db.String(200), nullable=False)

class HealthData(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("inlog_gegevens.id"))
    date = db.Column(db.Date, nullable=False)
    heart_rate = db.Column(db.Integer)
    steps = db.Column(db.Integer)
    sleep_hours = db.Column(db.Float)
    stress_level = db.Column(db.String(10))  # laag, gemiddeld, hoog

class ContactBericht(db.Model):  # ContactMessage → ContactBericht
    id = db.Column(db.Integer, primary_key=True)  # Bericht-ID
    naam = db.Column(db.String(100), nullable=False)  # Naam
    emailadres = db.Column(db.String(120), nullable=False)  # E-mailadres
    onderwerp = db.Column(db.String(100), nullable=False)  # Onderwerp
    telefoonnummer = db.Column(db.String(20))  # Telefoonnummer (optioneel)
    bericht = db.Column(db.Text, nullable=False)  # Berichttekst
    verzonden_op = db.Column(db.DateTime, default=datetime.utcnow)  # Tijdstip van verzending


class AuditLog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer)
    action = db.Column(db.String(255))
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)