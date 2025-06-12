from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify, send_file
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from authlib.integrations.flask_client import OAuth
from models import db, Gebruiker, GezondheidsData, AuditLog, ContactBericht
from utils import genereer_pdf_rapport, exporteer_naar_csv
from datetime import datetime
import pandas as pd
import plotly.express as px
from io import BytesIO
import os
from werkzeug.security import generate_password_hash
import logging
from functools import wraps
from urllib.parse import urlencode

app = Flask(__name__)
app.secret_key = os.environ.get('FLASK_GEHEIME_SLEUTEL', 'dev-geheime-sleutel')

# Auth0 Configuratie
oauth = OAuth(app)
auth0 = oauth.register(
    'auth0',
    client_id='Euz1mW8N2cpQT3VoMXFAEIAZ01fhBQN3',
    client_secret='auxqtovw7uMZPxFVu3BL_SRdmYJBH0Zdg0tyz4iwDWyHJmWcmle4u50NZquFfyto',
    api_base_url="https://dev-qri4asc6ndkott2u.uk.auth0.com",
    access_token_url="https://dev-qri4asc6ndkott2u.uk.auth0.com/oauth/token",
    authorize_url="https://dev-qri4asc6ndkott2u.uk.auth0.com/authorize",
    client_kwargs={'scope': 'openid profile email'},
)

# Login Manager
login_manager = LoginManager(app)
login_manager.login_view = 'inloggen'

# Decorators
def admin_vereist(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_admin:
            flash('Admin toegang vereist', 'gevaar')
            return redirect(url_for('profiel'))
        return f(*args, **kwargs)
    return decorated_function

# Routes
@app.route('/')
def home():
    return render_template('home.html')

@app.route('/inloggen')
def inloggen():
    return auth0.authorize_redirect(
        redirect_uri=url_for('callback', _external=True),
        audience="https://dev-qri4asc6ndkott2u.uk.auth0.com/userinfo"
    )

@app.route('/callback')
def callback():
    try:
        token = auth0.authorize_access_token()
        resp = auth0.get('userinfo')
        gebruikersinfo = resp.json()

        # Maak of update gebruiker
        gebruiker = Gebruiker.query.filter_by(auth0_id=gebruikersinfo['sub']).first()
        if not gebruiker:
            gebruiker = Gebruiker(
                auth0_id=gebruikersinfo['sub'],
                email=gebruikersinfo['email'],
                naam=gebruikersinfo.get('name', ''),
                is_admin=gebruikersinfo['email'] in os.environ.get('ADMIN_WHITELIST', '').split(',')
            )
            db.session.add(gebruiker)
            db.session.commit()

        login_user(gebruiker)
        return redirect(url_for('profiel'))
    except Exception as e:
        logging.error(f"Auth fout: {str(e)}")
        flash('Inloggen mislukt', 'gevaar')
        return redirect(url_for('home'))

@app.route('/uitloggen')
@login_required
def uitloggen():
    logout_user()
    session.clear()
    params = {
        'returnTo': url_for('home', _external=True),
        'client_id': 'Euz1mW8N2cpQT3VoMXFAEIAZ01fhBQN3'
    }
    return redirect(auth0.api_base_url + '/v2/logout?' + urlencode(params))

@app.route('/profiel')
@login_required
def profiel():
    gezondheidsdata = GezondheidsData.query.filter_by(gebruiker_id=current_user.id).order_by(GezondheidsData.datum.desc()).first()
    alle_data = GezondheidsData.query.filter_by(gebruiker_id=current_user.id).all()

    # Genereer grafieken
    if alle_data:
        df = pd.DataFrame([{
            'datum': d.datum,
            'stappen': d.stappen,
            'hartslag': d.hartslag,
            'slaap': d.slaap_uren
        } for d in alle_data])

        stappen_fig = px.line(df, x='datum', y='stappen', title='Stappen Geschiedenis')
        stappen_grafiek = stappen_fig.to_html(full_html=False)

        hartslag_fig = px.line(df, x='datum', y='hartslag', title='Hartslag Geschiedenis')
        hartslag_grafiek = hartslag_fig.to_html(full_html=False)
    else:
        stappen_grafiek = hartslag_grafiek = None

    return render_template('profiel.html',
                         gebruiker=current_user,
                         gezondheidsdata=gezondheidsdata,
                         stappen_grafiek=stappen_grafiek,
                         hartslag_grafiek=hartslag_grafiek)

@app.route('/profiel/bewerken', methods=['POST'])
@login_required
def profiel_bewerken():
    try:
        current_user.naam = request.form.get('naam', current_user.naam)

        # Update gezondheidsdata
        gezondheidsdata = GezondheidsData(
            gebruiker_id=current_user.id,
            gewicht=float(request.form['gewicht']),
            lengte=float(request.form['lengte']),
            stappen=int(request.form.get('stappen', 0)),
            hartslag=int(request.form.get('hartslag', 0)),
            slaap_uren=float(request.form.get('slaap_uren', 0)),
            datum=datetime.utcnow()
        )
        db.session.add(gezondheidsdata)
        db.session.commit()
        flash('Profiel succesvol bijgewerkt', 'succes')
    except Exception as e:
        db.session.rollback()
        flash(f'Update mislukt: {str(e)}', 'gevaar')

    return redirect(url_for('profiel'))

@app.route('/admin')
@login_required
@admin_vereist
def admin_dashboard():
    gebruikers = Gebruiker.query.all()
    gezondheidsdata = GezondheidsData.query.order_by(GezondheidsData.datum.desc()).limit(100).all()

    # Genereer admin grafieken
    df = pd.DataFrame([{
        'gebruiker': d.gebruiker.naam,
        'datum': d.datum,
        'bmi': d.gewicht / ((d.lengte / 100) ** 2)
    } for d in gezondheidsdata])

    bmi_fig = px.box(df, x='gebruiker', y='bmi', title='BMI Verdeling')
    bmi_grafiek = bmi_fig.to_html(full_html=False)

    return render_template('admin.html',
                         gebruikers=gebruikers,
                         gezondheidsdata=gezondheidsdata,
                         bmi_grafiek=bmi_grafiek)

@app.route('/admin/export/csv')
@login_required
@admin_vereist
def exporteer_csv():
    data = GezondheidsData.query.all()
    csv_data = exporteer_naar_csv(data)
    return send_file(
        BytesIO(csv_data.encode()),
        mimetype='text/csv',
        as_attachment=True,
        download_name='gezondheidsdata_export.csv'
    )

@app.route('/admin/export/pdf')
@login_required
@admin_vereist
def exporteer_pdf():
    data = GezondheidsData.query.limit(50).all()
    pdf = genereer_pdf_rapport(data)
    return send_file(
        BytesIO(pdf),
        mimetype='application/pdf',
        as_attachment=True,
        download_name='gezondheidsrapport.pdf'
    )

@app.route('/contact', methods=['GET', 'POST'])
def contact():
    if request.method == 'POST':
        try:
            bericht = ContactBericht(
                naam=request.form['naam'],
                email=request.form['email'],
                bericht=request.form['bericht'],
                aangemaakt_op=datetime.utcnow()
            )
            db.session.add(bericht)
            db.session.commit()
            flash('Bericht succesvol verzonden!', 'succes')
            return redirect(url_for('contact'))
        except Exception as e:
            flash(f'Fout: {str(e)}', 'gevaar')

    return render_template('contact.html')

@app.route('/instellingen', methods=['GET', 'POST'])
@login_required
def instellingen():
    if request.method == 'POST':
        # GDPR verwijderverzoek
        if 'account_verwijderen' in request.form:
            GezondheidsData.query.filter_by(gebruiker_id=current_user.id).delete()
            db.session.commit()
            flash('Alle je gezondheidsdata is verwijderd', 'info')

        return redirect(url_for('instellingen'))

    return render_template('instellingen.html')

@app.route('/over-ons')
def over_ons():
    return render_template('over_ons.html')

@app.errorhandler(404)
def pagina_niet_gevonden(e):
    return render_template('404.html'), 404

# API Endpoints
@app.route('/api/gezondheidsdata', methods=['GET'])
@login_required
def api_gezondheidsdata():
    data = GezondheidsData.query.filter_by(gebruiker_id=current_user.id).all()
    return jsonify([{
        'datum': d.datum.isoformat(),
        'stappen': d.stappen,
        'hartslag': d.hartslag,
        'slaap_uren': d.slaap_uren,
        'bmi': d.gewicht / ((d.lengte / 100) ** 2)
    } for d in data])

if __name__ == '__main__':
    app.run(debug=True)