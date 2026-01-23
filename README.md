<p align=center>
  <img width="800" alt="dwu" src="https://github.com/user-attachments/assets/811da782-793d-44cb-b844-e16626077e00">
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
**Arch / EndeavourOS / CatchyOS / Steam:**
```bash
sudo pacman -S python-pipx
```
**Debian:** *(Haven't tested this, so it's likely to not work, but feel free to try!)*

```bash
sudo apt install pipx
```

### 2. Install DWU

```bash
pipx install git+https://github.com/Zoshiao/dwu4kde.git
```

### 2.1 Upgrade DWU (later on)

If you already have DWU installed via `pipx` and want to upgrade to the latest version from GitHub:

```bash
pipx upgrade --force git+https://github.com/Zoshiao/dwu4kde.git
```

If that doesn’t pick up changes for some reason, you can reinstall:

```bash
pipx uninstall dwu
pipx install git+https://github.com/Zoshiao/dwu4kde.git
```

### 3. Set Up Automatic Updates (Optional but Recommended)

After installation, set up automatic hourly wallpaper updates:

```bash
# Get the repository (to access systemd files)
git clone https://github.com/Zoshiao/dwu4kde.git
cd dwu
```

```bash
# Install the systemd timer (works from repo root)
./systemd/install.sh
```

This will automatically:
- Set up a systemd timer that checks for new wallpapers every hour
- Set the wallpaper on boot/login  
- Work on any machine without configuration (automatically finds `dwu` in PATH via pipx)

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

**Filter by Resolution**

You can filter wallpapers by resolution tag. By default, `dwu --today` fetches from the main page, which includes **all resolutions** (1080p, 1440p, 2160p, etc.).  
Use these flags if you only want higher-resolution wallpapers:

```bash
dwu --today --1440p      # Latest 1440p wallpaper
dwu --today --2160p      # Latest 2160p (4K) wallpaper

# Go back through older high‑res posts
dwu --back 2 --1440p     # The 3rd most recent 1440p post

# Work with skips within a specific resolution
dwu --list-skipped --2160p   # List skipped wallpapers from the 4K tag
```

Notes:
- You can only use **one** resolution flag at a time.
- For `--back N` with a resolution flag, `N` means “Nth most recent post for that resolution”,  
  not “exactly N calendar days ago” (since high‑res posts are not daily on the site).

<h1>Automatic Wallpaper Updates (systemd Timer)</h1>
If you didn't set up automatic updates during installation, you can do it now. The timer runs `dwu --today` once per hour to check for new wallpapers.

**Quick Install:**
```bash
# From the repository root directory
./systemd/install.sh
```

**Manual Install:**
```bash
# Create systemd user directory if it doesn't exist
mkdir -p ~/.config/systemd/user

# Copy the service, timer, and wrapper script
cp systemd/dwu.service ~/.config/systemd/user/
cp systemd/dwu.timer ~/.config/systemd/user/
cp systemd/dwu-wrapper.sh ~/.config/systemd/user/
chmod +x ~/.config/systemd/user/dwu-wrapper.sh

# Reload systemd and enable the timer
systemctl --user daemon-reload
systemctl --user enable --now dwu.timer

# Check timer status
systemctl --user status dwu.timer

# Check when the timer will run next
systemctl --user list-timers dwu.timer

# View logs
journalctl --user -u dwu.service -f
```

<h1>Troubleshooting</h1>

If you run into issues during installation or updates, try these solutions.

"Command not found" after installing If the installation finished but the terminal can't find dwu, your local bin folder might not be in your PATH. Run this once and restart your terminal:
```bash
pipx ensurepath
```

"bash: /usr/bin/dwu: No such file or directory" If you previously installed an older version of dwu, your terminal might remember the old location. Force it to forget:
```bash
hash -r  # Clear command cache
pipx ensurepath  # Ensure pipx bin directory is in PATH
```

error: externally-managed-environment" or "exists in filesystem" This happens if you previously installed Python packages using sudo pip. You need to remove the conflicting system packages before pipx can work:
```bash
sudo pip uninstall [INSTER CONFLICTING PACKAGE] dwu --break-system-packages # In my case it was the 'click' package
```

The wallpaper has a watermark to credit the artist in the bottom right corner.  
Without artists, you wouldn't get amazing wallpapers! So please do show them some support!  
To remove it (for the current wallpaper), run the following command.  

```bash
dwu --credits
```

<h1>Uninstallation</h1>

To completely remove DWU from your system:

**1. Stop and disable the systemd timer (if installed):**
```bash
systemctl --user stop dwu.timer
systemctl --user disable dwu.timer
systemctl --user daemon-reload
```

**2. Remove systemd files (optional cleanup):**
```bash
rm ~/.config/systemd/user/dwu.service
rm ~/.config/systemd/user/dwu.timer
rm ~/.config/systemd/user/dwu-wrapper.sh
systemctl --user daemon-reload
```

**3. Uninstall DWU via pipx:**
```bash
pipx uninstall dwu
```

**4. Remove cached files (optional):**
```bash
# Remove wallpaper cache and metadata
rm -r ~/.cache/dwu

# Remove configuration (if you want to remove all settings)
rm -r ~/.config/dwu
```
