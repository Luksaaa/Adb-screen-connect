import subprocess
import os


def run_command(cmd):
    """Run a command and return (code, output, error)."""
    result = subprocess.run(cmd, capture_output=True, text=True)
    return result.returncode, result.stdout.strip(), result.stderr.strip()


def start_scrcpy(serial):
    """Start scrcpy without blocking the script."""
    try:
        subprocess.Popen(["scrcpy", "-s", serial], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        return True, ""
    except OSError as exc:
        return False, str(exc)


def ask_to_launch_again():
    """Ask whether to launch another USB device."""
    while True:
        print()
        choice = input("Launch another USB device? (y/n): ").strip().lower()
        if choice == "cls":
            os.system("cls")
            continue
        if choice in {"y", "n"}:
            return choice == "y"

        print("Invalid input. Enter 'y', 'n', or 'cls'.")


def parse_selection_list(value, max_index):
    """Parse a comma-separated list of numeric selections."""
    parts = [part.strip() for part in value.split(",") if part.strip()]
    if not parts:
        return None

    indexes = []
    for part in parts:
        if not part.isdigit():
            return None
        selected_index = int(part)
        if not 1 <= selected_index <= max_index:
            return None
        if selected_index not in indexes:
            indexes.append(selected_index)

    return indexes


def choose_usb_device(usb_devices):
    """Choose one or more USB devices from the detected list."""
    if len(usb_devices) == 1:
        return [usb_devices[0]]

    print()
    print("Available USB devices")
    print("---------------------")
    for index, serial in enumerate(usb_devices, start=1):
        print(f"{index}. {serial}")

    print()
    print("Choose device numbers like '1' or '1,2', type 'cls' to refresh, or type 'back' to return.")

    while True:
        choice = input("Select a USB device: ").strip().lower()
        if choice == "cls":
            return "refresh"
        if choice == "back":
            return None
        selected_indexes = parse_selection_list(choice, len(usb_devices))
        if selected_indexes:
            return [usb_devices[selected_index - 1] for selected_index in selected_indexes]

        print("Invalid selection. Enter listed numbers, 'cls', or 'back'.")

def main():
    while True:
        print("Disconnecting all TCP/IP connections...")
        run_command(["adb", "disconnect"])

        print("Checking devices...")
        code, out, err = run_command(["adb", "devices"])
        if code != 0:
            print()
            print("Error while checking devices:", err or out)
            os.system("pause")
            return

        # Parse the device list.
        lines = out.splitlines()[1:]  # Skip the "List of devices attached" header.
        usb_devices = [line.split()[0] for line in lines if "\tdevice" in line and ":" not in line]

        if not usb_devices:
            print()
            print("No USB devices found.")
            print("Make sure the phone is connected with a USB cable and USB debugging is enabled.")
            os.system("pause")   # Keep the window open.
            return

        serials = choose_usb_device(usb_devices)
        if serials == "refresh":
            os.system("cls")
            continue
        if serials is None:
            return

        for serial in serials:
            print()
            print(f"USB device selected: {serial}")

            print()
            print("Starting scrcpy...")
            started, error = start_scrcpy(serial)
            if not started:
                print()
                print("Error while starting scrcpy:", error)
                if ask_to_launch_again():
                    os.system("cls")
                    break
                return

            print()
            print("scrcpy launched.")

        else:
            if ask_to_launch_again():
                os.system("cls")
                continue
            return

if __name__ == "__main__":
    main()
