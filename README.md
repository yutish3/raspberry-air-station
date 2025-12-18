# raspberry-air-station
this is a small project. how it overall works is raspberry pie takes data from sen 54 sensor and displayes it on e ink display and on a password protected website

deeper explanation :- it runs on a raspberry pi 4 and it uses sen 54 to get the info like (PM1.0, PM2.5, PM4.0, PM10, VOC Index, Temperature, Humidity) and display it on the e ink display which updates every 10 second and in background it is also hosting a website so you can change image on the aqi sensor like black and white art from phone and can also access the aqi data from website and the website is password protected. there is also an physical touch sensor using which you can switch between what to show on e ink display photo or the data 

i decided to make this project so i can have it as my personal home air station as i live in delhi (avg 300+ aqi) i will prob use it a lot to check the aqi and it can give an overall glimps of if i should leave the state for now or not 

# BOM
1. Sensirion SEN54 - 1 - Air Quality Sensor
2. Raspberry Pi 4 Model B (4GB RAM) - 1 - main controller
3. Waveshare 4.2-inch e-Paper Module (SPI) - 1 - display (400x300)
4. SmartElex Logic Level Converter (Bi-Directional) - 1 - 4 channel bi direction converter (3.3v - 5v)
5. Raspberry Pi 4 Power Supply (5.1V 3A Type-C) - 1 - power supply
6. Male Headers (1x40 Pin, 2.54mm) - 1
7. Female Headers (2x20 Pin, 2.54mm) - 1 
8. TTP223 Touch Sensor (Module) - 1 - input sensor

i found all the components on robu except SEN54 which i found on Tanotis

# CAD FILE
<img width="813" height="690" alt="image" src="https://github.com/user-attachments/assets/d1877694-3192-452c-83c8-d4c72e9f9ead" />
<img width="812" height="744" alt="image" src="https://github.com/user-attachments/assets/a19d3233-f189-4272-a84c-775d891d97c5" />
<img width="742" height="626" alt="image" src="https://github.com/user-attachments/assets/4e74e954-0d36-4b91-8a02-0cbb531f518d" />
<img width="831" height="706" alt="image" src="https://github.com/user-attachments/assets/2c1a639a-b9a9-44da-a6e6-7fefeb144837" />

# PCM
<img width="1426" height="813" alt="image" src="https://github.com/user-attachments/assets/eb6f39a9-dbb6-4685-8ff0-94941a7c6e6d" />
<img width="513" height="591" alt="image" src="https://github.com/user-attachments/assets/1b33d0f0-88cb-46fe-a269-6f3c5ebcec18" />
<img width="549" height="626" alt="image" src="https://github.com/user-attachments/assets/88d1899d-5447-4131-abd1-af00f280f7ca" />






