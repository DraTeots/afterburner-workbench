# eic_xl, the image scripts/in-eic-xl.sh runs; keep the two tags equal.
# The image runs as root and has no other user: files written into the bind-mounted workbench would be
# root's on the host. VS Code gives this user your UID and GID when it starts the container.
FROM eicweb/eic_xl:26.11.0-stable
RUN useradd --create-home --shell /bin/bash eic
