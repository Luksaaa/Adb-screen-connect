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


def show_loading(label, step):
    """Show a lightweight inline loading indicator."""
    dots = "." * ((step % 3) + 1)
    print(f"\r{label}{dots}   ", end="", flush=True)


def clear_loading():
    """Clear the inline loading indicator line."""
    print("\r" + " " * 60 + "\r", end="", flush=True)


def discover_wireless_devices():
    """Return visible wireless debugging devices announced via ADB mDNS."""
    devices = {}

    for attempt in range(5):
        show_loading("Searching for wireless debugging devices", attempt)
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

    clear_loading()

    discovered = []
    for addr, service_name in devices.items():
        ip = addr.split(":", 1)[0]
        discovered.append({"addr": addr, "service": service_name, "preferred": ip == DEVICE_IP})

    discovered.sort(key=lambda item: (not item["preferred"], item["addr"]))
    return discovered


def resolve_connect_addr_for_ip(default_ip, current_addr):
    """Resolve the current connect address for the selected device IP."""
    for device in discover_wireless_devices():
        if device["addr"].split(":", 1)[0] == default_ip:
            return device["addr"]

    return current_addr


def discover_pairing_devices():
    """Return visible wireless pairing devices announced via ADB mDNS."""
    devices = {}

    for attempt in range(5):
        show_loading("Searching for wireless pairing devices", attempt)
        code, out, err = run_command([ADB_PATH, "mdns", "services"], timeout=5)
        if code == 0:
            for line in out.splitlines():
                line_low = line.lower()
                if "adb-tls-pairing" not in line_low and "_adb-tls-pairing._tcp" not in line_low:
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

    clear_loading()

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


def print_pairing_devices(discovered):
    """Print the discovered wireless pairing devices in a readable layout."""
    if not discovered:
        return

    print()
    print("Visible wireless pairing devices")
    print("-" * 31)

    for index, device in enumerate(discovered, start=1):
        preferred_note = "Yes" if device["preferred"] else "No"
        print(f"{index}. Address : {device['addr']}")
        print(f"   Service : {device['service']}")
        print(f"   Matches configured IP : {preferred_note}")
        print()


def normalize_pairing_addr(value, default_ip):
    """Normalize pairing input as either port-only or full IP:port."""
    value = value.strip()
    if value.isdigit():
        return f"{default_ip}:{value}"
    return value


def choose_device_addr():
    """Choose the device address to use for connection."""
    configured_addr = f"{DEVICE_IP}:{DEVICE_PORT}" if DEVICE_PORT else None
    while True:
        os.system("cls")
        print("Wireless debugging device scan starting...")
        discovered = discover_wireless_devices()

        print_discovered_devices(discovered)

        if discovered:
            print("Choose a device number, type 'cls' to refresh, or type 'pair' for wireless pairing.")

            while True:
                choice = input("Select a device number: ").strip().lower()
                if choice == "cls":
                    break
                if choice == "pair":
                    paired_ok, _ = run_pairing_flow(DEVICE_IP, f"{DEVICE_IP}:5555")
                    if paired_ok:
                        break
                    continue
                if choice.isdigit():
                    selected_index = int(choice)
                    if 1 <= selected_index <= len(discovered):
                        device = discovered[selected_index - 1]
                        return device["addr"], f"mDNS selection ({device['service']})"

                print("Invalid selection. Enter a listed number, 'cls', or 'pair'.")

            continue

        print("No wireless debugging devices were discovered.")
        print("Type 'cls' to refresh or 'pair' for wireless pairing.")
        choice = input("Action: ").strip().lower()
        if choice == "cls":
            continue
        if choice == "pair":
            run_pairing_flow(DEVICE_IP, f"{DEVICE_IP}:5555")
            continue

        if configured_addr:
            print(f"Using configured fallback address: {configured_addr}")
            return configured_addr, "configured fallback port"

        print(f"Using default fallback address: {DEVICE_IP}:5555")
        return f"{DEVICE_IP}:5555", "default port fallback"


def ask_to_retry():
    """Ask the user whether to run the wireless flow again."""
    while True:
        choice = input("Run again? (y/n): ").strip().lower()
        if choice == "cls":
            os.system("cls")
            continue
        if choice in {"y", "n"}:
            return choice == "y"

        print("Invalid input. Enter 'y', 'n', or 'cls'.")


def run_pairing_flow(default_ip, current_addr):
    """Run wireless pairing flow for first-time wireless setup."""
    print()
    print("Open 'Pair device with pairing code' on the phone before continuing.")
    print()

    while True:
        discovered = discover_pairing_devices()
        print_pairing_devices(discovered)

        pairing_addr = None
        if len(discovered) == 1:
            pairing_addr = discovered[0]["addr"]
            print(f"Using pairing address {pairing_addr}.")
        elif len(discovered) > 1:
            print("Multiple pairing devices are available.")
            print("Enter the number of the pairing device or type the pairing port / IP:port.")
            choice = input("Pairing device: ").strip().lower()
            if choice == "cls":
                os.system("cls")
                continue
            if choice.isdigit():
                selected_index = int(choice)
                if 1 <= selected_index <= len(discovered):
                    pairing_addr = discovered[selected_index - 1]["addr"]
                else:
                    pairing_addr = normalize_pairing_addr(choice, default_ip)
            else:
                pairing_addr = normalize_pairing_addr(choice, default_ip)
        else:
            pairing_addr = normalize_pairing_addr(input("Enter pairing port or address (IP:port): "), default_ip)

        if not pairing_addr:
            print()
            print("Pairing address is required.")
            if ask_to_retry():
                continue
            return False, current_addr

        pairing_code = input("Enter pairing code: ").strip()
        if not pairing_code:
            print()
            print("Pairing code is required.")
            if ask_to_retry():
                continue
            return False, current_addr

        print()
        print(f"Pairing with {pairing_addr}...")
        code, out, err = run_command([ADB_PATH, "pair", pairing_addr, pairing_code], timeout=20)
        out_low = (out or "").lower()
        err_low = (err or "").lower()
        paired_ok = code == 0 and ("successfully paired" in out_low or "successfully paired" in err_low)

        if paired_ok:
            print()
            print("Pairing successful.")
            time.sleep(2)
            return True, resolve_connect_addr_for_ip(default_ip, current_addr)

        print()
        print("Pairing error:")
        if out:
            print("   Output:", out)
        if err:
            print("   Error:", err)

        if not ask_to_retry():
            return False, current_addr


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
            print()
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

            paired_ok, paired_addr = run_pairing_flow(device_addr.split(":", 1)[0], device_addr)
            if paired_ok:
                device_addr = paired_addr
                continue

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
