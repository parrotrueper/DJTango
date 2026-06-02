FROM python:3.14-slim AS builder

ARG USERNAME=troilo
ARG USER_UID=1000
ARG USER_GID=1000
ARG USER_PATH="${PATH}:/usr/bin/"

# If the build passes empty values for USER_UID/USER_GID, fall back to defaults.
ENV USER_UID=${USER_UID:-1000} 
ENV USER_GID=${USER_GID:-1000} 
ENV PYTHONDONTWRITEBYTECODE=1 
ENV PYTHONUNBUFFERED=1

COPY --from=docker.io/astral/uv:latest /uv /uvx /bin/
COPY ci/docker-bashrc /etc/bash.bashrc    
RUN apt-get update && apt-get install -y --no-install-recommends \
    bash \
    curl \
    dbus-x11 \
    gcc \
    git \
    libgtk-3-0 \
    libx11-6 \
    libxcb1 \
    libx11-xcb1 \
    libxrender1 \
    libxext6 \
    libsm6 \
    libglib2.0-0 \
    libgl1 \
    libegl1 \
    libxcb-glx0 \
    libxcb-render0 \
    libxcb-shm0 \
    libpulse0 \
    libasound2 \
    libdbus-1-3 \
    libxkbcommon0 \
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
    && rm -rf /var/lib/apt/lists/* \
    && groupadd --gid "$USER_GID" "$USERNAME" 2>/dev/null || true \
    && useradd -m -u "$USER_UID" -g "$USER_GID" -s /bin/bash "$USERNAME"

RUN mkdir -p /workspace && chown "$USER_UID":"$USER_GID" /workspace

WORKDIR /workspace
USER ${USERNAME}

ENV PATH="${USER_PATH}"
ENV CLICOLOR=1
ENV CLICOLOR_FORCE=1
ENV NO_AT_BRIDGE=1
ENV GDK_DPI_SCALE=1.5
SHELL ["/bin/bash", "-c"]
CMD ["source /etc/bash.bashrc"]

