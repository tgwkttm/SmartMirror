import requests
import time
import re
from arduino_module import init_serial, read_data

#configure ThingSpeak
THINGSPEAK_WRITE_API_KEY = "8055QMA0XZ7OAJBZ"
THINGSPEAK_CHANNEL_ID = "2832900"
THINGSPEAK_URL = "https://api.thingspeak.com/update"

#inițializare conexiune serială cu Arduino
serial_connection = init_serial('/dev/ttyUSB0')

def send_to_thingspeak(aqi, temperature, humidity):
    """send data to ThingSpeak."""
    payload = {
        "api_key": THINGSPEAK_WRITE_API_KEY,
        "field1": aqi,          # AQI
        "field2": temperature,  # Temperatură
        "field3": humidity      # Umiditate
    }
    try:
        response = requests.get(THINGSPEAK_URL, params=payload)
        if response.status_code == 200:
            print("[INFO] Data sent to ThingSpeak successfully!")
        else:
            print(f"[ERROR] Failed to send data: {response.text}")
    except Exception as e:
        print(f"[ERROR] Exception while sending data: {e}")


def read_and_send_data():
    """Read data from arduino and send it to ThingSpeak"""
    while True:
        if serial_connection:
            data = read_data(serial_connection)
            if data:
                print(f"Raw Sensor Data: {data}")
                
                # Ignoră mesajele de calibrare
                if "Calibrating" in data or "Calibrated R0" in data:
                    print("[INFO] Calibration message detected, skipping...")
                    continue
                
                match = re.search(
                    r"CO2: ([\d\.]+) ppm \| NH3: ([\d\.]+) ppm \| Benzen: ([\d\.]+) ppm \| "
                    r"Alcohol: ([\d\.]+) ppm \| NOx: ([\d\.]+) ppm \| Temp: (\d+\.\d+)°C \| "
                    r"Humidity: (\d+\.\d+)% \| AQI: (\d+)", data
                )
                
                if match:
                    co2, nh3, benzen, alcohol, nox, temperature, humidity, aqi = match.groups()
                    send_to_thingspeak(aqi, temperature, humidity)
                else:
                    print("[ERROR] Failed to parse sensor data.")
            time.sleep(15)  # Trimite datele la fiecare 15 secunde

if __name__ == "__main__":
    read_and_send_data()