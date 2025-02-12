import psutil
import time

def get_cpu_ram_usage():
    cpu_usage = psutil.cpu_percent(interval=3)  #measure CPU usage (%)
    ram_usage = psutil.virtual_memory().used / (1024 * 1024)  # RAM usage (MB)
    return cpu_usage, ram_usage

# Tested scenarios
scenarios = ["Idle Mode (Only UI)", "During Login (Facial Recognition)", "Full Mode (Emotion Detection)"]
results = {}

for scenario in scenarios:
    input(f"\nSTART {scenario} and then PRESS ENTER to measure resource usage...")
    cpu, ram = get_cpu_ram_usage()
    results[scenario] = (cpu, ram)
    print(f"{scenario} - CPU: {cpu}%, RAM: {ram}MB")

print("\nTests are complete! Note down the values and use them for the graph.")