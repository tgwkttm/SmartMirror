import serial

def init_serial(port='/dev/ttyUSB0', baud_rate=9600):
    try:
        ser = serial.Serial(port, baud_rate)
        print(f"Conectat la {port}")
        return ser
    except serial.SerialException as e:
        print(f"Couldn't connect to {port}: {e}")
        return None

def read_data(ser):
    try:
        data = ser.readline().decode('utf-8', errors='ignore').strip()  #Ignor invalid characters
        return data
    except Exception as e:
        print(f"Error reading data from sensors: {e}")
        return None

def close_serial(ser):
    if ser and ser.is_open:
        ser.close()
        print("Serial port was closed.")
