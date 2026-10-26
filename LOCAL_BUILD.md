# Local build (fork danfg95/aventproxy, branch `local-build`)

Branch `local-build` starts at `ab187391e721282eb6cb0da677f32b202d703f45`, the commit of upstream tag
`2026.10.0` (thekoma/aventproxy), with only these changes, so the Home Assistant Supervisor builds the add-on
on the machine from this source instead of pulling the prebuilt image from ghcr.io:

- `aventproxy-bridge-addon/config.yaml`: no `image:` line (the Supervisor builds locally), `map: config:ro`
  (the bridge only reads `/config/philips_avent_bridge_*.json`), name "Philips Avent Bridge (local)".
- `aventproxy-bridge-addon/avent-webrtc-bridge/`: a copy of `avent-webrtc-bridge/`, where the Dockerfile
  expects it (the upstream release workflow copies it there before building).
- `aventproxy-bridge-addon/build.yaml`: base `debian:bookworm-slim`, as the upstream release workflow.
- `aventproxy-bridge-addon-beta/` and `-dev/` removed: they pull prebuilt images.
- `repository.yaml`: this fork. GitHub Actions are disabled on the fork.

Add-on repository URL in Home Assistant: `https://github.com/danfg95/aventproxy#local-build`
