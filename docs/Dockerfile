FROM golang:1.26.1-bookworm AS go-toolchain

FROM node:22-bookworm-slim

# Keep the Hugo version explicit so the image can be rebuilt reproducibly and
# updated deliberately. The default tracks the current local toolchain rather
# than relying on whatever version Debian happens to ship.
ARG HUGO_VERSION=0.158.0
ARG TARGETARCH

ENV DEBIAN_FRONTEND=noninteractive
ENV VIRTUAL_ENV=/opt/docs-venv
ENV PATH="/usr/local/go/bin:/opt/docs-venv/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin"

# This image is intentionally narrow: it contains the build/runtime
# prerequisites for the docs site, but not browser automation or serving.
# Those remain separate concerns.
RUN apt-get update && apt-get install -y --no-install-recommends \
    ca-certificates \
    curl \
    git \
    make \
    pandoc \
    python3 \
    python3-venv \
  && rm -rf /var/lib/apt/lists/*

COPY --from=go-toolchain /usr/local/go /usr/local/go

# Install the Hugo extended binary explicitly. Hugo modules in this repo rely
# on Go, which is why the image also carries the Go toolchain.
RUN set -eux; \
  detected_arch="${TARGETARCH:-}"; \
  if [ -z "${detected_arch}" ]; then \
    case "$(dpkg --print-architecture)" in \
      amd64) detected_arch="amd64" ;; \
      arm64) detected_arch="arm64" ;; \
      *) echo "Unable to infer a supported architecture from dpkg" >&2; exit 1 ;; \
    esac; \
  fi; \
  case "${detected_arch}" in \
    amd64) hugo_arch="amd64" ;; \
    arm64) hugo_arch="arm64" ;; \
    *) echo "Unsupported TARGETARCH: ${detected_arch}" >&2; exit 1 ;; \
  esac; \
  curl -fsSL -o /tmp/hugo.deb \
    "https://github.com/gohugoio/hugo/releases/download/v${HUGO_VERSION}/hugo_extended_${HUGO_VERSION}_linux-${hugo_arch}.deb"; \
  apt-get update; \
  apt-get install -y --no-install-recommends /tmp/hugo.deb; \
  rm -f /tmp/hugo.deb; \
  rm -rf /var/lib/apt/lists/*

# Python dependencies are installed from the docs-specific requirements plus
# the shared repo-level development requirements so the container can execute
# the legacy Python-based docs generators and supporting tooling without
# requiring extra host setup.
COPY docs/docs-requirements.txt /tmp/docs-requirements.txt
COPY dev-requirements.txt /tmp/dev-requirements.txt
RUN python3 -m venv "${VIRTUAL_ENV}" \
  && "${VIRTUAL_ENV}/bin/pip" install --upgrade pip \
  && "${VIRTUAL_ENV}/bin/pip" install --no-cache-dir \
    -r /tmp/docs-requirements.txt \
    -r /tmp/dev-requirements.txt \
  && rm -f /tmp/docs-requirements.txt /tmp/dev-requirements.txt

WORKDIR /workspace/docs

CMD ["/bin/bash"]
