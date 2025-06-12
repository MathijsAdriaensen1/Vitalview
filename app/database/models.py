from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from datetime import datetime
from sqlalchemy import event
from werkzeug.security import generate_password_hash
import uuid

db = SQLAlchemy()


# 🔐 Auth0 User + Local Auth Fallback
class User(db.Model, UserMixin):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    auth0_id = db.Column(db.String(128), unique=True)  # Auth0 identifier
    email = db.Column(db.String(120), unique=True, nullable=False)
    email_verified = db.Column(db.Boolean, default=False)
    name = db.Column(db.String(100))
    voornaam = db.Column(db.String(50))
    achternaam = db.Column(db.String(50))
    telefoonnummer = db.Column(db.String(20))
    profiel_foto = db.Column(db.String(256), default='default.png')
    dark_mode = db.Column(db.Boolean, default=False)
    taal = db.Column(db.String(2), default='nl')
    is_admin = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    last_login = db.Column(db.DateTime)

    # Local auth fallback (optioneel)
    password_hash = db.Column(db.String(128))

    # Relationships
    health_data = db.relationship('HealthData', backref='user', lazy='dynamic', cascade='all, delete-orphan')
    contact_messages = db.relationship('ContactMessage', backref='user', lazy='dynamic')
    audit_logs = db.relationship('AuditLog', backref='user', lazy='dynamic')

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    @property
    def bmi(self):
        latest_data = self.health_data.order_by(HealthData.date.desc()).first()
        if latest_data and latest_data.height > 0:
            return latest_data.weight / ((latest_data.height / 100) ** 2)
        return None


# 📊 Health Data Model (Uitgebreid)
class HealthData(db.Model):
    __tablename__ = "health_data"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    date = db.Column(db.DateTime, default=datetime.utcnow, index=True)

    # Basis metrics
    weight = db.Column(db.Float)  # kg
    height = db.Column(db.Float)  # cm
    steps = db.Column(db.Integer)  # stappen
    heart_rate = db.Column(db.Integer)  # bpm
    blood_pressure_systolic = db.Column(db.Integer)  # mmHg
    blood_pressure_diastolic = db.Column(db.Integer)  # mmHg
    sleep_hours = db.Column(db.Float)  # uren
    water_intake = db.Column(db.Float)  # liter
    mood = db.Column(db.String(20))  # happy, neutral, sad

    # Geavanceerde metrics
    blood_oxygen = db.Column(db.Float)  # SpO2 %
    blood_sugar = db.Column(db.Float)  # mmol/L
    activity_minutes = db.Column(db.Integer)  # actieve minuten

    # Metadata
    source = db.Column(db.String(50))  # manual/wearable/app
    notes = db.Column(db.Text)

    def calculate_bmi(self):
        if self.height > 0:
            return self.weight / ((self.height / 100) ** 2)
        return None


# 📨 Contact Formulier Model (Uitgebreid)
class ContactMessage(db.Model):
    __tablename__ = "contact_messages"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), nullable=False)
    phone = db.Column(db.String(20))
    subject = db.Column(db.String(100), nullable=False)
    message = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    is_read = db.Column(db.Boolean, default=False)
    response = db.Column(db.Text)
    response_at = db.Column(db.DateTime)

    # Categorisatie
    category = db.Column(db.String(50))  # vraag/klacht/suggestie
    priority = db.Column(db.Integer)  # 1-5


# 📜 Audit Log voor Admin Acties
class AuditLog(db.Model):
    __tablename__ = "audit_logs"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    action = db.Column(db.String(50), nullable=False)  # login/export/delete/etc.
    entity_type = db.Column(db.String(50))
    entity_id = db.Column(db.Integer)
    ip_address = db.Column(db.String(45))
    user_agent = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    details = db.Column(db.JSON)  # Voor complexe data


# 📦 Data Export Logs
class ExportLog(db.Model):
    __tablename__ = "export_logs"

    id = db.Column(db.Integer, primary_key=True)
    admin_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    export_type = db.Column(db.String(10), nullable=False)  # CSV/PDF/JSON
    filters = db.Column(db.JSON)  # Bewaar gebruikte filters
    file_name = db.Column(db.String(100))
    record_count = db.Column(db.Integer)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    user = db.relationship('User', backref='exports')


# 🔄 Database Triggers
@event.listens_for(HealthData, 'after_insert')
def log_health_data_insert(mapper, connection, target):
    if target.user_id:
        connection.execute(
            AuditLog.__table__.insert().values(
                user_id=target.user_id,
                action='health_data_create',
                entity_type='health_data',
                entity_id=target.id,
                details={'metric': 'weight' if target.weight else 'heart_rate' if target.heart_rate else 'other'}
            )
        )


@event.listens_for(User, 'after_update')
def log_user_changes(mapper, connection, target):
    if target.is_admin:
        connection.execute(
            AuditLog.__table__.insert().values(
                user_id=target.id,
                action='admin_status_update',
                entity_type='user',
                entity_id=target.id,
                details={'new_status': target.is_admin}
            )
        )