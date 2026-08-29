FROM python:3.14-slim AS base

ARG USERNAME=troilo
ARG USER_UID=1000
ARG USER_GID=1000
ARG USER_PATH="${PATH}:/usr/bin/:/usr/local/bin:/uv:/uvx"

ENV USER_UID=${USER_UID:-1000} \
    USER_GID=${USER_GID:-1000} \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

COPY --from=docker.io/astral/uv:latest /uv /uvx /bin/
COPY ci/docker-bashrc /etc/bash.bashrc
RUN apt-get update && apt-get install -y --no-install-recommends \
    bash \
    ca-certificates \
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
    libdbus-1-3 \ca-certificates \
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
    && rm -rf /var/lib/apt/lists/* 
RUN  DEBIAN_FRONTEND=noninteractive dpkg-reconfigure dash \
    # Add a new user with specified UID and GID
    && groupadd --gid ${USER_GID} ${USERNAME} \
    && useradd --uid ${USER_UID} --gid ${USER_GID} --shell /bin/bash ${USERNAME}

RUN mkdir -p /workspace && chown "$USER_UID":"$USER_GID" /workspace

FROM base AS builder

WORKDIR /workspace
COPY . /workspace
RUN python -m pip install --upgrade pip setuptools wheel && python -m pip install -e .[test,dev]

FROM base AS runtime

COPY --from=builder /usr/local /usr/local
WORKDIR /workspace
USER ${USERNAME}

ENV PATH="${USER_PATH}"
ENV CLICOLOR=1
ENV CLICOLOR_FORCE=1
ENV NO_AT_BRIDGE=1
ENV GDK_DPI_SCALE=1.5
SHELL ["/bin/bash", "-c"]
CMD ["bash"]

