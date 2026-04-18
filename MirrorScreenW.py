import subprocess
import os
import shutil
import re
import time

# Set your device IP address.
DEVICE_IP = "192.168.1.101"

# Optional fallback port.
# Leave as None to auto-detect the current Wireless debugging port via ADB mDNS.
# Set a value here only if you want to force a specific current port.
DEVICE_PORT = None



# If adb / scrcpy are not in PATH, you can enter the full path here manually.
# Example: ADB_PATH = r"C:\Android\platform-tools\adb.exe"
#          SCRCPY_PATH = r"C:\Program Files\scrcpy\scrcpy.exe"
ADB_PATH = shutil.which("adb") or "adb"
SCRCPY_PATH = shutil.which("scrcpy") or "scrcpy"


def run_command(cmd, timeout=None):
    """Run a command and return (code, output, error)."""
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)
        return result.returncode, result.stdout.strip(), result.stderr.strip()
    except subprocess.TimeoutExpired:
        return 1, "", "Command timed out"


def discover_wireless_devices():
    """Return visible wireless debugging devices announced via ADB mDNS."""
    devices = {}

    for _ in range(5):
        code, out, err = run_command([ADB_PATH, "mdns", "services"], timeout=5)
        if code == 0:
            for line in out.splitlines():
                line_low = line.lower()
                if "adb-tls-connect" not in line_low and "_adb-tls-connect._tcp" not in line_low:
                    continue

                match = re.search(r"\b((?:\d{1,3}\.){3}\d{1,3}):(\d+)\b", line)
                if not match:
                    continue

                addr = f"{match.group(1)}:{match.group(2)}"
                parts = line.split()
                service_name = parts[0] if parts else addr
                devices[addr] = service_name

            if devices:
                break

        time.sleep(1)

    discovered = []
    for addr, service_name in devices.items():
        ip = addr.split(":", 1)[0]
        discovered.append({"addr": addr, "service": service_name, "preferred": ip == DEVICE_IP})

    discovered.sort(key=lambda item: (not item["preferred"], item["addr"]))
    return discovered


def print_discovered_devices(discovered):
    """Print the discovered wireless debugging devices in a readable layout."""
    print()
    print("Visible wireless debugging devices")
    print("-" * 34)

    if not discovered:
        print("No wireless debugging devices were discovered on the local network.")
        print()
        return

    for index, device in enumerate(discovered, start=1):
        preferred_note = "Yes" if device["preferred"] else "No"
        print(f"{index}. Address : {device['addr']}")
        print(f"   Service : {device['service']}")
        print(f"   Matches configured IP : {preferred_note}")
        print()


def choose_device_addr():
    """Choose the device address to use for connection."""
    configured_addr = f"{DEVICE_IP}:{DEVICE_PORT}" if DEVICE_PORT else None
    discovered = discover_wireless_devices()

    print_discovered_devices(discovered)

    if len(discovered) == 1:
        device = discovered[0]
        return device["addr"], f"mDNS discovery ({device['service']})"

    if len(discovered) > 1:
        print("Multiple devices are available. Choose which one to connect to.")

        while True:
            choice = input("Select a device number: ").strip()
            if choice.isdigit():
                selected_index = int(choice)
                if 1 <= selected_index <= len(discovered):
                    device = discovered[selected_index - 1]
                    return device["addr"], f"mDNS selection ({device['service']})"

            print("Invalid selection. Enter one of the listed numbers.")

    if configured_addr:
        print(f"Using configured fallback address: {configured_addr}")
        return configured_addr, "configured fallback port"

    print(f"Using default fallback address: {DEVICE_IP}:5555")
    return f"{DEVICE_IP}:5555", "default port fallback"


def ask_to_retry():
    """Ask the user whether to run the wireless flow again."""
    while True:
        choice = input("Run again? (y/n): ").strip().lower()
        if choice in {"y", "n"}:
            return choice == "y"

        print("Invalid input. Enter 'y' or 'n'.")


def main():
    # Check whether adb exists.
    if not shutil.which(ADB_PATH) and ADB_PATH == "adb":
        print("'adb' was not found. Install platform-tools or enter the full path in ADB_PATH.")
        os.system("pause")
        return

    # Check whether scrcpy exists.
    if not shutil.which(SCRCPY_PATH) and SCRCPY_PATH == "scrcpy":
        print("'scrcpy' was not found. Install scrcpy or enter the full path in SCRCPY_PATH.")
        os.system("pause")
        return

    while True:
        device_addr, addr_source = choose_device_addr()
        print("Connection details")
        print("-" * 18)
        print(f"Using device address {device_addr} ({addr_source}).")

        print("Disconnecting all connections...")
        code, out, err = run_command([ADB_PATH, "disconnect"], timeout=5)
        # No special handling is needed here.

        print(f"Trying to connect to the device at {device_addr}...")
        code, out, err = run_command([ADB_PATH, "connect", device_addr], timeout=10)

        # ADB reports success in multiple ways: "connected to ..." or "already connected to ...".
        out_low = (out or "").lower()
        err_low = (err or "").lower()
        connected_ok = (
            code == 0
            and (
                "connected to" in out_low
                or "already connected to" in out_low
                or "connected to" in err_low
                or "already connected to" in err_low
            )
        )

        if not connected_ok:
            print("Connection error:")
            if out:
                print("   Output:", out)
            if err:
                print("   Error:", err)

            # A few common hints.
            if "unable to connect" in out_low or "failed to connect" in out_low:
                print("Check the IP/port (Wireless debugging on the phone) and make sure the PC and phone are on the same network.")
            if "unauthorized" in out_low:
                print("Confirm 'Allow USB/Wireless debugging' on the phone.")
            if "10061" in out_low or "cannot connect" in out_low:
                print("The wireless debugging port may have changed. Open Wireless debugging on the phone and run the script again.")

            if ask_to_retry():
                continue

            os.system("pause")
            return

        print(f"Connected device: {device_addr}")

        print("Starting scrcpy...")
        code, out, err = run_command([SCRCPY_PATH, "-s", device_addr])

        if code != 0:
            print("Error while starting scrcpy:")
            if out:
                print("   Output:", out)
            if err:
                print("   Error:", err)

            # Common messages.
            low = (out + "\n" + err).lower()
            if "no devices/emulators found" in low:
                print("ADB cannot see the device. Try 'adb devices' manually and check that it says 'device', not 'unauthorized' or 'offline'.")
            elif "not recognized" in low or "no such file" in low:
                print("scrcpy is not in PATH. Enter the full path in SCRCPY_PATH.")

            if ask_to_retry():
                continue
        else:
            print("scrcpy finished.")
            if ask_to_retry():
                continue

        break

    os.system("pause")   # Keep CMD open at the end.


if __name__ == "__main__":
    main()
