<p align=center>
  <img width="800" alt="dwu" src="https://github.com/user-attachments/assets/811da782-793d-44cb-b844-e16626077e00">
</p>

<p align="center">
  <a href="https://aur.archlinux.org/packages/dwu">
    <img src="https://img.shields.io/aur/version/dwu?style=flat-square" alt="AUR">
  </a>
  <a href="https://pypi.org/project/dwu/">
    <img src="https://img.shields.io/pypi/v/dwu?style=flat-square" alt="PyPI">
  </a>
  <a href="https://github.com/starrieste/dwu/stargazers">
    <img src="https://img.shields.io/github/stars/starrieste/dwu?style=flat-square" alt="Stars">
  </a>
</p>

---
<p align=center>A CLI tool that updates your desktop wallpaper each day to the latest anime wallpaper from <a href=https://wallpaper-a-day.com>wallpaper-a-day.com</a>  </p>
<p align=center>This is my first proper github project+fork so things may not work as intended! and most of the programing was done via AI Agents, so if that tips you off from installing and using? that's understable!</p>

<h1>Installation</h1>

**DWU - KDE Plasma Edition**

A specialized fork of Daily Wallpaper Updater, re-engineered specifically for **KDE Plasma**.

Unlike the original, this version uses KDE's native tools to manage wallpapers:

- **Primary Method**: Uses `plasma-apply-wallpaperimage` (KDE Plasma 6 recommended tool)
- **Fallback Method**: Direct D-Bus calls via `qdbus` for older Plasma versions
- **Resolution Detection**: Uses `kscreen-doctor` for smart watermark positioning

This means:
- No extra daemons (no swww, awww, or feh required)
- Multi-Monitor Sync (updates all screens and activities instantly)
- Smart Watermarks (auto-detects resolution to prevent cut-off text)

## Installation

The recommended way to install `dwu` is using `pipx`. This installs the tool in a clean, isolated environment.

### 1. Install pipx
**Arch / EndeavourOS:**
```bash
sudo pacman -S python-pipx
```
**Debian:** *(Haven't tested this, so it's likely to not work, but feel free to try!)*

```bash
sudo apt install pipx
```

### 2. Install My Fork

```bash
pipx install git+https://github.com/MadHatz42/dwu.git
```

<h1>Usage</h1>

Set to today's wallpaper
```bash
dwu --today
```

If you don't like a certain day's wallpaper, you can skip it:
```bash
dwu --skip
```

Set to the wallpaper from a certain amount of days before today (integer should be from 0-9)
```bash
dwu --back 2 # 2 days before today's wallpaper
```

If you like a wallpaper, you can save it!

```bash
dwu --save-dir ~/Wallpapers
dwu --save
```

I've tried to make a "Continuous Mode" like the original, I haven't done enough testing to confirm if it works 100% yet, so please report bugs or give advice on how to improve it! 
you can use systemd in two ways:

**Option 1: Continuous Mode (Recommended)**
Runs continuously in the background, checking for new wallpapers every hour:

```bash
# Copy the service file to your systemd user directory
cp systemd/dwu.service ~/.config/systemd/user/

# IMPORTANT: Edit the service file to use the correct path to dwu
# Find where dwu is installed: which dwu
# Then edit ~/.config/systemd/user/dwu.service and update the ExecStart line
# The default path is /usr/bin/dwu (for AUR/system packages)
# If installed via pipx/pip --user, change to: /home/YOUR_USERNAME/.local/bin/dwu
nano ~/.config/systemd/user/dwu.service

# Reload systemd and enable the service
systemctl --user daemon-reload
systemctl --user enable --now dwu.service

# Check status
systemctl --user status dwu.service

# View logs
journalctl --user -u dwu.service -f
```

**Option 2: Timer-based (Hourly)**
Runs once per hour using a timer:

```bash
# Copy both service and timer files
cp systemd/dwu.service ~/.config/systemd/user/
cp systemd/dwu.timer ~/.config/systemd/user/

# Enable and start the timer
systemctl --user enable --now dwu.timer
```

**Manual Continuous Mode**
You can also run continuous mode manually (useful for testing):

```bash
dwu --continuous              # Check every hour (default)
dwu --continuous --interval 1800  # Check every 30 minutes
```

The wallpaper has a watermark to credit the artist in the bottom right corner.  
Without artists, you wouldn't get amazing wallpapers! So please do show them some support!  
To remove it (for the current wallpaper), run the following command.  

```bash
dwu --credits
```
