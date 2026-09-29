---
name: notebooklm-pack-setup
description: Use when connecting NotebookLM to this machine for the first time or repairing the connection - "set up NotebookLM", "connect my Google account to NotebookLM packs", "notebooklm login isn't working", "switch the NotebookLM account" - or when notebooklm-pack reports the CLI missing or not logged in (push_pack.py exit code 2 or 3). Installs the notebooklm-py CLI, has the user sign in with their own Google account, and verifies the connection.
allowed-tools: Read Bash PowerShell
model: fast
---

# NotebookLM Pack — Setup

Connects `notebooklm-pack` to the NotebookLM account of the person at the
keyboard, so packs can be pushed instead of dragged in by hand.

**Core principle:** the account is always the user's own. Nothing ships with
this plugin that points at any account. The session is created by the user
signing in, and it is stored only on their machine under `~/.notebooklm/`.

Setup is optional. `notebooklm-pack` works without it; the user just uploads
the pack files by hand.

## When to Use

- First push on a machine, or `push_pack.py --check` does not say `Ready to push`
- The session expired (pushes that used to work now fail auth)
- The user wants packs to go to a different Google account

## When NOT to Use

- The user only wants the manual drag-in path. No setup needed
- The user has NotebookLM Enterprise and wants the official API. That is a
  Google Cloud setup, not this CLI

## Say this first

Before installing anything, tell the user in plain terms:

- The push path uses `notebooklm-py`, an **unofficial** tool. It drives the
  NotebookLM web app with their own browser session. Google can change
  things and break it, and automating a consumer product is a
  terms-of-service gray area.
- Their session cookies are saved on this machine. Anyone with access to
  their user account on this machine could use them.

Proceed only if they say yes. If they decline, stop and point them to the
manual drag-in steps in `notebooklm-pack`.

## Steps

`<pack_skill_dir>` is the `notebooklm-pack` skill folder, a sibling of this one.

### 1. Check the current state

```
python <pack_skill_dir>/scripts/push_pack.py --check
```

| Exit | Meaning | Next |
|---|---|---|
| 0 | Installed and logged in | Go to step 4 to confirm the account |
| 3 | CLI not installed | Step 2 |
| 2 | Not logged in or expired | Step 3 |

### 2. Install the CLI

Requires Python 3.10 or newer.

```
pip install --user "notebooklm-py[browser]"
```

Add the `cookies` extra only if the user picks the browser-cookie login in
step 3: `pip install --user "notebooklm-py[browser,cookies]"`.

The interactive login uses a Playwright browser. If login later reports a
missing browser, run `python -m playwright install chromium`.

### 3. The user signs in

The user does this step. Give them the command to run in their own terminal
(in Claude Code, prefixed with `!` so it runs in the session). Never ask for,
type, or store a Google password.

**Default: interactive login.** Opens a browser window; they sign in; the
session saves itself.

```
notebooklm login
```

If the bundled browser crashes or their organization requires a specific
one: `notebooklm login --browser chrome` or `--browser msedge`.

**Alternative: reuse an existing browser session.** Less friction, but it
reads cookies from their browser, so ask first.

```
notebooklm login --browser-cookies chrome
```

If several Google accounts are signed in to that browser, have the user name
the one to use. Do not pick for them.

```
notebooklm auth inspect
notebooklm login --browser-cookies chrome --account <their-email>
```

### 4. Verify, and confirm the account

```
python <pack_skill_dir>/scripts/push_pack.py --check
```

It must end with `Ready to push`. Then have the user confirm the account is
the one they intend by listing their notebooks:

```
notebooklm list
```

They should recognize the notebooks (or see an empty list on a new account).
If they see someone else's notebooks, the machine holds another person's
session. Go to "Switching accounts".

### 5. Hand back

Tell the user setup is done and return to `notebooklm-pack`. The first real
push still starts with `--dry-run`.

## Switching accounts

One Google account per profile.

```
notebooklm login --fresh              # replace the account in the active profile
notebooklm profile create <name>      # or keep both, one profile each
notebooklm -p <name> login
```

Push to a specific profile with `push_pack.py <pack_dir> --profile <name>`.

## Disconnecting

```
notebooklm auth logout
```

This clears the saved session on this machine. Notebooks already created
stay in the user's NotebookLM account.

## Anti-Patterns

| Anti-pattern | Why it fails | Fix |
|---|---|---|
| Asking the user for their Google password or a 2FA code | Credentials never pass through the assistant | The user signs in through the browser window |
| Running a login for the user without telling them what it does | They did not consent to storing a session | Say-this-first, then let them run it |
| Skipping the account confirmation | Packs land in the wrong account on shared machines | Step 4, every time |
| Picking an account from `auth inspect` yourself | It is the user's choice | Ask which email |
| Using `--all-accounts` | Pulls every signed-in Google account into profiles | Log in one named account |
| Copying `~/.notebooklm/` between machines or into a repo | It is a live session for a Google account | Log in fresh on each machine; never commit it |
| Printing or pasting the contents of `storage_state.json` | Those are session cookies | Use `--check`; it reports status only |
| Calling the CLI an official Google integration | It is not | State that it is unofficial and can break |
| Blocking the pack on setup failure | The pack is still usable | Fall back to manual drag-in |

## Cross-References

- `notebooklm-pack`: the skill this one serves. It sends users here when
  `--check` fails.
- `security-testing`: if the user asks what the stored session exposes.
