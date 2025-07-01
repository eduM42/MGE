from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from app.utils.api import api_get, api_post, api_put, api_delete
from app.helpers.navbarHelper import get_navbar_state

organizations_bp = Blueprint('organizations', __name__)

@organizations_bp.route('/organizations', methods=['GET'])
def organizations():
    if 'access_token' not in session:
        return redirect(url_for('auth.login'))
    user_resp = api_get('/auth/me')
    if user_resp.status_code != 200:
        return redirect(url_for('auth.login'))
    user = user_resp.json()
    if user.get('role') != 'admin':
        flash('Acesso negado.', 'danger')
        return redirect(url_for('devices.index'))
    orgs_resp = api_get('/organizations')
    organizations = orgs_resp.json() if orgs_resp.status_code == 200 else []
    navbar_state = get_navbar_state()
    return render_template('organizations.html', user=user, organizations=organizations, navbar_state=navbar_state, active_page='organizations')

@organizations_bp.route('/organizations/create', methods=['POST'])
def create_organization():
    if 'access_token' not in session:
        return redirect(url_for('auth.login'))
    name = request.form.get('name')
    description = request.form.get('description')
    resp = api_post('/organizations', json={'name': name, 'description': description})
    if resp.status_code == 201:
        flash('Organização criada com sucesso!', 'success')
    else:
        flash('Erro ao criar organização.', 'danger')
    return redirect(url_for('organizations.organizations'))

@organizations_bp.route('/organizations/edit/<org_id>', methods=['POST'])
def edit_organization(org_id):
    if 'access_token' not in session:
        return redirect(url_for('auth.login'))
    name = request.form.get('name')
    description = request.form.get('description')
    resp = api_put(f'/organizations/{org_id}', json={'name': name, 'description': description})
    if resp.status_code == 200:
        flash('Organização atualizada com sucesso!', 'success')
    else:
        flash('Erro ao atualizar organização.', 'danger')
    return redirect(url_for('organizations.organizations'))

@organizations_bp.route('/organizations/delete/<org_id>', methods=['POST'])
def delete_organization(org_id):
    if 'access_token' not in session:
        return redirect(url_for('auth.login'))
    resp = api_delete(f'/organizations/{org_id}')
    if resp.status_code == 204:
        flash('Organização removida com sucesso!', 'success')
    else:
        flash('Erro ao remover organização.', 'danger')
    return redirect(url_for('organizations.organizations'))
