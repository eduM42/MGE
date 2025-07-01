from flask import Blueprint, render_template, session, redirect, url_for
from app.utils.api import api_get
from app.helpers.navbarHelper import get_navbar_state

export_bp = Blueprint('export', __name__)

@export_bp.route('/export_measurements', methods=['GET'])
def export_measurements():
    if 'access_token' not in session:
        return redirect(url_for('auth.login'))
    user_resp = api_get('/auth/me')
    if user_resp.status_code != 200:
        return redirect(url_for('auth.login'))
    user = user_resp.json()
    navbar_state = get_navbar_state()
    return render_template('export_measurements.html', user=user, navbar_state=navbar_state, active_page='export')
