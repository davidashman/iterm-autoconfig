#!/usr/bin/env python3
import asyncio
import iterm2
import json
import os
import sys

SOCKET_PATH = os.path.expanduser("~/.iterm-autoconfig.sock")
CONFIG_FILE = ".iterm.json"

def hex_to_rgb(h):
    h = h.lstrip('#')
    return tuple(int(h[i:i+2], 16) for i in (0, 2, 4))

async def apply_changes(connection, config_dir):
    if config_dir:
        with open(os.path.join(config_dir, CONFIG_FILE)) as f:
            config = json.load(f)
    else:
        config = {}

    app = await iterm2.async_get_app(connection)
    session = app.current_terminal_window.current_tab.current_session
    default_profile = await iterm2.Profile.async_get_default(connection)
    change = iterm2.LocalWriteOnlyProfile()

    if "background_color" in config:
        rgb = hex_to_rgb(config["background_color"])
        change.set_background_color(iterm2.Color(rgb[0], rgb[1], rgb[2]))
    elif default_profile.background_color is not None:
        change.set_background_color(default_profile.background_color)

    if "tab_color" in config:
        rgb = hex_to_rgb(config["tab_color"])
        change.set_use_tab_color(True)
        change.set_tab_color(iterm2.Color(rgb[0], rgb[1], rgb[2]))
    else:
        change.set_use_tab_color(default_profile.use_tab_color)
        if default_profile.tab_color is not None:
            change.set_tab_color(default_profile.tab_color)

    if "badge" in config:
        change.set_badge_text(config["badge"])
    else:
        change.set_badge_text(default_profile.badge_text or "")

    if "title" in config:
        change.set_subtitle(config["title"])
    else:
        change.set_subtitle(default_profile.subtitle or "")

    if config_dir:
        change.set_initial_directory_mode(iterm2.InitialWorkingDirectory.INITIAL_WORKING_DIRECTORY_CUSTOM)
        change.set_custom_directory(config_dir)
    else:
        change.set_initial_directory_mode(iterm2.InitialWorkingDirectory.INITIAL_WORKING_DIRECTORY_HOME)

    await session.async_set_profile_properties(change)

async def handle_client(connection, reader, writer):
    try:
        data = await reader.readline()
        config_dir = data.decode().strip()
        await apply_changes(connection, config_dir)
    except Exception:
        pass
    finally:
        writer.close()
        try:
            await writer.wait_closed()
        except Exception:
            pass

async def daemon_main(connection):
    if os.path.exists(SOCKET_PATH):
        os.unlink(SOCKET_PATH)
    server = await asyncio.start_unix_server(
        lambda r, w: handle_client(connection, r, w),
        SOCKET_PATH
    )
    async with server:
        await server.serve_forever()

async def direct_main(connection):
    config_dir = sys.argv[1] if len(sys.argv) > 1 else ""
    await apply_changes(connection, config_dir)

if '--daemon' in sys.argv:
    iterm2.run_forever(daemon_main)
else:
    iterm2.run_until_complete(direct_main)
