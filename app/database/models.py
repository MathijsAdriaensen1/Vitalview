from .session import db
from datetime import datetime

class User(db.Model):
    __tablename__ = "users"
    id = db.Column(db.Integer, primary_key=True)
    auth0_id = db.Column(db.String(128), unique=True, nullable=False)
    email = db.Column(db.String(128), unique=True, nullable=False)
    name = db.Column(db.String(128))
    is_admin = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    profile = db.relationship("Profile", backref="user", uselist=False)
    logs = db.relationship("HealthLog", backref="user", lazy=True)
    messages = db.relationship("Message", backref="user", lazy=True)

class Profile(db.Model):
    __tablename__ = "profiles"
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    age = db.Column(db.Integer)
    gender = db.Column(db.String(10))
    height_cm = db.Column(db.Float)
    weight_kg = db.Column(db.Float)
    goal = db.Column(db.String(255))

class HealthLog(db.Model):
    __tablename__ = "health_logs"
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    date = db.Column(db.Date, default=datetime.utcnow)
    steps = db.Column(db.Integer)
    heart_rate = db.Column(db.Integer)
    sleep_hours = db.Column(db.Float)
    stress_level = db.Column(db.String(50))

class WorkoutPlan(db.Model):
    __tablename__ = "workout_plans"
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(128))
    description = db.Column(db.Text)
    duration_weeks = db.Column(db.Integer)
    intensity = db.Column(db.String(50))

class UserWorkout(db.Model):
    __tablename__ = "user_workouts"
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    plan_id = db.Column(db.Integer, db.ForeignKey("workout_plans.id"), nullable=False)
    start_date = db.Column(db.Date)
    completed = db.Column(db.Boolean, default=False)

class Appointment(db.Model):
    __tablename__ = "appointments"
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    datetime = db.Column(db.DateTime)
    subject = db.Column(db.String(128))
    status = db.Column(db.String(50))

class Message(db.Model):
    __tablename__ = "messages"
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"))
    content = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class Notification(db.Model):
    __tablename__ = "notifications"
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"))
    title = db.Column(db.String(128))
    body = db.Column(db.Text)
    seen = db.Column(db.Boolean, default=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
