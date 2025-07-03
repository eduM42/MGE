from flask import Flask
from app.blueprints.auth import auth_bp
from app.blueprints.devices import devices_bp
from app.blueprints.alarms import alarms_bp
from app.blueprints.user_management import user_management_bp
from app.blueprints.export import export_bp
from app.blueprints.organizations import organizations_bp
from app.blueprints.circuits import circuits_bp
from app.blueprints.sensors import sensors_bp

app = Flask(__name__)
app.secret_key = 'your-secret-key'  # Set a secure secret key

app.register_blueprint(auth_bp)
app.register_blueprint(devices_bp)
app.register_blueprint(alarms_bp)
app.register_blueprint(user_management_bp)
app.register_blueprint(export_bp)
app.register_blueprint(organizations_bp)
app.register_blueprint(circuits_bp)
app.register_blueprint(sensors_bp)
