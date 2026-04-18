import subprocess
import os

def run_command(cmd):
    """Run a command and return (code, output, error)."""
    result = subprocess.run(cmd, capture_output=True, text=True)
    return result.returncode, result.stdout.strip(), result.stderr.strip()

def main():
    print("Disconnecting all TCP/IP connections...")
    run_command(["adb", "disconnect"])

    print("Checking devices...")
    code, out, err = run_command(["adb", "devices"])
    if code != 0:
        print("Error while checking devices:", err or out)
        os.system("pause")
        return

    # Parse the device list.
    lines = out.splitlines()[1:]  # Skip the "List of devices attached" header.
    usb_devices = [line.split()[0] for line in lines if "\tdevice" in line and ":" not in line]

    if not usb_devices:
        print("No USB devices found.")
        print("Make sure the phone is connected with a USB cable and USB debugging is enabled.")
        os.system("pause")   # Keep the window open.
        return

    serial = usb_devices[0]
    print(f"USB device found: {serial}")

    print("Starting scrcpy...")
    code, out, err = run_command(["scrcpy", "-s", serial])
    if code != 0:
        print("Error while starting scrcpy:", err or out)
    else:
        print("scrcpy finished.")

    os.system("pause")   # Keep the window open at the end.

if __name__ == "__main__":
    main()
