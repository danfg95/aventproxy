# Changelog

## 2026.10.0

### ⚠️ BREAKING CHANGE: read this before updating

**The RTSP stream is now only reachable from this host.** The bridge's RTSP
server has no password, so it now listens on `localhost` (127.0.0.1 and ::1)
instead of every network interface. Until now, anyone on your network could
watch and hear the camera at `rtsp://<your-HA-address>:38554/<camera>`.

**Nothing to do** if Home Assistant opens the stream at the default
`rtsp://localhost:38554/...`, which is the standard setup.

**You must change a setting** if any of these applies to you:

- you open the stream from another machine: VLC, Frigate, Scrypted or
  HomeKit through Scrypted, a separate go2rtc;
- you set the integration's **Bridge host** option to this machine's IP
  address instead of `localhost`.

To restore access, set the add-on option **RTSP bind address** to `0.0.0.0`
(every interface) or to a specific address, save, and restart the add-on.
Then restrict port 38554 on your network, because the stream has no password.

### Fixed

- HomeKit through Scrypted froze on the first frame of the live view, and
  Scrypted lost the pre-roll of HomeKit Secure Video clips. Every packet of a
  video frame now carries the same RTP timestamp, and the parameter sets
  injected before each keyframe get consecutive sequence numbers (#88).
- An SD H.264 stream never reported that it had started, which left the
  camera locked and stalled every later client before it got an answer (#81).

### Changed

- Built with Go 1.27, pion/webrtc 4.2.23 and the matching pion libraries.
