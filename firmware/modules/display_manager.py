import time
import os
import threading
from PIL import Image, ImageDraw, ImageFont
try:
    from gpiozero import Button
    HAS_GPIO = True
except (ImportError, OSError):
    HAS_GPIO = False
from modules.config import SYSTEM_STATE, STATE_LOCK, ART_IMAGE_PATH, DISPLAY_WIDTH, DISPLAY_HEIGHT

# Attempt to import specific driver or mock it
try:
    # IMPORTANT: User must place their specific driver in drivers/
    # For example, if using Waveshare 3.7inch, you might have 'epd3in7.py'
    # We will try a generic import approach assuming 'epd_driver.py' wraps the real driver
    import sys
    sys.path.append(os.path.join(os.path.dirname(os.path.dirname(__file__)), 'drivers'))
    import epd_driver as epd
    HAS_EPD = True
except ImportError:
    print("WARNING: E-Ink Driver not found in 'drivers/'. run mode only.")
    HAS_EPD = False

# Font Paths - using default system fonts or providing a simple fallback
try:
    FONT_LARGE = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 32)
    FONT_MEDIUM = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 20)
    FONT_SMALL = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 14)
except IOError:
    # Use default PIL font if DejaVu not found (mostly for dev/test on non-Pi)
    FONT_LARGE = ImageFont.load_default()
    FONT_MEDIUM = ImageFont.load_default()
    FONT_SMALL = ImageFont.load_default()

class DisplayManager(threading.Thread):
    def __init__(self):
        super().__init__()
        self.daemon = True
        self.running = True
        
        # State Machine
        self.MODE_DATA = 0
        self.MODE_PHOTO = 1
        self.current_mode = self.MODE_DATA
        self.needs_refresh = True
        self.last_data_hash = None
        
        # Hardware Setup
        self.touch_pin = 4
        self.btn = None
        if HAS_GPIO:
            try:
                self.btn = Button(self.touch_pin)
                self.btn.when_pressed = self._toggle_mode
            except Exception as e:
                print(f"Display Manager: GPIO setup failed (Simulating?) - {e}")
        else:
            print("Display Manager: GPIO module missing. Touch input disabled (Simulated).")

        # Display Setup
        if HAS_EPD:
            try:
                self.epd = epd.EPD()
                self.epd.init()
                self.epd.Clear()
            except Exception as e:
                print(f"Display Manager: EPD init failed - {e}")
                self.epd = None
        else:
            self.epd = None

    def _toggle_mode(self):
        """Switch between Data and Photo mode."""
        if self.current_mode == self.MODE_DATA:
            self.current_mode = self.MODE_PHOTO
            print("Display Manager: Switched to Photo Mode")
        else:
            self.current_mode = self.MODE_DATA
            print("Display Manager: Switched to Data Mode")
        self.needs_refresh = True

    def _create_data_image(self, state):
        """Generates the UI image for sensor data."""
        # Create blank white image
        image = Image.new('1', (DISPLAY_WIDTH, DISPLAY_HEIGHT), 255)  # '1' for 1-bit bitmap
        draw = ImageDraw.Draw(image)
        
        # Draw Header
        draw.rectangle((0, 0, DISPLAY_WIDTH, 40), fill=0) # Black bar
        draw.text((10, 10), "AeroInk Station", font=FONT_MEDIUM, fill=255) # White text
        draw.text((DISPLAY_WIDTH - 150, 12), state['timestamp'] or "--:--", font=FONT_SMALL, fill=255)

        # Draw Sensor Data Grid
        # PM2.5 (Main Focus)
        draw.text((20, 60), "PM2.5", font=FONT_MEDIUM, fill=0)
        draw.text((20, 90), f"{state['pm2_5']}", font=FONT_LARGE, fill=0)
        draw.text((120, 105), "ug/m3", font=FONT_SMALL, fill=0)

        # VOC / Humidity / Temp
        draw.text((200, 60), "VOC Index", font=FONT_MEDIUM, fill=0)
        draw.text((200, 90), f"{state['voc_index']}", font=FONT_LARGE, fill=0)

        draw.text((20, 160), f"Temp: {state['temperature']} C", font=FONT_MEDIUM, fill=0)
        draw.text((200, 160), f"Humidity: {state['humidity']} %", font=FONT_MEDIUM, fill=0)
        
        # Status Bar
        draw.line((0, 240, DISPLAY_WIDTH, 240), fill=0)
        draw.text((10, 250), f"Status: {state['sensor_status']}", font=FONT_SMALL, fill=0)

        return image

    def _create_photo_image(self):
        """Loads and prepares the art image."""
        if os.path.exists(ART_IMAGE_PATH):
            try:
                img = Image.open(ART_IMAGE_PATH)
                # Resize and convert to 1-bit
                img = img.resize((DISPLAY_WIDTH, DISPLAY_HEIGHT), Image.Resampling.LANCZOS)
                img = img.convert('1')
                return img
            except Exception as e:
                print(f"Error loading art: {e}")
        
        # Fallback if no image found
        image = Image.new('1', (DISPLAY_WIDTH, DISPLAY_HEIGHT), 255)
        draw = ImageDraw.Draw(image)
        draw.text((50, 120), "No Image Uploaded", font=FONT_LARGE, fill=0)
        return image

    def run(self):
        print("Display Manager: Thread Started")
        
        while self.running:
            # Check for generic refresh triggers
            
            with STATE_LOCK:
                # Copy state to avoid holding lock during drawing
                current_state = SYSTEM_STATE.copy()

            # Data Hashing to detect significant changes
            # (Simple concatenation of values for check)
            data_hash = f"{current_state['pm2_5']}-{current_state['voc_index']}-{current_state['temperature']}-{self.current_mode}"
            
            if data_hash != self.last_data_hash:
                self.needs_refresh = True
                self.last_data_hash = data_hash

            if self.needs_refresh:
                print("Display Manager: Refreshing Screen...")
                
                if self.current_mode == self.MODE_DATA:
                    canvas = self._create_data_image(current_state)
                else:
                    canvas = self._create_photo_image()
                
                if self.epd:
                    try:
                        # Depending on driver, this might buffer then display
                        self.epd.display(self.epd.getbuffer(canvas))
                        # Some EPDs require sleep to prevent burn-in
                        # self.epd.sleep() 
                        # If we sleep, we need to init again next loop.
                        # For continuous updates, we might keep it awake or handle partial updates.
                        # Assuming full update for now.
                    except Exception as e:
                        print(f"Display Manager: Driver Error - {e}")
                else:
                    # Debug mode: Save image to check output
                    canvas.save(os.path.join(os.path.dirname(ART_IMAGE_PATH), "debug_display_out.png"))

                self.needs_refresh = False
            
            time.sleep(1) # Check loop delay

    def stop(self):
        self.running = False
        if self.epd:
            try:
                self.epd.sleep()
                epd.epdconfig.module_exit()
            except:
                pass
