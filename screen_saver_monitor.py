import dbus
import subprocess
import os
import argparse
from dbus.mainloop.glib import DBusGMainLoop
from gi.repository import GLib

# Default commands if not specified via CLI args or environment variables
DEFAULT_LOCK_COMMAND = 'echo locked'
DEFAULT_UNLOCK_COMMAND = 'echo unlocked'

last_state = None

def on_screen_active_changed(value):
    global last_state

    # Ignore if state hasn't changed since last action
    if last_state == value:
        return

    print(f"Screen active status: {value}")

    if not value:  # Screen saver inactive = screen unlocked
        subprocess.run(unlock_command, shell=True)
        last_state = value
    else:  # Screen saver active = screen locked
        subprocess.run(lock_command, shell=True)
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

    args = parser.parse_args()

    # Determine commands: CLI args take precedence, then environment variables, then defaults
    if args.lock_command:
        lock_command = args.lock_command
    elif 'LOCK_COMMAND' in os.environ:
        lock_command = os.environ['LOCK_COMMAND']
    else:
        lock_command = DEFAULT_LOCK_COMMAND

    if args.unlock_command:
        unlock_command = args.unlock_command
    elif 'UNLOCK_COMMAND' in os.environ:
        unlock_command = os.environ['UNLOCK_COMMAND']
    else:
        unlock_command = DEFAULT_UNLOCK_COMMAND

    # Initialize the D-Bus main loop
    DBusGMainLoop(set_as_default=True)

    # Connect to the D-Bus session bus
    bus = dbus.SessionBus()

    # Get the ScreenSaver interface
    obj = bus.get_object("org.freedesktop.ScreenSaver", "/ScreenSaver")
    interface = dbus.Interface(obj, "org.freedesktop.ScreenSaver")

    # Connect to the ActiveChanged signal
    interface.connect_to_signal("ActiveChanged", on_screen_active_changed)

    # Run the main loop
    loop = GLib.MainLoop()
    loop.run()