# Version pin (WP-D1)

PX4-Autopilot: `main` @ `1af262c9257c120615019c0da436e725476b63a9`
(`git describe --tags` → `v1.18.0-beta1-982-g1af262c925`)

Not a tagged stable release — this is a dev snapshot of `main`, 982 commits past
the `v1.18.0-beta1` tag. Recorded here so the environment is reproducible even
though it isn't pinned to a named release. If build/runtime instability shows
up later, the first thing to try is pinning back to the `v1.18.0-beta1` tag
itself.

px4_msgs: `release/1.18` branch — chosen to match PX4's v1.18 line rather than
the repo default (`release/1.15`), since PX4 is this far ahead of that release.

Built with:
- Ubuntu 24.04 (WSL2)
- ROS2 Jazzy
- Gazebo Harmonic (gz-sim 8.15.0)
- `Tools/setup/ubuntu.sh --no-nuttx --no-sim-tools` (NuttX cross-toolchain
  skipped — not needed until Phase 8 hardware port; Gazebo/ros_gz installed
  separately via scripts/setup/phase1_bootstrap.sh instead of PX4's own
  sim-tools installer, to avoid a second/conflicting Gazebo install)
