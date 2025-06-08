from flask import Flask, render_template, redirect, url_for, session, flash, request
from app.blueprints.auth import auth_bp
from app.utils.api import api_get
from app.helpers.navbarHelper import get_navbar_state, update_navbar_state

app = Flask(__name__)
app.secret_key = 'your-secret-key'  # Set a secure secret key

app.register_blueprint(auth_bp)

@app.route('/update_navbar_state', methods=['POST'])
def update_navbar_state_route():
    return update_navbar_state()

@app.route('/')
def index():
    if 'access_token' not in session:
        return redirect(url_for('auth.login'))
    # Fetch user info
    user_resp = api_get('/auth/me')
    if user_resp.status_code != 200:
        flash('Não foi possível obter informações do usuário. Faça login novamente.', 'danger')
        session.pop('access_token', None)
        return redirect(url_for('auth.login'))
    user = user_resp.json()
    # Fetch devices
    devices_resp = api_get('/devices')
    if devices_resp.status_code != 200:
        flash('Não foi possível obter dispositivos.', 'danger')
        devices = []
    else:
        devices = devices_resp.json()
    # Fetch circuits
    circuits_resp = api_get('/circuits')
    circuits = circuits_resp.json() if circuits_resp.status_code == 200 else []
    # Fetch organizations
    orgs_resp = api_get('/organizations')
    organizations = orgs_resp.json() if orgs_resp.status_code == 200 else []
    navbar_state = get_navbar_state()
    return render_template('index.html', user=user, devices=devices, navbar_state=navbar_state, active_page='home', circuits=circuits, organizations=organizations)

@app.route('/register_device', methods=['POST'])
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
    # Remove empty values
    payload = {k: v for k, v in payload.items() if v}
    from app.utils.api import api_post
    resp = api_post('/devices', json=payload)
    if resp.status_code == 201:
        flash('Dispositivo registrado com sucesso!', 'success')
    else:
        flash('Erro ao registrar dispositivo.', 'danger')
    return redirect(url_for('index'))

@app.route('/devices')
def devices():
    if 'access_token' not in session:
        return redirect(url_for('auth.login'))
    user_resp = api_get('/auth/me')
    if user_resp.status_code != 200:
        flash('Não foi possível obter informações do usuário. Faça login novamente.', 'danger')
        session.pop('access_token', None)
        return redirect(url_for('auth.login'))
    user = user_resp.json()
    # Approved devices
    devices_resp = api_get('/devices')
    devices = devices_resp.json() if devices_resp.status_code == 200 else []
    # Pending devices
    pending_resp = api_get('/devices/pending')
    pending_devices = pending_resp.json() if pending_resp.status_code == 200 else []
    # Circuits and organizations for approval modal
    circuits_resp = api_get('/circuits')
    circuits = circuits_resp.json() if circuits_resp.status_code == 200 else []
    orgs_resp = api_get('/organizations')
    organizations = orgs_resp.json() if orgs_resp.status_code == 200 else []
    navbar_state = get_navbar_state()
    return render_template('device_overview.html', user=user, devices=devices, pending_devices=pending_devices, circuits=circuits, organizations=organizations, navbar_state=navbar_state, active_page='devices')

@app.route('/approve_device', methods=['POST'])
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
    from app.utils.api import api_post
    resp = api_post(f'/devices/{device_id}/approve', json=payload)
    if resp.status_code == 200:
        flash('Dispositivo aprovado com sucesso!', 'success')
    else:
        flash('Erro ao aprovar dispositivo.', 'danger')
    return redirect(url_for('devices'))

@app.route('/deny_device', methods=['POST'])
def deny_device():
    if 'access_token' not in session:
        return redirect(url_for('auth.login'))
    device_id = request.form.get('device_id')
    from app.utils.api import api_post
    resp = api_post(f'/devices/{device_id}/deny')
    if resp.status_code == 204:
        flash('Dispositivo negado e removido.', 'success')
    else:
        flash('Erro ao negar dispositivo.', 'danger')
    return redirect(url_for('devices'))

@app.route('/edit_device', methods=['POST'])
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
        'pending': False  # Always keep device approved when editing
    }
    # Remove empty values except 'pending'
    payload = {k: v for k, v in payload.items() if v is not None or k == 'pending'}
    from app.utils.api import api_put
    resp = api_put(f'/devices/{device_id}', json=payload)
    if resp.status_code == 200:
        flash('Dispositivo atualizado com sucesso!', 'success')
    else:
        flash('Erro ao atualizar dispositivo.', 'danger')
    return redirect(url_for('devices'))

@app.route('/delete_device', methods=['POST'])
def delete_device():
    if 'access_token' not in session:
        return redirect(url_for('auth.login'))
    device_id = request.form.get('device_id')
    from app.utils.api import api_delete
    resp = api_delete(f'/devices/{device_id}')
    if resp.status_code == 204:
        flash('Dispositivo apagado com sucesso!', 'success')
    else:
        flash('Erro ao apagar dispositivo.', 'danger')
    return redirect(url_for('devices'))

@app.route('/user_profile', methods=['GET'])
def user_profile():
    if 'access_token' not in session:
        return redirect(url_for('auth.login'))
    user_resp = api_get('/auth/me')
    if user_resp.status_code != 200:
        flash('Não foi possível obter informações do usuário. Faça login novamente.', 'danger')
        session.pop('access_token', None)
        return redirect(url_for('auth.login'))
    user = user_resp.json()
    navbar_state = get_navbar_state()
    return render_template('user_profile.html', user=user, navbar_state=navbar_state, active_page='user_profile')
