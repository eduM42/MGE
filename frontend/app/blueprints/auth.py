from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from app.utils.api import api_post

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        resp = api_post('/auth/token', data={'username': username, 'password': password})
        if resp.status_code == 200:
            token = resp.json()['access_token']
            session['access_token'] = token
            return redirect(url_for('devices.index'))
        else:
            flash('Usuário ou senha inválidos', 'danger')
    return render_template('login.html')

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        password = request.form['password']
        confirm_password = request.form['confirm_password']
        if password != confirm_password:
            flash('As senhas não coincidem.', 'danger')
            return render_template('register.html')
        data = {
            "name": request.form['name'],
            "username": request.form['username'],
            "email": request.form['email'],
            "password": password
        }
        resp = api_post('/users/register', json=data)
        if resp.status_code == 200:
            flash('Usuário criado com sucesso, por favor, faça login!', 'success')
            return redirect(url_for('auth.login'))
        else:
            flash('Erro ao registrar usuário', 'danger')
    return render_template('register.html')

@auth_bp.route('/logout')
def logout():
    session.pop('access_token', None)
    return redirect(url_for('auth.login'))

@auth_bp.route('/user_profile', methods=['GET', 'POST'])
def user_profile():
    from app.utils.api import api_get, api_patch, api_post
    from app.helpers.navbarHelper import get_navbar_state
    if 'access_token' not in session:
        return redirect(url_for('auth.login'))
    user_resp = api_get('/auth/me')
    if user_resp.status_code != 200:
        flash('Não foi possível obter informações do usuário. Faça login novamente.', 'danger')
        session.pop('access_token', None)
        return redirect(url_for('auth.login'))
    user = user_resp.json()
    if request.method == 'POST':
        action = request.form.get('action')
        if action == 'update_profile':
            data = {
                'name': request.form.get('full_name'),
                'phone': request.form.get('phone'),
                'address': request.form.get('address'),
                'is_residential': request.form.get('is_residential') == 'on',
            }
            resp = api_patch('/auth/me', json=data)
            if resp.status_code == 200:
                flash('Perfil atualizado com sucesso!', 'success')
                user = resp.json()
            else:
                flash('Erro ao atualizar perfil.', 'danger')
        elif action == 'change_password':
            current_password = request.form.get('current_password')
            new_password = request.form.get('new_password')
            repeat_new_password = request.form.get('repeat_new_password')
            if new_password != repeat_new_password:
                flash('As novas senhas não coincidem.', 'danger')
            else:
                resp = api_post('/auth/me/change_password', json={
                    'current_password': current_password,
                    'new_password': new_password
                })
                if resp.status_code == 200:
                    flash('Senha alterada com sucesso!', 'success')
                else:
                    flash('Erro ao alterar senha: ' + resp.text, 'danger')
    navbar_state = get_navbar_state()
    return render_template('user_profile.html', user=user, navbar_state=navbar_state, active_page='user_profile')
