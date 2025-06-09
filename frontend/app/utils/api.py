import requests
from flask import session

BACKEND_URL = "http://backend:8050"  # Use 'http://localhost:8050' for local dev if needed

def get_token():
    return session.get('access_token')

def get_headers():
    token = get_token()
    if token:
        return {'Authorization': f'Bearer {token}'}
    return {}

def api_post(path, data=None, json=None):
    url = f"{BACKEND_URL}{path}"
    headers = get_headers()
    return requests.post(url, data=data, json=json, headers=headers)

def api_get(path, params=None):
    url = f"{BACKEND_URL}{path}"
    headers = get_headers()
    return requests.get(url, params=params, headers=headers)

def api_put(path, data=None, json=None):
    url = f"{BACKEND_URL}{path}"
    headers = get_headers()
    return requests.put(url, data=data, json=json, headers=headers)

def api_delete(path):
    url = f"{BACKEND_URL}{path}"
    headers = get_headers()
    return requests.delete(url, headers=headers)

def api_patch(path, data=None, json=None):
    url = f"{BACKEND_URL}{path}"
    headers = get_headers()
    return requests.patch(url, data=data, json=json, headers=headers)
