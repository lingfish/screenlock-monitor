# Screen Saver Monitor

A Python script that monitors screen saver activity and executes custom commands when the screen locks or unlocks.

## Features

- Monitors screen saver state using D-Bus (Linux)
- Executes custom commands on lock/unlock events
- Debounce mechanism to prevent duplicate events
- Multiple configuration options:
  - Command-line arguments (`-l`, `--lock-command`, `-u`, `--unlock-command`)
  - Environment variables (`LOCK_COMMAND`, `UNLOCK_COMMAND`)
  - Default commands if none specified

## Requirements

- Python 3.x
- D-Bus (Linux)
- GLib/GIO (typically installed with gobject-introspection)

## Installation

No installation required - just run the script directly.

## Usage

### Command-line Arguments

```bash
python3 screen_saver_monitor.py -l <lock_command> -u <unlock_command>
```

- `-l, --lock-command`: Command to run when screen is locked
- `-u, --unlock-command`: Command to run when screen is unlocked

### Environment Variables

```bash
export LOCK_COMMAND="your_lock_command"
export UNLOCK_COMMAND="your_unlock_command"
python3 screen_saver_monitor.py
```

### Default Behavior

If no arguments or environment variables are provided, the script will use default commands:
- Lock command: `echo locked`
- Unlock command: `echo unlocked`

## Example

Lock your screen and execute a custom command:

```bash
python3 screen_saver_monitor.py -l "echo 'Screen locked!'" -u "echo 'Screen unlocked!'"
```

Monitor screen saver and log to a file:

```bash
python3 screen_saver_monitor.py -l "logger 'Screen locked'" -u "logger 'Screen unlocked'"
```

## License

MIT License - feel free to use this script for your projects.