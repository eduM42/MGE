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
            return redirect(url_for('index'))
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
