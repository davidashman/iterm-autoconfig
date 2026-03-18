# iterm-autoconfig

An [oh-my-zsh](https://ohmyz.sh) plugin that automatically applies iTerm2 profile settings when you change directories. Place a `.iterm.json` file in any project root and your terminal will update its colors, badge, and title whenever you `cd` into that project.

## Features

- Sets tab color, background color, badge text, and window title per-project
- Walks up the directory tree to find the nearest `.iterm.json`
- Resets to your default iTerm2 profile when leaving a configured directory
- Sets the default working directory for new splits and tabs to the project root
- Runs lightweight and stateless — no background daemon or socket required

## Requirements

- [iTerm2](https://iterm2.com) with Python API enabled (**iTerm2 → Preferences → General → Magic → Enable Python API**)
- Python 3
- `iterm2` Python package:
  ```sh
  pip3 install iterm2
  ```

## Installation

### oh-my-zsh

Clone into your custom plugins directory:

```sh
git clone https://github.com/davidashman/iterm-autoconfig \
  ${ZSH_CUSTOM:-~/.oh-my-zsh/custom}/plugins/iterm-autoconfig
```

Then add `iterm-autoconfig` to the plugins list in your `~/.zshrc`:

```sh
plugins=(... iterm-autoconfig)
```

Reload your shell:

```sh
source ~/.zshrc
```

## Configuration

Create a `.iterm.json` file in any directory:

```json
{
  "subtitle": "My Project",
  "background_color": "#1e1e2e",
  "tab_color": "#ff0000",
  "badge": "my-project"
}
```

All fields are optional. Unset fields reset to your default iTerm2 profile values when entering a directory with a config, and all fields reset when leaving all configured directories.

| Field | Description |
|---|---|
| `subtitle` | Subtitle displayed below the main window/tab title |
| `background_color` | Terminal background color (hex) |
| `tab_color` | Tab color (hex) |
| `badge` | Badge text (displayed in the top-right of the terminal) |

## How it works

The plugin hooks into zsh's `chpwd` event, which fires whenever you change directories. On each `cd`, it walks up the directory tree looking for the nearest `.iterm.json`, then spawns `apply_iterm_config.py` in the background with the config path. The script connects to the iTerm2 Python API, applies the settings to the current session, and exits.
