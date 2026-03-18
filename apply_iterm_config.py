#!/usr/bin/env python3
import colorsys
import hashlib
import iterm2
import json
import os
import subprocess
import sys

CONFIG_FILE = ".iterm.json"
GLOBAL_CONFIG_FILE = os.path.expanduser("~/.iterm.json")

def hex_to_rgb(h):
    h = h.lstrip('#')
    return tuple(int(h[i:i+2], 16) for i in (0, 2, 4))

def repo_color(name):
    hue = int(hashlib.md5(name.encode()).hexdigest(), 16) % 360
    r, g, b = colorsys.hls_to_rgb(hue / 360, 0.40, 0.45)
    return int(r * 255), int(g * 255), int(b * 255)

def git_info(cwd):
    try:
        root = subprocess.check_output(
            ['git', 'rev-parse', '--show-toplevel'],
            cwd=cwd, stderr=subprocess.DEVNULL
        ).decode().strip()
        branch = subprocess.check_output(
            ['git', 'rev-parse', '--abbrev-ref', 'HEAD'],
            cwd=cwd, stderr=subprocess.DEVNULL
        ).decode().strip()
        return os.path.basename(root), branch
    except (subprocess.CalledProcessError, FileNotFoundError):
        return None, None

async def apply_changes(connection):
    config_dir = sys.argv[1] if len(sys.argv) > 1 else ""
    cwd = sys.argv[2] if len(sys.argv) > 2 else os.getcwd()

    if config_dir:
        with open(os.path.join(config_dir, CONFIG_FILE)) as f:
            config = json.load(f)
        repo_name, branch = None, None
    else:
        config = {}
        global_config = {}
        if os.path.exists(GLOBAL_CONFIG_FILE):
            with open(GLOBAL_CONFIG_FILE) as f:
                global_config = json.load(f)
        repo_name, branch = git_info(cwd) if global_config.get("git") else (None, None)

    app = await iterm2.async_get_app(connection)
    session = app.current_terminal_window.current_tab.current_session
    default_profile = await iterm2.Profile.async_get_default(connection)
    change = iterm2.LocalWriteOnlyProfile()

    if "background_color" in config:
        rgb = hex_to_rgb(config["background_color"])
        change.set_background_color(iterm2.Color(*rgb))
    elif default_profile.background_color is not None:
        change.set_background_color(default_profile.background_color)

    if "tab_color" in config:
        rgb = hex_to_rgb(config["tab_color"])
        change.set_use_tab_color(True)
        change.set_tab_color(iterm2.Color(*rgb))
    elif repo_name:
        change.set_use_tab_color(True)
        change.set_tab_color(iterm2.Color(*repo_color(repo_name)))
    else:
        change.set_use_tab_color(default_profile.use_tab_color)
        if default_profile.tab_color is not None:
            change.set_tab_color(default_profile.tab_color)

    if "badge" in config:
        change.set_badge_text(config["badge"])
    elif repo_name:
        change.set_badge_text(repo_name)
    else:
        change.set_badge_text(default_profile.badge_text or "")

    if "subtitle" in config:
        change.set_subtitle(config["subtitle"])
    elif repo_name:
        change.set_subtitle(f"{repo_name} · {branch}" if branch else repo_name)
    else:
        change.set_subtitle(default_profile.subtitle or "")

    if config_dir:
        change.set_initial_directory_mode(iterm2.InitialWorkingDirectory.INITIAL_WORKING_DIRECTORY_CUSTOM)
        change.set_custom_directory(config_dir)
    else:
        change.set_initial_directory_mode(iterm2.InitialWorkingDirectory.INITIAL_WORKING_DIRECTORY_HOME)

    await session.async_set_profile_properties(change)

iterm2.run_until_complete(apply_changes)
