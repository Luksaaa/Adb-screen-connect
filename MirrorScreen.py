import os
import subprocess
import sys


BASE_DIR = os.path.dirname(os.path.abspath(__file__))
USB_SCRIPT = os.path.join(BASE_DIR, "MirrorScreenC.py")
WIRELESS_SCRIPT = os.path.join(BASE_DIR, "MirrorScreenW.py")


def clear_screen():
    os.system("cls")


def run_script(script_path):
    subprocess.run([sys.executable, script_path], check=False)


def main():
    while True:
        clear_screen()
        print("Android Screen Mirror Launcher")
        print("-----------------------------")
        print("1. USB")
        print("2. Wireless")
        print("3. Exit")
        print()
        print("Choose how you want to connect.")
        print("You can choose Wireless even if the same device is connected by cable.")
        print()

        choice = input("Select an option: ").strip().lower()

        if choice == "1":
            run_script(USB_SCRIPT)
            continue

        if choice == "2":
            run_script(WIRELESS_SCRIPT)
            continue

        if choice in {"3", "q", "quit", "exit"}:
            break

        print()
        print("Invalid option. Press Enter to try again.")
        input()


if __name__ == "__main__":
    main()
