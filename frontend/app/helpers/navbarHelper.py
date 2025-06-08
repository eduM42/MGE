from flask import request, jsonify, session

def update_navbar_state():
    data = request.json
    is_expanded = data.get('isExpanded')
    session['navbar_expanded'] = is_expanded
    return jsonify({'success': True, 'navbarExpanded': is_expanded})

def get_navbar_state():
    return 'expand' if session.get('navbar_expanded', False) else ''