#!/usr/bin/env python3

import logging
import dbus
import subprocess
import os
import argparse
from dbus.mainloop.glib import DBusGMainLoop
from gi.repository import GLib

# Default commands if not specified via CLI args or environment variables
DEFAULT_LOCK_COMMAND = 'echo locked'
DEFAULT_UNLOCK_COMMAND = 'echo unlocked'

# Configure logging
logger = logging.getLogger(__name__)

last_state = None

def on_screen_active_changed(value):
    global last_state

    # Ignore if state hasn't changed since last action
    if last_state == value:
        return

    logger.info(f"Screen active status changed to: {value}")

    if not value:  # Screen saver inactive = screen unlocked
        logger.info(f"Executing unlock command: {unlock_command}")
        result = subprocess.run(unlock_command, shell=True)
        if result.returncode != 0:
            logger.error(f"Unlock command failed with return code: {result.returncode}")
        last_state = value
    else:  # Screen saver active = screen locked
        logger.info(f"Executing lock command: {lock_command}")
        result = subprocess.run(lock_command, shell=True)
        if result.returncode != 0:
            logger.error(f"Lock command failed with return code: {result.returncode}")
        last_state = value

if __name__ == "__main__":
    # Parse CLI arguments
    parser = argparse.ArgumentParser(
        description="Monitor screen saver activity and execute commands on lock/unlock."
    )
    parser.add_argument(
        '-l', '--lock-command',
        help='Command to run when screen is locked'
    )
    parser.add_argument(
        '-u', '--unlock-command',
        help='Command to run when screen is unlocked'
    )
    parser.add_argument(
        '-v', '--verbose',
        action='store_true',
        help='Enable verbose output'
    )

    args = parser.parse_args()

    # Configure logging level
    log_level = logging.DEBUG if args.verbose else logging.INFO
    logging.basicConfig(
        level=log_level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )

    logger.info("Screenlock Monitor starting...")

    # Determine commands: CLI args take precedence, then environment variables, then defaults
    if args.lock_command:
        lock_command = args.lock_command
        logger.info(f"Using lock command from CLI argument: {lock_command}")
    elif 'LOCK_COMMAND' in os.environ:
        lock_command = os.environ['LOCK_COMMAND']
        logger.info(f"Using lock command from environment variable: {lock_command}")
    else:
        lock_command = DEFAULT_LOCK_COMMAND
        logger.info(f"Using default lock command: {lock_command}")

    if args.unlock_command:
        unlock_command = args.unlock_command
        logger.info(f"Using unlock command from CLI argument: {unlock_command}")
    elif 'UNLOCK_COMMAND' in os.environ:
        unlock_command = os.environ['UNLOCK_COMMAND']
        logger.info(f"Using unlock command from environment variable: {unlock_command}")
    else:
        unlock_command = DEFAULT_UNLOCK_COMMAND
        logger.info(f"Using default unlock command: {unlock_command}")

    # Initialize the D-Bus main loop
    DBusGMainLoop(set_as_default=True)
    logger.info("Initialized D-Bus main loop")

    # Connect to the D-Bus session bus
    bus = dbus.SessionBus()
    logger.info("Connected to D-Bus session bus")

    # Get the ScreenSaver interface
    obj = bus.get_object("org.freedesktop.ScreenSaver", "/ScreenSaver")
    interface = dbus.Interface(obj, "org.freedesktop.ScreenSaver")
    logger.info("Connected to ScreenSaver interface")

    # Connect to the ActiveChanged signal
    interface.connect_to_signal("ActiveChanged", on_screen_active_changed)
    logger.info("Connected to ActiveChanged signal")

    # Run the main loop
    logger.info("Starting main event loop")
    loop = GLib.MainLoop()
    try:
        loop.run()
    except KeyboardInterrupt:
        logger.info("Received keyboard interrupt, shutting down...")
        loop.quit()
    except Exception as e:
        logger.error(f"Unexpected error: {e}", exc_info=True)
    finally:
        logger.info("Screenlock Monitor stopped")