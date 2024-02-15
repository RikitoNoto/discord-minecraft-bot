FROM mcr.microsoft.com/devcontainers/base:ubuntu
ENV WORKSPACE_DIR "/workspace"
# Install the xz-utils package
RUN apt-get update && apt-get install -y xz-utils
