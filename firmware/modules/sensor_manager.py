import time
import csv
import os
import threading
from datetime import datetime
try:
    from sensirion_i2c_driver import I2cConnection, LinuxI2cTransceiver
    from sensirion_i2c_sen5x import Sen5xI2cDevice
    HAS_SENSOR_LIB = True
except (ImportError, OSError):
    print("Sensor Manager: Hardware libraries not found or incompatible (Windows?). using Mock Mode.")
    HAS_SENSOR_LIB = False
    import random

from modules.config import SYSTEM_STATE, STATE_LOCK, LOG_FILE

class SensorManager(threading.Thread):
    def __init__(self):
        super().__init__()
        self.daemon = True  # kills thread when main program exits
        self.running = True
        self.i2c_transceiver = None
        self.sen54 = None
        
        # Initialize CSV
        self._init_csv()

    def _init_csv(self):
        """Creates CSV file with headers if it doesn't exist."""
        if not os.path.exists(LOG_FILE):
            with open(LOG_FILE, 'w', newline='') as f:
                writer = csv.writer(f)
                writer.writerow(["Timestamp", "PM1.0", "PM2.5", "PM4.0", "PM10", "VOC", "Temp", "Humidity"])

    def _connect_sensor(self):
        """Attempts to connect to the SEN54 sensor."""
        if not HAS_SENSOR_LIB:
            return False
            
        try:
            # On Raspberry Pi 4, the default I2C bus is usually 1
            self.i2c_transceiver = LinuxI2cTransceiver('/dev/i2c-1')
            self.sen54 = Sen5xI2cDevice(I2cConnection(self.i2c_transceiver))
            self.sen54.start_measurement()
            print("Sensor Manager: Connected to SEN54.")
            return True
        except Exception as e:
            print(f"Sensor Manager: Connection failed - {e}")
            with STATE_LOCK:
                SYSTEM_STATE["sensor_status"] = "Disconnected"
            return False

    def run(self):
        print("Sensor Manager: Thread Started")
        
        while self.running:
            if HAS_SENSOR_LIB:
                if self.sen54 is None:
                    if not self._connect_sensor():
                        time.sleep(5) 
                        self._update_mock_data() # Use mock data if connection fails
                        continue

                try:
                    # Read Data
                    data = self.sen54.read_measured_values()
                    
                    pm1_0 = data.mass_concentration_1p0.physical
                    pm2_5 = data.mass_concentration_2p5.physical
                    pm4_0 = data.mass_concentration_4p0.physical
                    pm10 = data.mass_concentration_10p0.physical
                    voc = data.voc_index.scaled
                    temp = data.ambient_temperature.degrees_celsius
                    hum = data.ambient_humidity.percent_rh
                    
                    self._update_state(pm1_0, pm2_5, pm4_0, pm10, voc, temp, hum, "Active")

                except Exception as e:
                    print(f"Sensor Manager: Read Error - {e}")
                    with STATE_LOCK:
                        SYSTEM_STATE["sensor_status"] = "Error"
                    
                    try:
                        self.i2c_transceiver.close()
                    except:
                        pass
                    self.sen54 = None
            else:
                self._update_mock_data()

            # Wait 2 seconds
            time.sleep(2)

    def _update_mock_data(self):
        """Generates fake data for testing."""
        pm1_0 = random.uniform(0, 10)
        pm2_5 = random.uniform(5, 35)
        pm4_0 = random.uniform(5, 40)
        pm10 = random.uniform(10, 50)
        voc = random.randint(50, 150)
        temp = random.uniform(20, 30)
        hum = random.uniform(40, 60)
        self._update_state(pm1_0, pm2_5, pm4_0, pm10, voc, temp, hum, "Simulated")

    def _update_state(self, pm1_0, pm2_5, pm4_0, pm10, voc, temp, hum, status):
        now = datetime.now()
        timestamp_str = now.strftime("%Y-%m-%d %H:%M:%S")

        with STATE_LOCK:
            SYSTEM_STATE["pm1_0"] = round(pm1_0, 1)
            SYSTEM_STATE["pm2_5"] = round(pm2_5, 1)
            SYSTEM_STATE["pm4_0"] = round(pm4_0, 1)
            SYSTEM_STATE["pm10"] = round(pm10, 1)
            SYSTEM_STATE["voc_index"] = round(voc, 0)
            SYSTEM_STATE["temperature"] = round(temp, 1)
            SYSTEM_STATE["humidity"] = round(hum, 1)
            SYSTEM_STATE["timestamp"] = timestamp_str
            SYSTEM_STATE["sensor_status"] = status

        # Log to CSV
        with open(LOG_FILE, 'a', newline='') as f:
            writer = csv.writer(f)
            writer.writerow([
                timestamp_str, 
                SYSTEM_STATE["pm1_0"], 
                SYSTEM_STATE["pm2_5"], 
                SYSTEM_STATE["pm4_0"], 
                SYSTEM_STATE["pm10"], 
                SYSTEM_STATE["voc_index"], 
                SYSTEM_STATE["temperature"], 
                SYSTEM_STATE["humidity"]
            ])

    def stop(self):
        self.running = False
