from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from app.utils.api import api_get, api_post, api_put, api_delete
from app.helpers.navbarHelper import get_navbar_state

circuits_bp = Blueprint('circuits', __name__)

@circuits_bp.route('/circuits', methods=['GET'])
def circuits():
    if 'access_token' not in session:
        return redirect(url_for('auth.login'))
    user_resp = api_get('/auth/me')
    if user_resp.status_code != 200:
        return redirect(url_for('auth.login'))
    user = user_resp.json()
    circuits_resp = api_get('/circuits')
    circuits = circuits_resp.json() if circuits_resp.status_code == 200 else []
    navbar_state = get_navbar_state()
    return render_template('circuits.html', user=user, circuits=circuits, navbar_state=navbar_state, active_page='circuits')

@circuits_bp.route('/circuits/create', methods=['POST'])
def create_circuit():
    if 'access_token' not in session:
        return redirect(url_for('auth.login'))
    name = request.form.get('name')
    resp = api_post('/circuits', json={'name': name})
    if resp.status_code == 201:
        flash('Circuito criado com sucesso!', 'success')
    else:
        flash('Erro ao criar circuito.', 'danger')
    return redirect(url_for('circuits.circuits'))

@circuits_bp.route('/circuits/edit/<circuit_id>', methods=['POST'])
def edit_circuit(circuit_id):
    if 'access_token' not in session:
        return redirect(url_for('auth.login'))
    name = request.form.get('name')
    resp = api_put(f'/circuits/{circuit_id}', json={'name': name})
    if resp.status_code == 200:
        flash('Circuito atualizado com sucesso!', 'success')
    else:
        flash('Erro ao atualizar circuito.', 'danger')
    return redirect(url_for('circuits.circuits'))

@circuits_bp.route('/circuits/delete/<circuit_id>', methods=['POST'])
def delete_circuit(circuit_id):
    if 'access_token' not in session:
        return redirect(url_for('auth.login'))
    resp = api_delete(f'/circuits/{circuit_id}')
    if resp.status_code == 204:
        flash('Circuito removido com sucesso!', 'success')
    else:
        flash('Erro ao remover circuito.', 'danger')
    return redirect(url_for('circuits.circuits'))
