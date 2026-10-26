FROM golang:1.27-bookworm AS builder

WORKDIR /src
COPY avent-webrtc-bridge/ .
RUN go mod download && CGO_ENABLED=0 go build -o /avent-webrtc-bridge .

# Base pinned here (no build.yaml): the same debian:bookworm-slim index the upstream 2026.10.0 release build used
FROM docker.io/library/debian:bookworm-slim@sha256:7c7b2c966bc9ee8cedfeef67e0e279108992c77681fa595db4a9d65c06ccc587

RUN apt-get update && apt-get install -y --no-install-recommends jq ca-certificates && rm -rf /var/lib/apt/lists/*

COPY --from=builder /avent-webrtc-bridge /usr/local/bin/avent-webrtc-bridge
COPY run.sh /
RUN chmod a+x /run.sh

CMD [ "/run.sh" ]
