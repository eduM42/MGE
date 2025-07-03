from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from app.utils import api

sensors_bp = Blueprint('sensors', __name__)

@sensors_bp.route('/sensors', methods=['GET', 'POST'])
def manage_sensors():
    token = session.get('access_token')
    if not token:
        return redirect(url_for('auth.login'))
    user_resp = api.api_get('/auth/me')
    if not user_resp.ok:
        flash('Sessão expirada. Faça login novamente.', 'danger')
        return redirect(url_for('auth.login'))
    user = user_resp.json()
    if request.method == 'POST' and request.form.get('delete_sensor_id'):
        sensor_id = request.form.get('delete_sensor_id')
        if api.delete_sensor(sensor_id):
            flash('Sensor excluído com sucesso.', 'success')
        else:
            flash('Erro ao excluir o sensor.', 'danger')
        return redirect(url_for('sensors.manage_sensors'))
    devices = api.get_user_devices(user['id'])
    sensors = api.get_user_sensors(user['id'])
    if request.method == 'POST':
        device_id = request.form.get('device_id')
        sensor_type = request.form.get('type')
        phase = request.form.get('phase')
        if not device_id or not sensor_type or not phase:
            flash('Todos os campos são obrigatórios.', 'danger')
        else:
            result = api.add_sensor(device_id, sensor_type, phase)
            if result.get('success'):
                flash('Sensor adicionado com sucesso.', 'success')
                return redirect(url_for('sensors.manage_sensors'))
            else:
                flash(result.get('error', 'Falha ao adicionar sensor.'), 'danger')
    return render_template('sensors.html', user=user, devices=devices, sensors=sensors, active_page='sensors')
