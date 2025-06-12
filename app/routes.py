from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify, send_file
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from authlib.integrations.flask_client import OAuth
from models import db, User, HealthData, AuditLog, ContactMessage
from utils import generate_pdf_report, export_to_csv
from datetime import datetime
import pandas as pd
import plotly.express as px
from io import BytesIO
import os
from werkzeug.security import generate_password_hash
import logging
from functools import wraps

app = Flask(__name__)
app.secret_key = os.environ.get('FLASK_SECRET_KEY', 'dev-secret-key')

# Auth0 Config
oauth = OAuth(app)
auth0 = oauth.register(
    'auth0',
    client_id='Euz1mW8N2cpQT3VoMXFAEIAZ01fhBQN3',
    client_secret='auxqtovw7uMZPxFVu3BL_SRdmYJBH0Zdg0tyz4iwDWyHJmWcmle4u50NZquFfyto',
    api_base_url=f"https://dev-qri4asc6ndkott2u.uk.auth0.com",
    access_token_url=f"https://dev-qri4asc6ndkott2u.uk.auth0.com/oauth/token",
    authorize_url=f"https://dev-qri4asc6ndkott2u.uk.auth0.com/authorize",
    client_kwargs={'scope': 'openid profile email'},
)

# Login Manager
login_manager = LoginManager(app)
login_manager.login_view = 'login'


# Decorators
def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_admin:
            flash('Admin access required', 'danger')
            return redirect(url_for('profile'))
        return f(*args, **kwargs)

    return decorated_function


# Routes
@app.route('/')
def home():
    return render_template('home.html', dark_mode=session.get('dark_mode', False))


@app.route('/login')
def login():
    return auth0.authorize_redirect(
        redirect_uri=url_for('callback', _external=True),
        audience=f"https://dev-qri4asc6ndkott2u.uk.auth0.com/userinfo"
    )


@app.route('/callback')
def callback():
    try:
        token = auth0.authorize_access_token()
        resp = auth0.get('userinfo')
        userinfo = resp.json()

        # Create or update user
        user = User.query.filter_by(auth0_id=userinfo['sub']).first()
        if not user:
            user = User(
                auth0_id=userinfo['sub'],
                email=userinfo['email'],
                name=userinfo.get('name', ''),
                is_admin=userinfo['email'] in os.environ.get('ADMIN_WHITELIST', '').split(',')
            )
            db.session.add(user)
            db.session.commit()

        login_user(user)
        return redirect(url_for('profile'))
    except Exception as e:
        logging.error(f"Auth error: {str(e)}")
        flash('Login failed', 'danger')
        return redirect(url_for('home'))


@app.route('/logout')
@login_required
def logout():
    logout_user()
    session.clear()
    params = {
        'returnTo': url_for('home', _external=True),
        'client_id': 'Euz1mW8N2cpQT3VoMXFAEIAZ01fhBQN3'
    }
    return redirect(auth0.api_base_url + '/v2/logout?' + urlencode(params))


@app.route('/profile')
@login_required
def profile():
    health_data = HealthData.query.filter_by(user_id=current_user.id).order_by(HealthData.date.desc()).first()
    all_data = HealthData.query.filter_by(user_id=current_user.id).all()

    # Generate Plotly graphs
    if all_data:
        df = pd.DataFrame([{
            'date': d.date,
            'steps': d.steps,
            'heart_rate': d.heart_rate,
            'sleep': d.sleep_hours
        } for d in all_data])

        steps_fig = px.line(df, x='date', y='steps', title='Step History')
        steps_graph = steps_fig.to_html(full_html=False)

        hr_fig = px.line(df, x='date', y='heart_rate', title='Heart Rate History')
        hr_graph = hr_fig.to_html(full_html=False)
    else:
        steps_graph = hr_graph = None

    return render_template('profile.html',
                           user=current_user,
                           health_data=health_data,
                           steps_graph=steps_graph,
                           hr_graph=hr_graph,
                           dark_mode=session.get('dark_mode', False)
                           )


@app.route('/profile/update', methods=['POST'])
@login_required
def update_profile():
    try:
        current_user.name = request.form.get('name', current_user.name)

        # Update health data
        health_data = HealthData(
            user_id=current_user.id,
            weight=float(request.form['weight']),
            height=float(request.form['height']),
            steps=int(request.form.get('steps', 0)),
            heart_rate=int(request.form.get('heart_rate', 0)),
            sleep_hours=float(request.form.get('sleep_hours', 0)),
            date=datetime.utcnow()
        )
        db.session.add(health_data)
        db.session.commit()
        flash('Profile updated successfully', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Update failed: {str(e)}', 'danger')

    return redirect(url_for('profile'))


@app.route('/admin')
@login_required
@admin_required
def admin_dashboard():
    users = User.query.all()
    health_data = HealthData.query.order_by(HealthData.date.desc()).limit(100).all()

    # Generate admin graphs
    df = pd.DataFrame([{
        'user': d.user.name,
        'date': d.date,
        'bmi': d.weight / ((d.height / 100) ** 2)
    } for d in health_data])

    bmi_fig = px.box(df, x='user', y='bmi', title='BMI Distribution')
    bmi_graph = bmi_fig.to_html(full_html=False)

    return render_template('admin.html',
                           users=users,
                           health_data=health_data,
                           bmi_graph=bmi_graph,
                           dark_mode=session.get('dark_mode', False)
                           )


@app.route('/admin/export/csv')
@login_required
@admin_required
def export_csv():
    data = HealthData.query.all()
    csv_data = export_to_csv(data)
    return send_file(
        BytesIO(csv_data.encode()),
        mimetype='text/csv',
        as_attachment=True,
        download_name='health_data_export.csv'
    )


@app.route('/admin/export/pdf')
@login_required
@admin_required
def export_pdf():
    data = HealthData.query.limit(50).all()
    pdf = generate_pdf_report(data)
    return send_file(
        BytesIO(pdf),
        mimetype='application/pdf',
        as_attachment=True,
        download_name='health_report.pdf'
    )


@app.route('/contact', methods=['GET', 'POST'])
def contact():
    if request.method == 'POST':
        try:
            message = ContactMessage(
                name=request.form['name'],
                email=request.form['email'],
                message=request.form['message'],
                created_at=datetime.utcnow()
            )
            db.session.add(message)
            db.session.commit()
            flash('Message sent successfully!', 'success')
            return redirect(url_for('contact'))
        except Exception as e:
            flash(f'Error: {str(e)}', 'danger')

    return render_template('contact.html', dark_mode=session.get('dark_mode', False))


@app.route('/settings', methods=['GET', 'POST'])
@login_required
def settings():
    if request.method == 'POST':
        # Dark mode toggle
        if 'dark_mode' in request.form:
            session['dark_mode'] = request.form['dark_mode'] == 'on'

        # GDPR delete request
        if 'delete_account' in request.form:
            HealthData.query.filter_by(user_id=current_user.id).delete()
            db.session.commit()
            flash('All your health data has been deleted', 'info')

        return redirect(url_for('settings'))

    return render_template('settings.html', dark_mode=session.get('dark_mode', False))


@app.route('/about')
def about():
    return render_template('about.html', dark_mode=session.get('dark_mode', False))


@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404


# API Endpoints
@app.route('/api/health-data', methods=['GET'])
@login_required
def api_health_data():
    data = HealthData.query.filter_by(user_id=current_user.id).all()
    return jsonify([{
        'date': d.date.isoformat(),
        'steps': d.steps,
        'heart_rate': d.heart_rate,
        'sleep_hours': d.sleep_hours,
        'bmi': d.weight / ((d.height / 100) ** 2)
    } for d in data])


if __name__ == '__main__':
    app.run(debug=True)