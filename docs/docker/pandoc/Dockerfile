FROM texlive/texlive:latest

# This image is the complete PDF build runtime for `docs/`.
#
# Design constraints:
# - build on top of a TeX-native base image so the LaTeX layer is not rebuilt
#   from scratch in this repo
# - keep Pandoc, LaTeX, fonts, and Mermaid tooling inside one image
# - let Mermaid CLI manage its own browser/runtime dependencies via npm rather
#   than wiring a separate browser package into the docs build contract
# - keep the final runtime obvious enough that future PDF failures can be
#   debugged by reading one Dockerfile instead of reverse-engineering a chain
#   of host dependencies

ARG DEBIAN_FRONTEND=noninteractive
ENV TERM=dumb
ENV PUPPETEER_CACHE_DIR=/opt/puppeteer
ENV PUPPETEER_SKIP_CHROMIUM_DOWNLOAD=true
ENV PUPPETEER_EXECUTABLE_PATH=/usr/bin/chromium
ENV CHROME_BIN=/usr/bin/chromium

# `texlive/texlive` is based on Debian testing and already carries the full
# TeX Live tree. That removes the most expensive and failure-prone part of the
# old image build: trying to reconstruct a sufficiently complete TeX install in
# this Dockerfile. The remaining packages are only the non-TeX pieces our PDF
# pipeline needs on top of that base.
#
# Notable choices:
# - `pandoc` comes from Debian testing and is current enough for this repo's
#   Lua filter surface, so the old hand-downloaded `.deb` path is gone.
# - Node.js comes from NodeSource rather than Debian so the Mermaid runtime can
#   stay pinned to the Node 20 line the PDF container expects, independent of
#   whatever Node version Debian testing happens to carry at build time.
# - `chromium` comes from Debian testing so the browser binary matches the
#   container architecture instead of relying on Puppeteer's prebuilt browser
#   downloads, which are not usable on this arm64 runtime.
# - Puppeteer's browser download is explicitly disabled and its executable path
#   is pinned to `/usr/bin/chromium` so Mermaid reuses the packaged browser.
# - the font packages are kept explicit because the LaTeX template names these
#   families directly; leaving them implicit would make the visual contract much
#   harder to reason about.
RUN apt-get update \
    && apt-get install --yes --no-install-recommends \
      ca-certificates \
      chromium \
      chromium-sandbox \
      curl \
      fonts-firacode \
      fonts-freefont-ttf \
      fonts-inter \
      fonts-liberation \
      fonts-noto-cjk \
      fonts-noto-core \
      gnupg \
      inkscape \
      libncurses6 \
      librsvg2-bin \
      pandoc \
      xdg-utils \
    && rm -rf /var/lib/apt/lists/* \
    && curl -fsSL https://deb.nodesource.com/setup_20.x | bash - \
    && apt-get update \
    && apt-get install --yes --no-install-recommends \
      nodejs \
    && rm -rf /var/lib/apt/lists/*

# Mermaid CLI still comes from npm, but Chromium comes from the distro package
# manager. The environment above tells Puppeteer not to fetch its own browser
# during install and to launch the packaged Chromium binary at runtime.
RUN npm install --global @mermaid-js/mermaid-cli@11.12.0 \
    && npm cache clean --force

# The builder mounts the repo's `docs/` directory at /docs and invokes this
# image with Pandoc arguments directly.
WORKDIR /docs
ENTRYPOINT ["pandoc"]
