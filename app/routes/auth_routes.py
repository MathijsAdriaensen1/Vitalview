"""
Bevat de login, callback en logout routes voor Auth0-integratie.
"""

from flask import Blueprint, redirect, session, url_for, jsonify
from authlib.integrations.flask_client import OAuth
from flask import current_app as app
import os

auth_bp = Blueprint("auth", __name__)
oauth = OAuth()

# Auth0 config
oauth.register(
    "auth0",
    client_id=os.getenv("AUTH0_CLIENT_ID"),
    client_secret=os.getenv("AUTH0_CLIENT_SECRET"),
    api_base_url=f"https://{os.getenv('AUTH0_DOMAIN')}",
    access_token_url=f"https://{os.getenv('AUTH0_DOMAIN')}/oauth/token",
    authorize_url=f"https://{os.getenv('AUTH0_DOMAIN')}/authorize",
    client_kwargs={"scope": "openid profile email"},
)

@auth_bp.before_app_request
def setup_oauth():
    oauth.init_app(app)

@auth_bp.route("/login")
def login():
    return oauth.auth0.authorize_redirect(redirect_uri=os.getenv("AUTH0_CALLBACK_URL"))

@auth_bp.route("/callback")
def callback():
    token = oauth.auth0.authorize_access_token()
    userinfo = token.get("userinfo")
    session["user"] = userinfo
    return redirect("/dashboard")

@auth_bp.route("/logout")
def logout():
    session.clear()
    return redirect(
        f"https://{os.getenv('AUTH0_DOMAIN')}/v2/logout?returnTo=http://localhost:5000&client_id={os.getenv('AUTH0_CLIENT_ID')}"
    )
