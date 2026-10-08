#!/usr/bin/env python3
"""NaturalScrollSwitcher
External mouse connected    -> natural scrolling OFF
No external mouse connected -> natural scrolling ON

Run with --list to print which devices it sees as mice (for debugging).
"""
import ctypes
import datetime
import plistlib
import subprocess
import sys
import time

POLL_SECONDS = 2.0
IGNORED_PRODUCT_SUBSTRINGS = ("trackpad", "karabiner", "virtual")
BUILT_IN_TRANSPORTS = {"SPI", "FIFO", "I2C"}

# Private framework used by System Settings itself; applies the change live.
_pps = ctypes.CDLL(
    "/System/Library/PrivateFrameworks/PreferencePanesSupport.framework/PreferencePanesSupport"
)
_pps.setSwipeScrollDirection.argtypes = [ctypes.c_bool]
_pps.setSwipeScrollDirection.restype = None
_pps.swipeScrollDirection.argtypes = []
_pps.swipeScrollDirection.restype = ctypes.c_bool


def log(msg):
    print(f"[{datetime.datetime.now():%Y-%m-%d %H:%M:%S}] {msg}", flush=True)


def is_natural():
    return bool(_pps.swipeScrollDirection())


def set_natural(on):
    _pps.setSwipeScrollDirection(bool(on))


def hid_devices():
    try:
        out = subprocess.run(
            ["/usr/sbin/ioreg", "-r", "-c", "IOHIDDevice", "-d", "1", "-a"],
            capture_output=True, timeout=10,
        ).stdout
        return plistlib.loads(out) if out.strip() else []
    except Exception as e:
        log(f"ioreg failed: {e}")
        return None  # unknown; skip this cycle


def classify(dev):
    """Return (is_external_mouse, label)."""
    product = str(dev.get("Product", "Unknown"))
    transport = str(dev.get("Transport", ""))
    pairs = dev.get("DeviceUsagePairs", []) or []
    is_mouse = any(
        p.get("DeviceUsagePage") == 1 and p.get("DeviceUsage") == 2 for p in pairs
    ) or (dev.get("PrimaryUsagePage") == 1 and dev.get("PrimaryUsage") == 2)
    label = f"{product} [{transport or '?'}]"
    if not is_mouse:
        return False, label
    if dev.get("Built-In") is True or transport in BUILT_IN_TRANSPORTS:
        return False, label
    if any(s in product.lower() for s in IGNORED_PRODUCT_SUBSTRINGS):
        return False, label
    return True, label


def connected_mice(devices):
    return sorted({label for d in devices for ok, label in [classify(d)] if ok})


def list_mode():
    devices = hid_devices() or []
    print("Pointing devices:")
    for d in devices:
        if d.get("PrimaryUsagePage") == 1:
            ok, label = classify(d)
            print(f"  {'MOUSE ' if ok else 'ignore'} {label}")
    print(f"External mouse present: {bool(connected_mice(devices))}")
    print(f"Natural scrolling currently: {'ON' if is_natural() else 'OFF'}")


def main():
    if "--list" in sys.argv:
        list_mode()
        return
    log("NaturalScrollSwitcher started")
    last_present = None
    while True:
        devices = hid_devices()
        if devices is not None:
            mice = connected_mice(devices)
            present = bool(mice)
            if present != last_present:  # act only on transitions
                last_present = present
                want = not present
                if is_natural() != want:
                    set_natural(want)
                log(f"Mouse connected ({', '.join(mice)}) -> natural scrolling OFF"
                    if present else "No mouse -> natural scrolling ON")
        time.sleep(POLL_SECONDS)


if __name__ == "__main__":
    main()
