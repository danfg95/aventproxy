# Local build (fork danfg95/aventproxy, branch `local-build`)

Branch `local-build` starts at `ab187391e721282eb6cb0da677f32b202d703f45`, the commit of upstream tag
`2026.10.0` (thekoma/aventproxy), with only these changes, so the Home Assistant Supervisor builds the add-on
on the machine from this source instead of pulling the prebuilt image from ghcr.io:

- `aventproxy-bridge-addon/config.yaml`: no `image:` line (the Supervisor builds locally), `map: config:ro`
  (the bridge only reads `/config/philips_avent_bridge_*.json`), name "Philips Avent Bridge (local)".
- `aventproxy-bridge-addon/avent-webrtc-bridge/`: a copy of `avent-webrtc-bridge/`, where the Dockerfile
  expects it (the upstream release workflow copies it there before building).
- `aventproxy-bridge-addon/Dockerfile`: the runtime base is fixed in the Dockerfile,
  `FROM docker.io/library/debian:bookworm-slim@sha256:7c7b2c966bc9ee8cedfeef67e0e279108992c77681fa595db4a9d65c06ccc587`
  (the same index the upstream 2026.10.0 release build resolved), instead of `ARG BUILD_FROM` / `FROM ${BUILD_FROM}`.
  `build.yaml` is removed.
- `aventproxy-bridge-addon-beta/` and `-dev/` removed: they pull prebuilt images.
- `repository.yaml`: this fork. GitHub Actions are disabled on the fork.
- `aventproxy-bridge-addon/run.sh`: waits for the integration's bridge config instead of exiting when the add-on
  starts first (`/data/options.json` only counts when it has a `signing_key`), and looks for the newest config again
  on every restart of the bridge.
- `pkg/rtsp/forwarder.go` (both copies): the camera's video packets are put back in sequence order before they are
  restamped (late NACK resends were stamped into the next frame: garbage slices, grey smears), a lost one is given up
  after 100 ms, a frame goes out only whole (one with a lost packet is dropped, so no keyframe is cut short), and each
  RTSP client gets video only from a keyframe on: when it joins, and again after a loss.

Add-on repository URL in Home Assistant: `https://github.com/danfg95/aventproxy#local-build`

## Why there is no build.yaml

Supervisor 2026.10.3 still reads `build.yaml` (it logs that it is deprecated: "Move build parameters into the
Dockerfile directly"), but it validates each `build_from` image against
`^([a-zA-Z\-\.:\d{}]+/)*?([\-\w{}]+)/([\-\w{}]+)(:[\.\-\w{}]+)?$`, which needs a `namespace/name` form.
`debian:bookworm-slim` does not match (`docker.io/library/debian:bookworm-slim` would), so the whole file was
discarded "using defaults" and `BUILD_FROM` became `ghcr.io/home-assistant/base:latest` (Alpine, no apt-get):
the first build failed. Without `build.yaml` the Supervisor passes no `BUILD_FROM` and the Dockerfile's own
`FROM` is used (supervisor/apps/build.py, `_read_build_config` and `base_image`).
