---
name: remote-access-setup
description: Use when the user wants to reach or control their computers from anywhere, set up Tailscale, Sunshine, or Moonlight, stream a desktop to a laptop/phone/tablet, or "set up remote access" / "let me use my desktop from my laptop" / "connect my machines". Sets up the private network (Tailscale) on every device, the streaming host (Sunshine) on the machine to be controlled, and the client (Moonlight) on the devices that connect. Windows, macOS, Linux; Moonlight also on iOS/Android.
---

# Remote access setup: Tailscale + Sunshine + Moonlight

Three pieces, each with one job:
- **Tailscale**: a private network between the person's own devices. Nothing is exposed to the internet.
- **Sunshine** (the *host*): runs on the computer that gets controlled, and streams its screen.
- **Moonlight** (the *client*): runs on the device the person sits at, and shows that screen.

Do every step yourself on the machine you are running on. Stop only for things that need
the person: a browser sign-in, a UAC/sudo prompt, a PIN, a password they choose, or a choice.
Never ask them to paste passwords or keys to you. They type those into the program directly.

## 0. Ask two questions first

1. **What is this machine?** The *host* (to be controlled), a *client* (to control from), or both?
2. **Which other devices are part of the setup?** For example "desktop at home + MacBook + iPad".

Run this skill once on each computer. Phones and tablets only need the Tailscale and
Moonlight apps from their app store (step 5).

## 1. Detect the machine

OS and version, admin rights, whether `tailscale`, `sunshine`, and `moonlight` are already
installed. On Windows also run `winget --version`. On macOS run `brew --version`.

## 2. Tailscale (every device)

| OS | Install |
|---|---|
| Windows | `winget install --id Tailscale.Tailscale -e` |
| macOS | `brew install --cask tailscale-app` (or the App Store "Tailscale") |
| Linux | `curl -fsSL https://tailscale.com/install.sh \| sh` then `sudo systemctl enable --now tailscaled` |

Sign in: run `tailscale up`. On Windows and macOS the app opens a sign-in window. The person
signs in **with the same account on every device**. That account is what puts the devices
on one private network. Then:
- `tailscale status`: every device of theirs that is already set up shows in the list.
- `tailscale ip -4`: write down this machine's `100.x.y.z` address and its name. The
  client uses them in step 4.
- Recommend they turn on MagicDNS in the admin console (https://login.tailscale.com/admin/dns),
  so devices can be reached by name instead of by number.
- **Host machines only:** recommend disabling key expiry for this machine
  (admin console → Machines → ⋯ → Disable key expiry). If they don't, the host drops off the
  network every ~180 days until someone signs in at the keyboard.

## 3. Sunshine (host only)

### Install
| OS | Install |
|---|---|
| Windows | `winget install --id LizardByte.Sunshine -e` (installs and starts the `SunshineService` service) |
| Linux | Download the `.deb` / `.rpm` / AppImage for this distro from https://github.com/LizardByte/Sunshine/releases/latest, or `flatpak install flathub dev.lizardbyte.app.Sunshine`. Then follow the release notes' post-install steps (udev rule for `uinput`, `setcap` for KMS capture), and enable it: `systemctl --user enable --now sunshine` |
| macOS | Sunshine on macOS is experimental. Recommend using the Mac as a **client**. Install only if they insist: `brew tap LizardByte/homebrew && brew install sunshine` |

### Web UI login
The person chooses a Sunshine username and password. Have them set it themselves, either by
opening **https://localhost:47990** in a browser (accept the self-signed certificate warning)
or by running `sunshine --creds <user> <password>` in their own terminal. (On Windows,
Sunshine is at `C:\Program Files\Sunshine\sunshine.exe`.) Do not take the password yourself.

### Make it work unattended (read each point and ask before changing anything)
- **Something to stream:** Sunshine captures a real display. A host with no monitor plugged in
  streams nothing. Options: keep a monitor connected (it can be switched off), use an HDMI/DP
  dummy plug (~$8), or install a virtual display driver
  (Windows: https://github.com/VirtualDrivers/Virtual-Display-Driver).
- **Multiple monitors:** Sunshine may switch the host to one screen while streaming, and the
  other screens can stay dark after disconnect. If that happens, setting the display to
  "Extend" (Windows: Win+P) brings them back.
- **After a reboot:** Sunshine needs a logged-in desktop. To reach the machine after it
  restarts unattended, the person can enable automatic sign-in. This is a security trade-off,
  so explain it and let them decide. Windows: `netplwiz` (or Sysinternals Autologon).
  Linux: their display manager's autologin setting.
- **Sleep:** set the host to never sleep, or set up Wake-on-LAN. WoL also needs the BIOS
  settings "Resume by PCI-E device = Enabled" and "ErP Ready = Disabled", plus another
  always-on device on the same LAN to send the wake packet. Treat WoL as optional extra work.
- **Don't run RDP at the same time.** Windows Remote Desktop takes over the console session
  that Sunshine streams.
- **Firewall:** the installer opens Sunshine's ports. Do not forward any ports on the router.
  Tailscale makes that unnecessary, and port forwarding would expose the host to the internet.

### Check
- Windows: `Get-Service SunshineService` shows Running / Automatic.
- Linux: `systemctl --user status sunshine`.
- The web UI loads at https://localhost:47990 after login.

## 4. Moonlight (client only)

| OS | Install |
|---|---|
| Windows | `winget install --id MoonlightGameStreamingProject.Moonlight -e` |
| macOS | `brew install --cask moonlight` |
| Linux | `flatpak install flathub com.moonlight_stream.Moonlight` |
| iPhone / iPad / Android | "Moonlight Game Streaming" from the App Store / Play Store |

### Pair (one time per client and host pair)
1. Make sure Tailscale is connected on both machines (`tailscale status` shows the host).
2. In Moonlight: **Add PC (+)**, and enter the host's Tailscale IP from step 2 (or its MagicDNS
   name). Moonlight on the LAN may find the host automatically. Over Tailscale, add it by IP.
3. Moonlight shows a 4-digit PIN. On the host, open https://localhost:47990 → **PIN** tab,
   enter the PIN and a name for this device. (If you are running on the host and the person
   gives you the PIN, you may submit it through the web UI together with them.)
4. Click **Desktop** in Moonlight. The host's screen appears.

Suggested settings for streaming over the internet: start at 1080p60, 20 Mbps. Go higher on
a good connection.

## 5. Phones and tablets

Install the **Tailscale** app, sign in with the same account, then install **Moonlight** and
pair as in step 4. Nothing else is needed.

## 6. Verify and hand off

On a client:
- `tailscale ping <host-name-or-ip>` succeeds.
- Moonlight connects and shows the desktop.

Finish with a short plain summary for the person:
- every device and its Tailscale address
- which machine is the host
- what is still to do (PINs, disabling key expiry, a dummy plug, autologin)
- how to connect from now on: "open Moonlight → click your PC → Desktop"

Give the person the plain-language explainer in this skill's folder:
`explainer/remote-access-explained.pdf`. It covers what Tailscale, Sunshine, and Moonlight
are, why the setup is safe, and what this skill did. (Source: `explainer/remote-access-explained.md`,
written in ASD-STE100 style. Rebuild the PDF with `python explainer/build_pdf.py` after edits.)

If it doesn't connect, check in this order: is Tailscale up on both ends (`tailscale status`)?
Is Sunshine running on the host? Is the host awake and logged in? Is a display attached?
