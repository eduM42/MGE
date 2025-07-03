from flask import Blueprint, render_template, session, redirect, url_for, request, flash, send_file
from app.utils.api import api_get, api_post
from app.helpers.navbarHelper import get_navbar_state
import io

export_bp = Blueprint('export', __name__)

@export_bp.route('/export_measurements', methods=['GET', 'POST'])
def export_measurements():
    if 'access_token' not in session:
        return redirect(url_for('auth.login'))
    user_resp = api_get('/auth/me')
    if user_resp.status_code != 200:
        return redirect(url_for('auth.login'))
    user = user_resp.json()
    navbar_state = get_navbar_state()
    # Get devices for dropdown
    devices_resp = api_get('/devices/')
    devices = devices_resp.json() if devices_resp.status_code == 200 else []
    if request.method == 'POST':
        file_format = request.form.get('file_format', 'csv')
        timeframe = request.form.get('timeframe', 'last_24h')
        start_date = request.form.get('start_date')
        end_date = request.form.get('end_date')
        selected_devices = request.form.getlist('devices')
        measurements = request.form.getlist('measurements')
        # Prepare payload for backend
        payload = {
            'file_format': file_format,
            'timeframe': timeframe,
            'start_date': start_date,
            'end_date': end_date,
            'devices': selected_devices,
            'measurements': measurements
        }
        # Call backend export endpoint (assume /measurements/export exists and returns file)
        resp = api_post('/measurements/export', json=payload, stream=True)
        if resp.status_code == 200:
            filename = f"export.{file_format}"
            return send_file(io.BytesIO(resp.content), as_attachment=True, download_name=filename)
        else:
            flash('Erro ao exportar medições.', 'danger')
    return render_template('export_measurements.html', user=user, devices=devices, navbar_state=navbar_state, active_page='export')
