This directory (`drivers/`) is where you must place the specific driver files for your E-Ink display.

Because there are many generic "3.7 inch E-Ink" displays (most likely Waveshare), I cannot include the proprietary driver code directly.

**INSTRUCTIONS:**

1.  Identify your display model (Waveshare 4.2-inch e-Paper Module).
2.  Go to the official Wiki or GitHub repository for your display.
    *   Example: `https://github.com/waveshare/e-Paper/tree/master/RaspberryPi_JetsonNano/python/lib`
3.  Download the following files and place them in this folder:
    *   `epdconfig.py` (Handles SPI communication)
    *   `epd4in2.py` (The specific driver for your screen size)
4.  **Rename** the specific driver file (e.g., `epd4in2.py`) to **`epd_driver.py`**.
    *   *Alternative:* If you don't want to rename it, edit `modules/display_manager.py` line 14 to import your specific file:
        `import epd4in2 as epd` instead of `import epd_driver as epd`.

**Why is this necessary?**
These files contain the low-level SPI commands specific to the screen's controller chip. Without them, the Python code cannot talk to the display.

**Testing:**
If these files are missing, the system will print: 
`WARNING: E-Ink Driver not found in 'drivers/'. run mode only.`
and write debug images to the `static/uploads/` folder instead of updating a screen.
