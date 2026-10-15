# Changelog

This is the beta card: it follows release candidates of the integration.
Stay on the stable card unless you are testing an rc.

## 2026.10.1-rc3

The bridge is unchanged from rc1. In the integration, Baby Detected no longer
stays on after the baby leaves the crib on monitors that push SenseIQ status
over the LAN. Please report on #74.

## 2026.10.1-rc2

The bridge is unchanged from rc1. In the integration, SenseIQ entities now
appear when their data first arrives, not only at startup, so data that shows
up after Home Assistant starts still gets its entities. Please report on #74.

## 2026.10.1-rc1

The bridge is the same as in 2026.10.0. This rc exists to test SenseIQ
sleep and breathing in the integration (#87); please report on #74.

### ⚠️ BREAKING CHANGE: read this before updating

**The RTSP stream is now only reachable from this host.** The bridge's RTSP
server has no password, so it now listens on `localhost` (127.0.0.1 and ::1)
instead of every network interface.

**Nothing to do** if Home Assistant opens the stream at the default
`rtsp://localhost:38554/...`.

**You must change a setting** if you open the stream from another machine
(VLC, Frigate, Scrypted or HomeKit through Scrypted, a separate go2rtc), or if
you set the integration's **Bridge host** option to this machine's IP address.
Set the add-on option **RTSP bind address** to `0.0.0.0` or to a specific
address, save, restart the add-on, and restrict port 38554 on your network.

### Fixed

- HomeKit through Scrypted no longer freezes on the first frame: every packet
  of a video frame carries the same RTP timestamp (#88).
- An SD H.264 stream no longer leaves the camera locked for later clients
  (#81).

### Changed

- Built with Go 1.27, pion/webrtc 4.2.23 and the matching pion libraries.
