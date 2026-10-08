# Natural Scroll Switcher

Automatically turns macOS **natural scrolling off when a mouse is connected** and **back on when it's disconnected**, so the trackpad always feels natural and the mouse wheel always scrolls the "normal" way.

No app to install, nothing to compile — just a small Python script that runs in the background and starts at login.

## Install

```bash
git clone https://github.com/dorshoham/natural-scroll-switcher.git
cd natural-scroll-switcher
bash install.sh
```

At the end, the installer prints the devices it detected, for example:

```
Pointing devices:
  MOUSE  Razer DeathAdder V2 [USB]
  ignore Apple Internal Keyboard / Trackpad [USB]
  ignore Magic Keyboard [Bluetooth]
External mouse present: True
Natural scrolling currently: OFF
```

Plug your mouse in or out, and the scroll direction switches within about 2 seconds.

## Uninstall

```bash
bash install.sh --uninstall
```

## How it works

- Every 2 seconds it reads the list of connected input devices (`ioreg`) and checks for an external mouse (USB or Bluetooth). Built-in trackpads, Magic Trackpads and keyboards are ignored.
- It only acts when a mouse **connects or disconnects**, so if you change the setting by hand, it leaves you alone until the next plug or unplug.
- It changes the setting through the same system function that System Settings uses, so the change applies instantly with no logout.
- It runs as a LaunchAgent (`~/Library/LaunchAgents/local.naturalscrollswitcher.plist`) and restarts automatically if it stops.

## Good to know

- macOS has **one** natural-scrolling setting shared by the trackpad and the mouse. While a mouse is connected, the trackpad scrolls the non-natural way too. If you want each device to have its own direction at all times, look at [LinearMouse](https://linearmouse.app) or [Scroll Reverser](https://pilotmoon.com/scrollreverser/).
- It uses a private macOS framework (`PreferencePanesSupport`) to apply the change live. Apple could change it in a future macOS version.
- Tested on macOS 15 (Intel). It uses the `python3` that ships with Apple's Command Line Tools; if `python3` is missing, run `xcode-select --install`.

## Troubleshooting

- **See what it detects:** `python3 natural_scroll_switcher.py --list`
- **Log file:** `~/Library/Logs/NaturalScrollSwitcher.log`
- **A device is wrongly counted as a mouse** (for example, a virtual device created by mouse software): add part of its name to `IGNORED_PRODUCT_SUBSTRINGS` at the top of `natural_scroll_switcher.py`, then run `bash install.sh` again.

## License

MIT
