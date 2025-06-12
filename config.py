import os

class Config:
    SECRET_KEY = os.environ.get("SECRET_KEY", "vitalview-secret-key")
    SQLALCHEMY_DATABASE_URI = os.environ.get("DATABASE_URL", "sqlite:///vitalview.db")
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # Auth0
    AUTH0_CLIENT_ID = os.environ.get("AUTH0_CLIENT_ID")
    AUTH0_CLIENT_SECRET = os.environ.get("AUTH0_CLIENT_SECRET")
    AUTH0_DOMAIN = os.environ.get("AUTH0_DOMAIN")
    AUTH0_CALLBACK_URL = os.environ.get("AUTH0_CALLBACK_URL")
    AUTH0_AUDIENCE = os.environ.get("AUTH0_AUDIENCE")