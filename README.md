# Whisker Litter-Robot Integration for Unfolded Circle Remote 2/3

Monitor and control your Whisker **Litter-Robot** smart litter boxes directly from your Unfolded Circle Remote 2 or Remote 3 with **full status monitoring**, **clean cycle control**, and a **dedicated remote entity** for activities.

![Whisker](https://img.shields.io/badge/Whisker-Litter--Robot-blue)
[![GitHub Release](https://img.shields.io/github/v/release/mase1981/uc-intg-whisker?style=flat-square)](https://github.com/mase1981/uc-intg-whisker/releases)
![License](https://img.shields.io/badge/license-MPL--2.0-blue?style=flat-square)
[![GitHub issues](https://img.shields.io/github/issues/mase1981/uc-intg-whisker?style=flat-square)](https://github.com/mase1981/uc-intg-whisker/issues)
[![Community Forum](https://img.shields.io/badge/community-forum-blue?style=flat-square)](https://unfolded.community/)
[![Discord](https://badgen.net/discord/online-members/zGVYf58)](https://discord.gg/zGVYf58)
![GitHub Downloads (all assets, all releases)](https://img.shields.io/github/downloads/mase1981/uc-intg-whisker/total?style=flat-square)
[![Buy Me A Coffee](https://img.shields.io/badge/buy%20me%20a%20coffee-donate-yellow.svg?style=flat-square)](https://buymeacoffee.com/meirmiyara)
[![PayPal](https://img.shields.io/badge/PayPal-donate-blue.svg?style=flat-square)](https://paypal.me/mmiyara)
[![Github Sponsors](https://img.shields.io/badge/GitHub%20Sponsors-30363D?&logo=GitHub-Sponsors&logoColor=EA4AAA&style=flat-square)](https://github.com/sponsors/mase1981)


## Features

This integration connects to your Whisker cloud account (the same login used by the Whisker mobile app) and automatically discovers every Litter-Robot on the account, delivering seamless integration with your Unfolded Circle Remote including status monitoring, clean cycle control, night light, panel lock, sleep mode, and clean cycle wait time configuration. It provides the **full command surface of the Home Assistant Litter-Robot integration**.

---
## ❤️ Support Development ❤️

If you find this integration useful, consider supporting development:

[![GitHub Sponsors](https://img.shields.io/badge/Sponsor-GitHub-pink?style=for-the-badge&logo=github)](https://github.com/sponsors/mase1981)
[![Buy Me A Coffee](https://img.shields.io/badge/Buy%20Me%20A%20Coffee-FFDD00?style=for-the-badge&logo=buy-me-a-coffee&logoColor=black)](https://www.buymeacoffee.com/meirmiyara)
[![PayPal](https://img.shields.io/badge/PayPal-00457C?style=for-the-badge&logo=paypal&logoColor=white)](https://paypal.me/mmiyara)

Your support helps maintain this integration. Thank you! ❤️
---

### 🐈 **Multi-Robot Support**

- **Automatic Discovery** - Every Litter-Robot on the account is added automatically
- **Per-Robot Entities** - Each robot gets its own dedicated set of entities
- **Litter-Robot 3 Connect** and **Litter-Robot 4** supported
- **Model-Aware** - Litter-Robot 4 exposes extra controls (litter level, night light mode, panel brightness)

### 🎛️ **Remote Control Entity**

Dedicated remote entity per robot with a UI page and discrete, activity-friendly commands:

#### **UI Page**
- Power On / Power Off
- Start Clean Cycle
- Night Light On / Off
- Panel Lock On / Off
- Sleep Mode On / Off
- Reset Waste Drawer (Litter-Robot 3)

#### **Activity Support**
- **POWER_ON** / **POWER_OFF** simple commands - discrete power control for activity sequences
- **START_CLEAN** simple command - trigger a clean cycle from any activity
- **Full simple-command set** - every action available for custom button mappings

### 🔘 **Button Entities**

- **Clean Cycle** - Start a clean cycle on demand
- **Reset Waste Drawer** - Reset the waste drawer gauge after emptying *(Litter-Robot 3)*

### 🔀 **Switch Entities**

- **Power** - Turn the unit on / off
- **Night Light** - Toggle the night light
- **Panel Lock** - Lock / unlock the control panel buttons
- **Sleep Mode** - Enable / disable scheduled sleep

### 🔽 **Select Entities**

- **Clean Cycle Wait Time** - Minutes to wait after a cat is detected (LR3: 3/7/15, LR4: 3/7/15/25/30)
- **Night Light Mode** - Off / On / Auto *(Litter-Robot 4)*
- **Panel Brightness** - Low / Medium / High *(Litter-Robot 4)*

### 📊 **Sensor Entities**

Real-time monitoring of each robot:

- **Status** - Current operating status (Ready, Clean Cycle In Progress, Cat Detected, Drawer Full, etc.)
- **Waste Drawer** - Approximate waste drawer fill level (%)
- **Litter Level** - Approximate litter level (%) *(Litter-Robot 4)*
- **Cycle Count** - Clean cycles since the waste drawer was last reset
- **Sleep Mode** - Off / Scheduled / Sleeping
- **Sleep Start / Sleep End** - Scheduled sleep window
- **Last Seen** - Last time the robot reported in

### **Connection Requirements**

- **Protocol**: Whisker cloud API (via the [pylitterbot](https://github.com/natekspencer/pylitterbot) library)
- **Authentication**: Whisker account email and password (same as the mobile app)
- **Connection**: Periodic cloud polling for state updates (30-second interval)
- **Internet Access**: Required - the Litter-Robot is a cloud-connected device

### **Network Requirements**

- **Internet Access** - The Remote must have internet access to reach the Whisker cloud
- **Robot Online** - Each Litter-Robot must be connected to Wi-Fi and online in the Whisker app

## Installation

### Option 1: Remote Web Interface (Recommended)
1. Navigate to the [**Releases**](https://github.com/mase1981/uc-intg-whisker/releases) page
2. Download the latest `uc-intg-whisker-<version>-aarch64.tar.gz` file
3. Open your remote's web interface (`http://your-remote-ip`)
4. Go to **Settings** → **Integrations** → **Add Integration**
5. Click **Upload** and select the downloaded `.tar.gz` file

### Option 2: Docker (Advanced Users)

The integration is available as a pre-built Docker image from GitHub Container Registry:

**Image**: `ghcr.io/mase1981/uc-intg-whisker:latest`

**Docker Compose:**
```yaml
services:
  uc-intg-whisker:
    image: ghcr.io/mase1981/uc-intg-whisker:latest
    container_name: uc-intg-whisker
    network_mode: host
    volumes:
      - </local/path>:/data
    environment:
      - UC_CONFIG_HOME=/data
      - UC_INTEGRATION_HTTP_PORT=9090
      - UC_INTEGRATION_INTERFACE=0.0.0.0
      - PYTHONPATH=/app
    restart: unless-stopped
```

**Docker Run:**
```bash
docker run -d --name uc-intg-whisker --restart unless-stopped --network host -v whisker-config:/app/config -e UC_CONFIG_HOME=/app/config -e UC_INTEGRATION_INTERFACE=0.0.0.0 -e UC_INTEGRATION_HTTP_PORT=9090 -e PYTHONPATH=/app ghcr.io/mase1981/uc-intg-whisker:latest
```

## Configuration

### Step 1: Prepare Your Whisker Account

**IMPORTANT**: Your Litter-Robot must already be set up and online in the Whisker mobile app before adding the integration.

#### Verify Your Setup:
1. Confirm each Litter-Robot is connected to Wi-Fi and shows as online in the Whisker app
2. Have your Whisker account email and password ready (the same credentials used in the app)
3. Ensure your Remote has internet access

#### Supported Devices:
**Litter-Robot 3 Connect** - Full support
**Litter-Robot 4** - Full support with additional controls (litter level, night light mode, panel brightness)

### Step 2: Setup Integration

1. After installation, go to **Settings** → **Integrations**
2. The Whisker Litter-Robot integration should appear in **Available Integrations**
3. Click **"Configure"** to begin setup:

#### **Configuration:**
- **Email**: Your Whisker account email
- **Password**: Your Whisker account password
- Click **Next**

The integration validates the account, discovers all Litter-Robots, and creates their entities automatically.

4. Integration will create entities for each robot:
   - **Remote**: `remote.whisker_[account]_[robot]`
   - **Sensors**: Status, Waste Drawer, Litter Level (LR4), Cycle Count, Sleep Mode, Sleep Start/End, Last Seen
   - **Switches**: Power, Night Light, Panel Lock, Sleep Mode
   - **Buttons**: Clean Cycle, Reset Waste Drawer (LR3)
   - **Selects**: Clean Cycle Wait Time, Night Light Mode (LR4), Panel Brightness (LR4)

## Using the Integration

### Remote Control Entity

The remote control entity provides quick access to every robot action through a UI page and exposes discrete simple commands for activities:

- Power On / Off, Start Clean Cycle, Night Light On / Off, Panel Lock On / Off, Sleep Mode On / Off, Reset Waste Drawer

### Activity Integration

Use the discrete **POWER_ON** / **POWER_OFF** and **START_CLEAN** simple commands inside activities for reliable, unambiguous control instead of toggles.

### Sensor Entities

| Sensor | Description |
|--------|-------------|
| Status | Current operating status |
| Waste Drawer | Waste drawer fill level (%) |
| Litter Level | Litter level (%) — Litter-Robot 4 only |
| Cycle Count | Clean cycles since last waste drawer reset |
| Sleep Mode | Off / Scheduled / Sleeping |
| Sleep Start / Sleep End | Scheduled sleep window |
| Last Seen | Last time the robot reported in |

## Known Limitations

- **Cloud Dependency**: The Litter-Robot is a cloud-connected device - an internet connection is required, and state updates are subject to cloud polling (30-second interval).
- **State Polling**: Changes made in the Whisker app or physically on the unit may take a few seconds to reflect on the Remote.
- **Sleep Schedule**: The Remote has no native time entity, so the exact sleep schedule time is shown via read-only sensors; the Sleep Mode switch enables/disables the existing schedule.
- **Litter-Robot 4 Controls**: Litter level, night light mode, and panel brightness are only available on Litter-Robot 4.

## Credits

- **Developer**: Meir Miyara
- **Protocol Library**: [pylitterbot](https://github.com/natekspencer/pylitterbot) by Nathan Spencer
- **Reference Implementation**: [Home Assistant Litter-Robot integration](https://github.com/home-assistant/core/tree/dev/homeassistant/components/litterrobot)
- **Unfolded Circle**: Remote 2/3 integration framework (ucapi)
- **Community**: Testing and feedback from UC community

## License

This project is licensed under the Mozilla Public License 2.0 (MPL-2.0) - see LICENSE file for details.

## Support & Community

- **GitHub Issues**: [Report bugs and request features](https://github.com/mase1981/uc-intg-whisker/issues)
- **UC Community Forum**: [General discussion and support](https://unfolded.community/)
- **Developer**: [Meir Miyara](https://www.linkedin.com/in/meirmiyara)

---

**Made with ❤️ for the Unfolded Circle and Whisker Communities**

**Thank You**: Meir Miyara
