# DJ Track User Guide

## Overview

DJ Track is a Python-based tool for managing track music libraries and DJing. 

It includes:

- A GUI mode for interactive browsing and playback (`djtango/DJTango.py`)
- A CLI mode for database initialization, scanning, and library inspection (`tools/djtango_cli.py`)
- A SQLite-backed local database stored in `~/.djtango`

At the moment, the project is designed to run from a Python virtual environment.

---

## What You Can Do

### GUI mode

- Browse track songs
- Play tracks
- Scan directories for audio files
- Manage track metadata and playlists

### CLI mode

- Create or initialize the DJ Track database
- Scan a directory and insert supported track files
- List songs already stored in the database
- Detect new files not yet in the database
- Detect missing database entries for files removed from disk

---

## Requirements

- Python 3.8 or later
- Runtime dependencies are declared in `pyproject.toml`
- For GUI mode: `PySide6` is recommended

Note: the base installation uses the project package metadata from `pyproject.toml`, so you do not need a separate `requirements.txt` file.

---

## Installation

1. Clone the repository:

```bash
git clone https://github.com/flccrakers/dj-track.git
cd dj-track
```

2. Create the virtual environment and install the project:

```bash
./setup-env.sh
```

3. Activate the virtual environment:

```bash
source .venv/bin/activate
```

4. Install the project and its runtime dependencies from `pyproject.toml`:

```bash
python -m pip install -e .
```

5. If you want GUI support, ensure `PySide6` is installed. It is already declared in `pyproject.toml`, so the above install should cover it.

---

## Running the GUI

Use the GUI launcher script:

```bash
./run-tdj.sh
```

This script checks for `.venv` and the Qt bindings, then starts `djtango/DJTango.py`.

### First run behavior
The first time DJ Track runs, it will detect that no database exists and will create one in the DJ home directory.

By default, the home directory is:

```bash
~/.djtango
```

You can override the database directory with the `DJ_HOME_PATH` environment variable:

```bash
DJ_HOME_PATH="$HOME/my-dj-home" ./run-tdj.sh
```

If Qt bindings are not installed, the script will report a message and ask you to install `PySide6` or `PyQt5`.

---

## Running the CLI

Use the CLI launcher script:

```bash
./run-tdj-cli.sh --help
```

Or invoke the installed console script from inside the virtual environment:

```bash
source .venv/bin/activate
.venv/bin/python -m pip install -e .
.venv/bin/python -m djtango_cli --help
```

### Available commands

- `init-db`
  - Creates the DJ Track database in the configured home directory
- `scan <path>`
  - Scans the given directory for supported track audio files and inserts them into the database
- `list`
  - Lists all songs stored in the database
- `check-new <path>`
  - Lists audio files on disk that are not yet in the database
- `check-missing <path>`
  - Lists database entries whose files are missing from the given path root

### Example CLI workflow

Initialize the database:

```bash
./run-tdj-cli.sh init-db
```

Scan a directory of track files:

```bash
./run-tdj-cli.sh scan /path/to/track/music
```

List songs in the database:

```bash
./run-tdj-cli.sh list --limit 100
```

Check for new files not yet indexed:

```bash
./run-tdj-cli.sh check-new /path/to/track/music
```

Check for missing database entries:

```bash
./run-tdj-cli.sh check-missing /path/to/track/music
```

---

## Database storage

By default, DJ Track stores its database files under `~/.djtango`:

- `~/.djtango/djtango.db` — main song database
- `~/.djtango/el-recodo.db` — secondary track metadata database

The CLI and GUI both use the same home directory by default. To change that, set `DJ_HOME_PATH` before launching the app.

---

## Troubleshooting

### Virtual environment missing

If `.venv` is missing, run:

```bash
./setup-env.sh
```

### Qt bindings missing

If GUI mode fails with a Qt import error, install `PySide6`:

```bash
.venv/bin/python -m pip install PySide6
```

### Running headless or testing GUI startup

The GUI can be started in offscreen mode for testing. Set:

```bash
export QT_QPA_PLATFORM=offscreen
export DJTANGO_DISABLE_DIR_SCAN=1
```

Then run the GUI startup path in a test environment.

### Project tests

Run the unit tests locally with:

```bash
source .venv/bin/activate
python -m pytest -q
```

For container-based CI testing, use the repository test harness:

```bash
./ci/test
```

To force a Docker image rebuild for CI tests:

```bash
./ci/test -rebuild
```

---

## Project structure

- `tools/`
  - `djtango_cli.py` — CLI application entrypoint
- `djtango/`
  - `DJTango.py` — GUI application entrypoint
  - `data.py` — database connection and CRUD operations
  - `run-tdj.sh` — GUI launcher script
  - `run-tdj-cli.sh` — CLI launcher script
- `djtango/`
  - `data.py` — database connection and CRUD operations
  - `dirscanningthread.py` — directory scanner thread used by the GUI
  - `qt_compat.py` — Qt compatibility shim for PySide6/PyQt5
- `setup-env.sh` — builds the `.venv` and installs the project
- `pyproject.toml` — packaging configuration
- `tests/` — unit tests

---

## Notes for users

- The CLI is best for batch library management and scanning without a GUI dependency.
- The GUI is best for playback and interactive song selection.
- Keep your audio files organized in a stable directory tree so DJ Track can keep paths and database entries matched.
- If you install the project in editable mode with `./setup-env.sh`, code changes in the repository will be available immediately without reinstalling.

---

## Quick start summary

```bash
git clone https://github.com/flccrakers/dj-track.git
cd dj-track
./setup-env.sh
source .venv/bin/activate
.venv/bin/python -m pip install PySide6
./run-tdj.sh
```

Or use the CLI:

```bash
./run-tdj-cli.sh init-db
./run-tdj-cli.sh scan /path/to/tracks
./run-tdj-cli.sh list --limit 50
```
