# DJTango

Software for track DJs.

Originally forked from https://github.com/flccrakers/dj-track 

This project is a very different beast from the original source.

**Project status -- Under development**

## Dependencies

### Python dependencies

These are managed in `pyproject.toml`:

* `PySide6`
* `pydub`
* `audioread`

Optional test dependencies:

* `nose`

### System library dependencies

For GUI and multimedia support, the container build installs:

* `libgtk-3-0`
* `libx11-6`
* `libxrender1`
* `libxext6`
* `libsm6`
* `libglib2.0-0`
* `libgl1`
* `libegl1`
* `libpulse0`
* `libasound2`
* `libdbus-1-3`
* `libxkbcommon-x11-0`
* `libxcb-xinerama0`
* `libxcb-icccm4`
* `libxcb-image0`
* `libxcb-keysyms1`
* `libxcb-render-util0`
* `libxcb-xfixes0`
* `libxcb-xkb1`
* `libxrandr2`
* `libxss1`
* `libxi6`
* `libfontconfig1`
* `libfreetype6`
* `libgstreamer1.0-0`
* `libgstreamer-plugins-base1.0-0`
* `gstreamer1.0-libav`
* `gstreamer1.0-plugins-good`
* `gstreamer1.0-plugins-bad`

## Installation

* Clone the repository.
* Setup the environment
  
```shell
./setup-env.sh
```

If you are using `uv`, the project can also be bootstrapped from the repository root:

```shell
uv .venv install -e .[test,dev]
uv .venv shell
```

## Testing

Run the unit tests with:

```shell
source .venv/bin/activate
python -m pytest -q
```

For CI tests inside Docker, use:

```shell
./ci/test
```

## Launch

```shell
./run-tdj.sh
```

## Status

* Finish unit testing -- in progress
* Finish bug fixes -- in progress

## TODO

* Create CI 
* Create deploy
* Release
  