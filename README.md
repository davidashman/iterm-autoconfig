# iterm-autoconfig

An [oh-my-zsh](https://ohmyz.sh) plugin that automatically applies iTerm2 profile settings when you change directories. Place a `.iterm.json` file in any project root and your terminal will update its colors, badge, and title whenever you `cd` into that project.

## Features

- Sets tab color, background color, badge text, and window title per-project
- Walks up the directory tree to find the nearest `.iterm.json`
- Resets to your default iTerm2 profile when leaving a configured directory
- Sets the default working directory for new splits and tabs to the project root
- Uses a persistent background daemon to eliminate per-`cd` startup latency

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
  "title": "My Project",
  "background_color": "#1e1e2e",
  "tab_color": "#ff0000",
  "badge": "my-project"
}
```

All fields are optional. Unset fields reset to your default iTerm2 profile values when entering a directory with a config, and all fields reset when leaving all configured directories.

| Field | Description |
|---|---|
| `title` | Window/tab title |
| `background_color` | Terminal background color (hex) |
| `tab_color` | Tab color (hex) |
| `badge` | Badge text (displayed in the top-right of the terminal) |

## How it works

On shell startup, a daemon is launched that maintains a persistent connection to the iTerm2 Python API. When you `cd`, the plugin sends the config directory path to the daemon over a Unix socket (`~/.iterm-autoconfig.sock`) — just a socket write, no Python startup overhead. If the daemon is not running, the plugin falls back to direct execution and automatically restarts the daemon.
