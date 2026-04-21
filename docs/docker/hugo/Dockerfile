ARG HUGO_BASE_IMAGE=ghcr.io/gohugoio/hugo:latest
FROM ${HUGO_BASE_IMAGE}

# Docsy's production CSS pipeline shells out to PostCSS. Keep that runtime
# inside the Hugo container so `make build` does not depend on host Node/npm.
USER root

RUN apk add --no-cache nodejs npm \
    && npm install --global autoprefixer postcss postcss-cli \
    && npm cache clean --force

ENV NODE_PATH=/usr/local/lib/node_modules
