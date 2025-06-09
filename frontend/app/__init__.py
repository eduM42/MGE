from flask import Flask
from app.blueprints.auth import auth_bp
from app.blueprints.devices import devices_bp
from app.blueprints.alarms import alarms_bp

app = Flask(__name__)
app.secret_key = 'your-secret-key'  # Set a secure secret key

app.register_blueprint(auth_bp)
app.register_blueprint(devices_bp)
app.register_blueprint(alarms_bp)
