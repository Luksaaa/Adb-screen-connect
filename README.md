# Android Screen Mirror Launcher

Small Windows Python scripts for launching `scrcpy` with either:

- a USB-connected Android device
- a wireless Android device using ADB Wireless Debugging

This repository contains two scripts:

- `MirrorScreenC.py` for USB connections
- `MirrorScreenW.py` for wireless connections

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

### `MirrorScreenC.py`

Use this script when your phone is connected with a USB cable.

What it does:

1. Disconnects existing ADB TCP/IP connections
2. Checks connected ADB devices
3. Picks the first USB device it finds
4. Starts `scrcpy`

### `MirrorScreenW.py`

Use this script when you want to connect over Wi-Fi.

What it does:

1. Shows devices currently visible on the local Wi-Fi network
2. Shows Android devices that advertise Wireless Debugging through ADB mDNS
3. Lets you choose a wireless device if multiple are found
4. Connects with `adb connect`
5. Starts `scrcpy`

## How To Use

## USB Mode

1. Connect your phone with a USB cable
2. Make sure `USB debugging` is enabled on the phone
3. Accept the debugging authorization prompt on the phone if it appears
4. Run:

```bash
py -3 MirrorScreenC.py
```

If Python is available as `python`, you can also run:

```bash
python MirrorScreenC.py
```

## Wireless Mode

1. Make sure the phone and PC are on the same Wi-Fi network
2. Enable `Wireless debugging` on the phone
3. Run:

```bash
py -3 MirrorScreenW.py
```

The script will:

- list visible devices on the local network
- list Android devices that expose Wireless Debugging
- ask you to choose a device if more than one is available
- connect and open `scrcpy`

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

### No USB device found

Check the following:

1. The cable supports data transfer
2. `USB debugging` is enabled
3. The phone authorization popup was accepted

## Summary

- Use `MirrorScreenC.py` for USB mirroring
- Use `MirrorScreenW.py` for wireless mirroring
- Install Python, Android Platform Tools, and `scrcpy` first
- Wireless mode depends on ADB discovery and Android Wireless Debugging behavior
