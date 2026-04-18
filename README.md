# Android Screen Mirror Launcher

Small Windows Python scripts for launching `scrcpy` over:

- USB
- Wireless Debugging
- or both, through a simple launcher menu

This repository contains three scripts:

- `MirrorScreenBoth.py` - launcher with USB / Wireless menu
- `MirrorScreenC.py` - USB mode
- `MirrorScreenW.py` - Wireless mode

## Requirements

Install the following before using the scripts:

1. Python 3
2. Android Platform Tools (`adb`)
3. `scrcpy`

## Downloads

### Python

Download Python 3 from:

- https://www.python.org/downloads/

During installation, enable `Add Python to PATH`.

### Android Platform Tools

Download Android Platform Tools from:

- https://developer.android.com/tools/releases/platform-tools

This provides the `adb` command.

### scrcpy

Download `scrcpy` from:

- https://github.com/Genymobile/scrcpy

Make sure `scrcpy` is available in your system `PATH`, or edit the script and set the full path manually.

## Windows Setup

You can use either of these approaches:

1. Add `adb` and `scrcpy` to your `PATH`
2. Edit `MirrorScreenW.py` and set `ADB_PATH` and `SCRCPY_PATH` manually

Example:

```python
ADB_PATH = r"C:\Android\platform-tools\adb.exe"
SCRCPY_PATH = r"C:\Program Files\scrcpy\scrcpy.exe"
```

`MirrorScreenC.py` uses the commands directly from `PATH`, so the USB script works best when `adb` and `scrcpy` are already available globally.

## Android Setup

On your Android device:

1. Enable `Developer options`
2. Enable `USB debugging`
3. For wireless use, enable `Wireless debugging`

Typical path on Android:

- `Settings` -> `Developer options` -> `USB debugging`
- `Settings` -> `Developer options` -> `Wireless debugging`

## Files

### `MirrorScreenBoth.py`

Use this as the main entry point.

What it does:

1. Shows a simple launcher menu
2. Lets you choose `USB` or `Wireless`
3. Returns you to the main menu after each mode finishes

### `MirrorScreenC.py`

Use this script when your phone is connected with a USB cable.

What it does:

1. Disconnects existing ADB TCP/IP connections
2. Checks connected USB devices
3. Lets you choose one or more USB devices if multiple are connected
4. Launches `scrcpy` for each selected device

### `MirrorScreenW.py`

Use this script when you want to connect over Wi-Fi.

What it does:

1. Finds Android devices that advertise Wireless Debugging through ADB mDNS
2. Lets you choose one or more wireless devices if multiple are found
3. Supports manual wireless pairing when connect fails
4. Connects with `adb connect`
5. Launches `scrcpy` for each selected device

## How To Use

## Recommended Launcher

Run the main launcher:

```bash
py -3 MirrorScreenBoth.py
```

It gives you:

- `1. USB`
- `2. Wireless`
- `3. Exit`

You can choose Wireless even if the same device is connected by cable.

## USB Mode

1. Connect your phone with a USB cable
2. Make sure `USB debugging` is enabled on the phone
3. Accept the debugging authorization prompt on the phone if it appears
4. Run directly:

```bash
py -3 MirrorScreenC.py
```

If Python is available as `python`, you can also run:

```bash
python MirrorScreenC.py
```

The script can launch:

- one USB device
- multiple USB devices in one selection, for example `1,2`

## Wireless Mode

1. Make sure the phone and PC are on the same Wi-Fi network
2. Enable `Wireless debugging` on the phone
3. Run directly:

```bash
py -3 MirrorScreenW.py
```

The script will:

- list Android devices that expose Wireless Debugging
- let you choose one device or multiple devices like `1,2`
- support `pair` if the device is not already paired
- connect and launch `scrcpy`

## Configuration

In `MirrorScreenW.py` you can change:

```python
DEVICE_IP = "192.168.1.101"
DEVICE_PORT = None
```

Notes:

- `DEVICE_IP` is used as the preferred device IP
- `DEVICE_PORT = None` means the script tries to auto-detect the current wireless debugging port
- if you set a fixed port manually, it will be used as a fallback

## Important Notes About Wireless Debugging

Android Wireless Debugging may change the connection port after disabling and enabling it again.

Because of that:

- the wireless script tries to detect the current port automatically
- automatic connection works best when the device is already paired with the PC
- if Android asks for pairing again, you must pair the device again before `adb connect` can work
- when pairing, use the `IP address & Port` shown in the lower `Pair with device` popup, not the one from the main Wireless debugging screen

## Troubleshooting

### `adb` not found

Cause:

- Android Platform Tools are not installed
- `adb` is not in `PATH`

Fix:

1. Install Platform Tools
2. Add the folder to `PATH`
3. Or set `ADB_PATH` manually in `MirrorScreenW.py`

### `scrcpy` not found

Cause:

- `scrcpy` is not installed
- `scrcpy` is not in `PATH`

Fix:

1. Install `scrcpy`
2. Add it to `PATH`
3. Or set `SCRCPY_PATH` manually in `MirrorScreenW.py`

### Wireless connection fails

Check the following:

1. The PC and phone are on the same network
2. `Wireless debugging` is enabled
3. The device is already paired if Android requires pairing
4. The phone is visible in ADB mDNS discovery
5. If pairing is needed, open `Pair device with pairing code` on the phone before entering the pairing code and port

### No USB device found

Check the following:

1. The cable supports data transfer
2. `USB debugging` is enabled
3. The phone authorization popup was accepted

## Summary

- Use `MirrorScreenBoth.py` as the main launcher
- Use `MirrorScreenC.py` for USB mirroring only
- Use `MirrorScreenW.py` for wireless mirroring only
- Install Python, Android Platform Tools, and `scrcpy` first
- Wireless mode depends on ADB discovery and Android Wireless Debugging behavior
- USB and Wireless modes both support launching multiple devices
