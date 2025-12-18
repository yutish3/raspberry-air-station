from flask import Flask, render_template, request, jsonify, redirect, url_for
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
import os
import secrets
from modules.config import SYSTEM_STATE, STATE_LOCK, UPLOAD_FOLDER, ART_IMAGE_PATH
from modules.sensor_manager import SensorManager
from modules.display_manager import DisplayManager

app = Flask(__name__)
app.secret_key = secrets.token_hex(16)

# Login Setup
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

# Simple User Model
class User(UserMixin):
    def __init__(self, id):
        self.id = id

@login_manager.user_loader
def load_user(user_id):
    if user_id == 'admin':
        return User(user_id)
    return None

# --- Routes ---

@app.route('/')
def index():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        # Hardcoded credentials for simplicity as requested
        # In production, use hashed passwords
        if username == 'admin' and password == 'admin':
            login_user(User(username))
            return redirect(url_for('dashboard'))
        else:
            return render_template('login.html', error="Invalid Credentials")
    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

@app.route('/dashboard')
@login_required
def dashboard():
    return render_template('dashboard.html')

@app.route('/api/data')
@login_required
def api_data():
    """Returns the current sensor state as JSON."""
    with STATE_LOCK:
        return jsonify(SYSTEM_STATE)

@app.route('/upload', methods=['POST'])
@login_required
def upload_file():
    if 'file' not in request.files:
        return redirect(request.url)
    file = request.files['file']
    if file.filename == '':
        return redirect(request.url)
    if file:
        # Save file as art.png, replacing the old one
        # Basic validation could be added here
        try:
            file.save(ART_IMAGE_PATH)
            return redirect(url_for('dashboard'))
        except Exception as e:
            return f"Error saving file: {e}", 500
    return redirect(url_for('dashboard'))

# --- Main Entry Point ---

if __name__ == '__main__':
    # 1. Start Sensor Thread
    sensor_thread = SensorManager()
    sensor_thread.start()

    # 2. Start Display Thread
    display_thread = DisplayManager()
    display_thread.start()

    try:
        # 3. Start Web Server
        # host='0.0.0.0' allows access from other devices on the network
        app.run(host='0.0.0.0', port=5000, debug=False, use_reloader=False)
    except KeyboardInterrupt:
        print("Stopping threads...")
    finally:
        sensor_thread.stop()
        display_thread.stop()
        sensor_thread.join()
        display_thread.join()
        print("System Shutdown Complete.")
