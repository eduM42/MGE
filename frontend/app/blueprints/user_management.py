from flask import Blueprint, render_template, redirect, url_for, session, flash, request
from app.utils.api import api_get, api_patch, api_delete, api_post
from app.helpers.navbarHelper import get_navbar_state

user_management_bp = Blueprint('user_management', __name__)

@user_management_bp.route('/user_management', methods=['GET'])
def user_management():
    if 'access_token' not in session:
        return redirect(url_for('auth.login'))
    user_resp = api_get('/auth/me')
    if user_resp.status_code != 200:
        flash('Não foi possível obter informações do usuário. Faça login novamente.', 'danger')
        session.pop('access_token', None)
        return redirect(url_for('auth.login'))
    user = user_resp.json()
    organizations = []
    if user['role'] == 'admin':
        users_resp = api_get('/users')
        users = users_resp.json() if users_resp.status_code == 200 else []
        orgs_resp = api_get('/organizations')
        organizations = orgs_resp.json() if orgs_resp.status_code == 200 else []
    elif user['role'] == 'org_owner':
        users_resp = api_get(f"/users/by_organization/{user['organization_id']}")
        users = users_resp.json() if users_resp.status_code == 200 else []
        # Only show their own org
        orgs_resp = api_get(f"/organizations/{user['organization_id']}")
        organizations = [orgs_resp.json()] if orgs_resp.status_code == 200 else []
    else:
        flash('Acesso não autorizado.', 'danger')
        return redirect(url_for('devices.devices'))
    navbar_state = get_navbar_state()
    return render_template('user_management.html', user=user, users=users, organizations=organizations, navbar_state=navbar_state, active_page='user_management')

@user_management_bp.route('/admin_user_management', methods=['GET'])
def admin_user_management():
    if 'access_token' not in session:
        return redirect(url_for('auth.login'))
    user_resp = api_get('/auth/me')
    if user_resp.status_code != 200:
        flash('Não foi possível obter informações do usuário. Faça login novamente.', 'danger')
        session.pop('access_token', None)
        return redirect(url_for('auth.login'))
    user = user_resp.json()
    if user['role'] != 'admin':
        flash('Acesso não autorizado.', 'danger')
        return redirect(url_for('devices.devices'))
    users_resp = api_get('/users')
    users = users_resp.json() if users_resp.status_code == 200 else []
    orgs_resp = api_get('/organizations')
    organizations = orgs_resp.json() if orgs_resp.status_code == 200 else []
    navbar_state = get_navbar_state()
    return render_template('admin_user_management.html', user=user, users=users, organizations=organizations, navbar_state=navbar_state, active_page='user_management')

@user_management_bp.route('/org_user_management', methods=['GET'])
def org_user_management():
    if 'access_token' not in session:
        return redirect(url_for('auth.login'))
    user_resp = api_get('/auth/me')
    if user_resp.status_code != 200:
        flash('Não foi possível obter informações do usuário. Faça login novamente.', 'danger')
        session.pop('access_token', None)
        return redirect(url_for('auth.login'))
    user = user_resp.json()
    if user['role'] != 'org_owner':
        flash('Acesso não autorizado.', 'danger')
        return redirect(url_for('devices.devices'))
    users_resp = api_get(f"/users/by_organization/{user['organization_id']}")
    users = users_resp.json() if users_resp.status_code == 200 else []
    orgs_resp = api_get('/organizations')
    organizations = orgs_resp.json() if orgs_resp.status_code == 200 else []
    navbar_state = get_navbar_state()
    return render_template('user_management.html', user=user, users=users, organizations=organizations, navbar_state=navbar_state, active_page='user_management')

@user_management_bp.route('/user_management/create', methods=['POST'])
def create_user():
    if 'access_token' not in session:
        return redirect(url_for('auth.login'))
    user_resp = api_get('/auth/me')
    if user_resp.status_code != 200:
        flash('Não foi possível obter informações do usuário. Faça login novamente.', 'danger')
        session.pop('access_token', None)
        return redirect(url_for('auth.login'))
    user = user_resp.json()
    if user['role'] not in ['admin', 'org_owner']:
        flash('Acesso não autorizado.', 'danger')
        return redirect(url_for('user_management.user_management'))
    org_id = request.form.get('organization_id')
    role = request.form.get('role')
    # Org owner can only create users for their own org
    if user['role'] == 'org_owner':
        org_id = user.get('organization_id')
    if role == 'org_owner' and not org_id:
        flash('Selecione uma organização para o Org Owner.', 'danger')
        return redirect(url_for('user_management.user_management'))
    data = {
        'name': request.form.get('name'),
        'username': request.form.get('username'),
        'email': request.form.get('email'),
        'password': request.form.get('password'),
        'role': role,
        'organization_id': org_id if org_id else None,
    }
    # DEBUG: Show what is being sent
    flash(f"DEBUG: Data to backend: {data}", 'info')
    resp = api_post('/users/register', json=data)
    flash(f"DEBUG: Backend status: {resp.status_code}, text: {resp.text}", 'info')
    if resp.status_code == 200:
        flash('Usuário criado com sucesso!', 'success')
    else:
        flash('Erro ao criar usuário.', 'danger')
    return redirect(url_for('user_management.user_management'))

@user_management_bp.route('/user_management/edit/<user_id>', methods=['POST'])
def edit_user(user_id):
    if 'access_token' not in session:
        return redirect(url_for('auth.login'))
    user_resp = api_get('/auth/me')
    if user_resp.status_code != 200:
        flash('Não foi possível obter informações do usuário. Faça login novamente.', 'danger')
        session.pop('access_token', None)
        return redirect(url_for('auth.login'))
    user = user_resp.json()
    if user['role'] not in ['admin', 'org_owner']:
        flash('Acesso não autorizado.', 'danger')
        return redirect(url_for('user_management.user_management'))
    org_id = request.form.get('organization_id')
    role = request.form.get('role')
    if role == 'org_owner' and not org_id:
        flash('Selecione uma organização para o Org Owner.', 'danger')
        return redirect(url_for('user_management.user_management'))
    data = {
        'name': request.form.get('name'),
        'email': request.form.get('email'),
        'role': role,
        'organization_id': org_id if org_id else None,
    }
    resp = api_patch(f'/users/{user_id}', json=data)
    if resp.status_code == 200:
        flash('Usuário atualizado com sucesso!', 'success')
    else:
        flash('Erro ao atualizar usuário.', 'danger')
    return redirect(url_for('user_management.user_management'))

@user_management_bp.route('/user_management/delete/<user_id>', methods=['POST'])
def delete_user(user_id):
    if 'access_token' not in session:
        return redirect(url_for('auth.login'))
    user_resp = api_get('/auth/me')
    if user_resp.status_code != 200:
        flash('Não foi possível obter informações do usuário. Faça login novamente.', 'danger')
        session.pop('access_token', None)
        return redirect(url_for('auth.login'))
    user = user_resp.json()
    if user['role'] not in ['admin', 'org_owner']:
        flash('Acesso não autorizado.', 'danger')
        return redirect(url_for('user_management.user_management'))
    resp = api_delete(f'/users/{user_id}')
    if resp.status_code == 204:
        flash('Usuário removido com sucesso!', 'success')
    else:
        flash('Erro ao remover usuário.', 'danger')
    return redirect(url_for('user_management.user_management'))
