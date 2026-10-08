---
title: Remote access to your computers
subtitle: Tailscale, Sunshine, and Moonlight, and the setup skill that installs them
---

# Remote access to your computers

## 1. What this document tells you

This document explains a setup that lets you use one of your computers from a different device. For example, you can use your desktop computer at home from your laptop in a hotel.

The setup has three parts: Tailscale, Sunshine, and Moonlight. This document tells you what each part is, why the setup is safe, and what the setup skill does on your computers.

## 2. The three parts

| Part | Where it runs | What it does |
|---|---|---|
| **Tailscale** | On all of your devices | Makes a private network that only your devices can use. |
| **Sunshine** | On the *host*: the computer that you want to control | Sends the screen of the host as a video stream. Receives keyboard and mouse input. |
| **Moonlight** | On the *client*: the device in front of you | Shows the video stream from the host. Sends your keyboard and mouse input to the host. |

Tailscale connects the devices. Sunshine and Moonlight use that connection to show the host screen on the client.

## 3. Tailscale

### 3.1 What Tailscale is

Tailscale is a private network for your own devices. It is also known as a "mesh VPN". When a device is on your Tailscale network, it gets a private address that starts with `100.`. Your other devices use this address to connect to it.

The connection operates from any location. The devices can be in your home, in an office, on a mobile network, or in a hotel.

### 3.2 How Tailscale works

Tailscale uses WireGuard, an open-source encryption protocol. Each device makes its own pair of encryption keys: a private key and a public key. The private key never goes off the device.

A Tailscale coordination server gives each device the public keys of your other devices. The coordination server does not receive the private keys. Your network traffic does not go through the coordination server.

The devices then send data directly to each other, when the networks between them permit this. When a direct connection is not possible, Tailscale sends the encrypted data through a relay server. The relay server cannot decrypt the data, because it does not have the private keys.

### 3.3 Why Tailscale is safe

- **No open ports.** You do not open ports on your router. Thus, a computer on the internet cannot connect to Sunshine on the host.
- **Encryption on all traffic.** WireGuard encrypts all traffic between your devices, including the video stream.
- **Only your devices.** A device can join your network only after a person signs in with your account.
- **Your own sign-in.** You sign in with an account that you already have, for example Google, Microsoft, Apple, or GitHub. If that account uses two-factor authentication, your network gets the same protection.
- **You can remove a device.** In the Tailscale admin console, you can remove a lost or stolen device from your network immediately.
- **Open-source client.** The Tailscale software on your devices is open source. Security researchers can examine it.

### 3.4 What Tailscale can see, and the risks that stay

Tailscale operates the coordination server. Thus, Tailscale knows the names of your devices, their Tailscale addresses, and when they connect. Tailscale cannot see the contents of your traffic.

Your account is the key to your network. If a different person gets access to your sign-in account, that person can add a device to your network. Use a strong password and two-factor authentication on the account that you use for Tailscale.

## 4. Sunshine

### 4.1 What Sunshine is

Sunshine is open-source streaming software from the LizardByte project. You install it on the host. Sunshine records the screen of the host and encodes it as a video stream. When a graphics card is available, Sunshine uses the graphics card for this work.

Sunshine also receives keyboard, mouse, and game-controller input from Moonlight. It gives this input to the host. Thus, you control the host as if you sat in front of it.

### 4.2 The Sunshine settings page

Sunshine has a settings page in a web browser on the host: `https://localhost:47990`. You choose a Sunshine username and password the first time that you open this page. By default, Sunshine does not permit access to this page from the internet. The page also asks for your Sunshine username and password.

### 4.3 Pairing

Sunshine does not accept a stream request from an unknown device. Each Moonlight device must first be "paired" with Sunshine one time:

1. Moonlight shows a 4-digit PIN.
2. On the host, type this PIN on the Sunshine settings page.
3. Sunshine then accepts that one Moonlight device.

A device that is not paired cannot see the host screen, even when it is on your Tailscale network.

## 5. Moonlight

Moonlight is open-source software that receives a stream from Sunshine. You install it on the client. It is available for Windows, macOS, Linux, iPhone, iPad, Android, and other platforms.

Moonlight shows the host screen in a window or on the full screen. The Moonlight developers made it for game streaming. Thus, the delay between your input and the screen change is small.

## 6. How the parts operate together

When you connect from the client to the host, this sequence occurs:

1. Moonlight on the client sends a request to the Tailscale address of the host.
2. Tailscale finds the host and makes an encrypted connection between the two devices.
3. Sunshine on the host makes sure that the client is a paired device.
4. Sunshine sends the host screen to Moonlight as a video stream.
5. Moonlight sends your keyboard and mouse input back to Sunshine.

All of this traffic goes through the encrypted Tailscale connection.

## 7. What the setup skill does

The setup skill is a set of instructions for Claude Code. You run the skill one time on each computer. On a phone or tablet, you only install two apps.

The skill does these tasks:

1. It asks if the computer is a host, a client, or both.
2. It finds the operating system and the software that the computer has already.
3. It installs Tailscale and starts the sign-in.
4. On a host, it installs Sunshine and sets Sunshine to start automatically.
5. On a client, it installs Moonlight and connects Moonlight to the Tailscale address of the host.
6. It helps you through the pairing PIN.
7. It makes sure that the client can connect to the host.
8. It gives you a summary of your devices and the tasks that are not complete.

On a host, the skill also tells you about these items. It asks you before it changes them:

- **A monitor.** Sunshine records the image on a monitor. If the host has no monitor, Sunshine has nothing to send. A monitor that is off, a dummy monitor plug, or a virtual monitor driver solves this problem.
- **Automatic sign-in.** After a restart, Sunshine needs a signed-in desktop. Automatic sign-in gives this, but it decreases the security of the host. You decide.
- **Sleep.** If the host sleeps, you cannot connect to it. You can set the host to never sleep, or you can set up Wake-on-LAN.
- **Remote Desktop.** Windows Remote Desktop and Sunshine use the same desktop session. The skill tells you not to use them at the same time.
- **Key expiry.** By default, Tailscale asks each device to sign in again after a period. For a host, you can turn off key expiry in the Tailscale admin console.

## 8. What the skill does not do

- It does not see or keep your passwords. You type all passwords into Tailscale and Sunshine yourself.
- It does not open ports on your router.
- It does not change the security settings of a host without your approval.

## 9. What you do yourself

1. Sign in to Tailscale on each device. Use the same account on all of them.
2. Choose a Sunshine username and password on the host.
3. Type the pairing PIN on the host.
4. Decide about automatic sign-in, sleep, and key expiry on the host.

## 10. Daily use

1. Open Moonlight on the client.
2. Click the name of the host.
3. Click **Desktop**.

If Moonlight cannot connect, do these checks in this order:

1. Make sure that Tailscale shows "Connected" on the client and on the host.
2. Make sure that the host is on and not asleep.
3. Make sure that a user session is open on the host.
4. Make sure that the host has a monitor or a dummy monitor plug.
5. Make sure that Sunshine operates on the host.

## 11. Terms

| Term | Meaning in this document |
|---|---|
| Host | The computer that you control from a different location. Sunshine runs on it. |
| Client | The device in front of you. Moonlight runs on it. |
| Tailscale network | The private network of your devices. Also known as a "tailnet". |
| Tailscale address | The private address of a device on your Tailscale network. It starts with `100.`. |
| Coordination server | The Tailscale server that gives each device the public keys of your other devices. |
| Pairing | The one-time step that lets one Moonlight device connect to one Sunshine host. |
| Sign in | To prove your identity to Tailscale, or to start a user session on a computer. |

---

*About this document: Claude (an AI model) drafted this document in ASD-STE100 Simplified Technical English style. Claude checked the vocabulary against known rules and high-risk patterns only, not against the official ASD-STE100 dictionary. A person must review and approve the content before a client receives it.*
