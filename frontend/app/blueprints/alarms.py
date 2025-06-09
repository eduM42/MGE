from flask import Blueprint, render_template, redirect, url_for, session, flash, request
from app.utils.api import api_get, api_post, api_delete, api_put, api_patch
from app.helpers.navbarHelper import get_navbar_state

alarms_bp = Blueprint('alarms', __name__)

@alarms_bp.route('/alarms', methods=['GET'])
def alarms():
    if 'access_token' not in session:
        return redirect(url_for('auth.login'))
    user_resp = api_get('/auth/me')
    if user_resp.status_code != 200:
        flash('Não foi possível obter informações do usuário. Faça login novamente.', 'danger')
        session.pop('access_token', None)
        return redirect(url_for('auth.login'))
    user = user_resp.json()
    alarms_resp = api_get('/alarms')
    alarms = alarms_resp.json() if alarms_resp.status_code == 200 else []
    devices_resp = api_get('/devices')
    devices = devices_resp.json() if devices_resp.status_code == 200 else []
    triggered_alarms_resp = api_get('/triggered_alarms')
    triggered_alarms = triggered_alarms_resp.json() if triggered_alarms_resp.status_code == 200 else []
    navbar_state = get_navbar_state()
    return render_template('alarms.html', user=user, alarms=alarms, devices=devices, triggered_alarms=triggered_alarms, navbar_state=navbar_state, active_page='alarms')

@alarms_bp.route('/alarms/create', methods=['POST'])
def create_alarm():
    if 'access_token' not in session:
        return redirect(url_for('auth.login'))
    name = request.form.get('alarm_name')
    description = request.form.get('alarm_description')
    alarm_type = request.form.get('alarm_type')
    threshold = request.form.get('threshold')
    device_id = request.form.get('device_id') or None
    active = 'activate_immediately' in request.form
    # Notification channels
    send_sms = 'send_sms' in request.form
    send_email = 'send_email' in request.form
    send_whatsapp = 'send_whatsapp' in request.form
    payload = {
        'name': name,
        'description': description,
        'type': alarm_type,
        'threshold': float(threshold) if threshold else 0,
        'device_id': device_id,
        'active': active,
        'send_sms': send_sms,
        'send_email': send_email,
        'send_whatsapp': send_whatsapp
    }
    resp = api_post('/alarms', json=payload)
    if resp.status_code == 201:
        flash('Alarme criado com sucesso!', 'success')
    else:
        flash('Erro ao criar alarme.', 'danger')
    return redirect(url_for('alarms.alarms'))

@alarms_bp.route('/alarms/edit/<alarm_id>', methods=['POST'])
def edit_alarm(alarm_id):
    if 'access_token' not in session:
        return redirect(url_for('auth.login'))
    name = request.form.get('alarm_name')
    description = request.form.get('alarm_description')
    alarm_type = request.form.get('alarm_type')
    threshold = request.form.get('threshold')
    device_id = request.form.get('device_id') or None
    active = 'activate_immediately' in request.form
    send_sms = 'send_sms' in request.form
    send_email = 'send_email' in request.form
    send_whatsapp = 'send_whatsapp' in request.form
    payload = {
        'name': name,
        'description': description,
        'type': alarm_type,
        'threshold': float(threshold) if threshold else 0,
        'device_id': device_id,
        'active': active,
        'send_sms': send_sms,
        'send_email': send_email,
        'send_whatsapp': send_whatsapp
    }
    resp = api_put(f'/alarms/{alarm_id}', json=payload)
    if resp.status_code == 200:
        flash('Alarme atualizado com sucesso!', 'success')
    else:
        flash('Erro ao atualizar alarme.', 'danger')
    return redirect(url_for('alarms.alarms'))

@alarms_bp.route('/alarms/toggle/<alarm_id>', methods=['POST'])
def toggle_alarm(alarm_id):
    if 'access_token' not in session:
        return redirect(url_for('auth.login'))
    active = request.form.get('active') == 'True'
    payload = {'active': active}
    # Use PATCH for partial update
    resp = api_patch(f'/alarms/{alarm_id}', json=payload)
    if resp.status_code == 200:
        flash('Estado do alarme atualizado!', 'success')
    else:
        flash('Erro ao atualizar estado do alarme.', 'danger')
    return redirect(url_for('alarms.alarms'))

@alarms_bp.route('/alarms/delete/<alarm_id>', methods=['POST'])
def delete_alarm(alarm_id):
    if 'access_token' not in session:
        return redirect(url_for('auth.login'))
    resp = api_delete(f'/alarms/{alarm_id}')
    if resp.status_code == 204:
        flash('Alarme excluído com sucesso!', 'success')
    else:
        flash('Erro ao excluir alarme.', 'danger')
    return redirect(url_for('alarms.alarms'))
