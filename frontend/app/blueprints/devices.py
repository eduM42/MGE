from flask import Blueprint, render_template, redirect, url_for, session, flash, request
from app.utils.api import api_get, api_post, api_put, api_delete
from app.helpers.navbarHelper import get_navbar_state

devices_bp = Blueprint('devices', __name__)

def build_circuit_map(circuits):
    """Build a mapping from circuit_id to circuit name."""
    return {c['id']: c['name'] for c in circuits}

@devices_bp.route('/')
def index():
    if 'access_token' not in session:
        return redirect(url_for('auth.login'))
    user_resp = api_get('/auth/me')
    if user_resp.status_code != 200:
        flash('Não foi possível obter informações do usuário. Faça login novamente.', 'danger')
        session.pop('access_token', None)
        return redirect(url_for('auth.login'))
    user = user_resp.json()
    devices_resp = api_get('/devices')
    if devices_resp.status_code != 200:
        flash('Não foi possível obter dispositivos.', 'danger')
        devices = []
    else:
        devices = devices_resp.json()
    circuits_resp = api_get('/circuits')
    circuits = circuits_resp.json() if circuits_resp.status_code == 200 else []
    orgs_resp = api_get('/organizations')
    organizations = orgs_resp.json() if orgs_resp.status_code == 200 else []
    triggered_alarms_resp = api_get('/triggered_alarms')
    triggered_alarms = triggered_alarms_resp.json() if triggered_alarms_resp.status_code == 200 else []
    circuit_map = build_circuit_map(circuits)
    navbar_state = get_navbar_state()
    return render_template('index.html', user=user, devices=devices, navbar_state=navbar_state, active_page='home', circuits=circuits, organizations=organizations, circuit_map=circuit_map, triggered_alarms=triggered_alarms)

@devices_bp.route('/register_device', methods=['POST'])
def register_device():
    if 'access_token' not in session:
        return redirect(url_for('auth.login'))
    pretty_name = request.form.get('pretty_name')
    circuit_id = request.form.get('circuit_id') or None
    organization_id = request.form.get('organization_id') or None
    payload = {
        'pretty_name': pretty_name,
        'circuit_id': circuit_id if circuit_id else None,
        'organization_id': organization_id if organization_id else None
    }
    payload = {k: v for k, v in payload.items() if v}
    resp = api_post('/devices', json=payload)
    if resp.status_code == 201:
        flash('Dispositivo registrado com sucesso!', 'success')
    else:
        flash('Erro ao registrar dispositivo.', 'danger')
    return redirect(url_for('devices.index'))

@devices_bp.route('/devices')
def devices():
    if 'access_token' not in session:
        return redirect(url_for('auth.login'))
    user_resp = api_get('/auth/me')
    if user_resp.status_code != 200:
        flash('Não foi possível obter informações do usuário. Faça login novamente.', 'danger')
        session.pop('access_token', None)
        return redirect(url_for('auth.login'))
    user = user_resp.json()
    devices_resp = api_get('/devices')
    devices = devices_resp.json() if devices_resp.status_code == 200 else []
    pending_resp = api_get('/devices/pending')
    pending_devices = pending_resp.json() if pending_resp.status_code == 200 else []
    circuits_resp = api_get('/circuits')
    circuits = circuits_resp.json() if circuits_resp.status_code == 200 else []
    orgs_resp = api_get('/organizations')
    organizations = orgs_resp.json() if orgs_resp.status_code == 200 else []
    circuit_map = build_circuit_map(circuits)
    navbar_state = get_navbar_state()
    return render_template('device_overview.html', user=user, devices=devices, pending_devices=pending_devices, circuits=circuits, organizations=organizations, navbar_state=navbar_state, active_page='devices', circuit_map=circuit_map)

@devices_bp.route('/approve_device', methods=['POST'])
def approve_device():
    if 'access_token' not in session:
        return redirect(url_for('auth.login'))
    device_id = request.form.get('device_id')
    circuit_id = request.form.get('circuit_id') or None
    organization_id = request.form.get('organization_id') or None
    payload = {}
    if circuit_id:
        payload['circuit_id'] = circuit_id
    if organization_id:
        payload['organization_id'] = organization_id
    resp = api_post(f'/devices/{device_id}/approve', json=payload)
    if resp.status_code == 200:
        flash('Dispositivo aprovado com sucesso!', 'success')
    else:
        flash('Erro ao aprovar dispositivo.', 'danger')
    return redirect(url_for('devices.index'))

@devices_bp.route('/deny_device', methods=['POST'])
def deny_device():
    if 'access_token' not in session:
        return redirect(url_for('auth.login'))
    device_id = request.form.get('device_id')
    resp = api_post(f'/devices/{device_id}/deny')
    if resp.status_code == 204:
        flash('Dispositivo negado e removido.', 'success')
    else:
        flash('Erro ao negar dispositivo.', 'danger')
    return redirect(url_for('devices.index'))

@devices_bp.route('/edit_device', methods=['POST'])
def edit_device():
    if 'access_token' not in session:
        return redirect(url_for('auth.login'))
    device_id = request.form.get('device_id')
    pretty_name = request.form.get('pretty_name')
    circuit_id = request.form.get('circuit_id') or None
    organization_id = request.form.get('organization_id') or None
    payload = {
        'pretty_name': pretty_name,
        'circuit_id': circuit_id if circuit_id else None,
        'organization_id': organization_id if organization_id else None,
        'pending': False
    }
    payload = {k: v for k, v in payload.items() if v is not None or k == 'pending'}
    resp = api_put(f'/devices/{device_id}', json=payload)
    if resp.status_code == 200:
        flash('Dispositivo atualizado com sucesso!', 'success')
    else:
        flash('Erro ao atualizar dispositivo.', 'danger')
    return redirect(url_for('devices.index'))

@devices_bp.route('/delete_device', methods=['POST'])
def delete_device():
    if 'access_token' not in session:
        return redirect(url_for('auth.login'))
    device_id = request.form.get('device_id')
    resp = api_delete(f'/devices/{device_id}')
    if resp.status_code == 204:
        flash('Dispositivo apagado com sucesso!', 'success')
    else:
        flash('Erro ao apagar dispositivo.', 'danger')
    return redirect(url_for('devices.index'))

@devices_bp.route('/device/<device_id>')
def device_details(device_id):
    if 'access_token' not in session:
        return redirect(url_for('auth.login'))
    user_resp = api_get('/auth/me')
    if user_resp.status_code != 200:
        flash('Não foi possível obter informações do usuário. Faça login novamente.', 'danger')
        session.pop('access_token', None)
        return redirect(url_for('auth.login'))
    user = user_resp.json()
    device_resp = api_get(f'/devices/{device_id}')
    if device_resp.status_code != 200:
        flash('Dispositivo não encontrado.', 'danger')
        return redirect(url_for('devices.index'))
    device = device_resp.json()
    circuits_resp = api_get('/circuits')
    circuits = circuits_resp.json() if circuits_resp.status_code == 200 else []
    circuit_map = build_circuit_map(circuits)
    navbar_state = get_navbar_state()
    return render_template('device_details.html', user=user, device=device, circuits=circuits, circuit_map=circuit_map, navbar_state=navbar_state, active_page='devices')

@devices_bp.route('/system_statistics')
def system_statistics():
    if 'access_token' not in session:
        return redirect(url_for('auth.login'))
    user_resp = api_get('/auth/me')
    if user_resp.status_code != 200:
        flash('Não foi possível obter informações do usuário. Faça login novamente.', 'danger')
        session.pop('access_token', None)
        return redirect(url_for('auth.login'))
    user = user_resp.json()
    stats_resp = api_get('/devices/system_stats')
    stats = stats_resp.json() if stats_resp.status_code == 200 else {}
    navbar_state = get_navbar_state()
    return render_template('system_statistics.html', user=user, navbar_state=navbar_state, active_page='system_statistics',
                           system_info=stats.get('system_info', {}),
                           database_tables=stats.get('database_tables', []),
                           processes=stats.get('processes', []))
