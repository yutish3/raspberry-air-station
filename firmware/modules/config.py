import threading
import os

# Global State Dictionary
# This is shared between Sensor Thread, Web Thread, and Display Thread
SYSTEM_STATE = {
    "pm1_0": 0.0,
    "pm2_5": 0.0,
    "pm4_0": 0.0,
    "pm10": 0.0,
    "voc_index": 0.0,
    "temperature": 0.0,
    "humidity": 0.0,
    "timestamp": None,
    "sensor_status": "Starting..."
}

# Lock for thread-safe access to SYSTEM_STATE
STATE_LOCK = threading.Lock()

# Configuration
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, 'data')
LOG_FILE = os.path.join(DATA_DIR, 'sensor_log.csv')
STATIC_DIR = os.path.join(BASE_DIR, 'static')
UPLOAD_FOLDER = os.path.join(STATIC_DIR, 'uploads')
ART_IMAGE_PATH = os.path.join(UPLOAD_FOLDER, 'art.png')

# Display Configuration
# 4.2 inch e-Paper resolution is 400x300
DISPLAY_WIDTH = 400
DISPLAY_HEIGHT = 300

# Create directories if they don't exist
os.makedirs(DATA_DIR, exist_ok=True)
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
