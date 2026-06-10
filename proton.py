import subprocess
import time

ADAPTER_NAME = "ProtonVPN"
RECONNECT_DELAY = 5       # seconds
LOOP_INTERVAL = 600       # seconds, set to None if you don't want a loop

def toggle_adapter(adapter_name):
    try:
        print(f"Disconnecting {adapter_name}...")
        subprocess.run([
            "powershell",
            "-Command",
            f'Disable-NetAdapter -Name "{adapter_name}" -Confirm:$false'
        ], check=True)

        time.sleep(RECONNECT_DELAY)

        print(f"Reconnecting {adapter_name}...")
        subprocess.run([
            "powershell",
            "-Command",
            f'Enable-NetAdapter -Name "{adapter_name}" -Confirm:$false'
        ], check=True)

        print("Reconnect complete!\n")
    except subprocess.CalledProcessError:
        print(f"Error: Could not toggle {adapter_name}. Make sure you run as Administrator.")

if LOOP_INTERVAL:
    while True:
        toggle_adapter(ADAPTER_NAME)
        print(f"Waiting {LOOP_INTERVAL} seconds before next reconnect...")
        time.sleep(LOOP_INTERVAL)
else:
    toggle_adapter(ADAPTER_NAME)