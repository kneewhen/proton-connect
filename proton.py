import subprocess
import time
import datetime
import sys

# ==============================
# CONFIGURATION
# ==============================
RECONNECT_DELAY = 1       # seconds between disable/enable
LOOP_INTERVAL = 600        # seconds between reconnect cycles
LOG_FILE = "proton_reconnect.log"
SEARCH_KEYWORDS = ["proton", "tap"]  # auto-detect adapter names
# ==============================


def log(msg):
    """Write timestamped logs to console and file."""
    timestamp = datetime.datetime.now().strftime("[%Y-%m-%d %H:%M:%S]")
    line = f"{timestamp} {msg}"
    print(line)
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(line + "\n")


def run_ps(command):
    """Run a PowerShell command and return output."""
    result = subprocess.run(
        ["powershell", "-Command", command],
        capture_output=True,
        text=True
    )
    return result.stdout.strip(), result.stderr.strip(), result.returncode


def detect_proton_adapter():
    """Find any network adapter whose name contains ProtonVPN keywords."""
    ps_cmd = "Get-NetAdapter | Select-Object -ExpandProperty Name"
    stdout, stderr, code = run_ps(ps_cmd)

    if code != 0:
        log(f"PowerShell error while listing adapters: {stderr}")
        return None

    for line in stdout.splitlines():
        name = line.strip()
        lower = name.lower()
        if any(k in lower for k in SEARCH_KEYWORDS):
            return name

    return None


def toggle_adapter(name):
    """Disable and re-enable the adapter."""
    try:
        log(f"Disabling adapter: {name}")
        subprocess.run([
            "powershell",
            "-Command",
            f'Disable-NetAdapter -Name "{name}" -Confirm:$false'
        ], check=True)

        time.sleep(RECONNECT_DELAY)

        log(f"Enabling adapter: {name}")
        subprocess.run([
            "powershell",
            "-Command",
            f'Enable-NetAdapter -Name "{name}" -Confirm:$false'
        ], check=True)

        log("Reconnect complete")

    except subprocess.CalledProcessError:
        log(f"ERROR: Could not toggle adapter '{name}'. Run script as Administrator.")


def main_loop():
    log("=== ProtonVPN Auto-Reconnect Script Started ===")

    while True:
        adapter = detect_proton_adapter()

        if adapter:
            log(f"Detected ProtonVPN adapter: {adapter}")
            toggle_adapter(adapter)
        else:
            log("No ProtonVPN adapter found. Is ProtonVPN using OpenVPN mode?")

        log(f"Sleeping {LOOP_INTERVAL} seconds...\n")
        time.sleep(LOOP_INTERVAL)


if __name__ == "__main__":
    try:
        main_loop()
    except KeyboardInterrupt:
        log("Script terminated by user.")
        sys.exit(0)
