FROM python:3.14-slim AS builder

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

RUN apt-get update && apt-get install -y --no-install-recommends \
        gcc \
        libgtk-3-0 \
        libx11-6 \
        libxrender1 \
        libxext6 \
        libsm6 \
        libglib2.0-0 \
        libgl1 \
        libegl1 \
        libpulse0 \
        libasound2 \
        libdbus-1-3 \
        libxkbcommon-x11-0 \
        libxcb-xinerama0 \
        libxcb-icccm4 \
        libxcb-image0 \
        libxcb-keysyms1 \
        libxcb-render-util0 \
        libxcb-xfixes0 \
        libxcb-xkb1 \
        libxrandr2 \
        libxss1 \
        libxi6 \
        libfontconfig1 \
        libfreetype6 \
        libgstreamer1.0-0 \
        libgstreamer-plugins-base1.0-0 \
        gstreamer1.0-libav \
        gstreamer1.0-plugins-good \
        gstreamer1.0-plugins-bad \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY pyproject.toml ./

RUN python -m pip install --upgrade pip setuptools wheel pyinstaller

COPY . /app
RUN python -m pip install -e .[test]

RUN pyinstaller --noconfirm --clean --onefile --name DJTango \
    --add-data "gui/img:gui/img" \
    --add-data "djtango/img:djtango/img" \
    djtango/DJTango.py
