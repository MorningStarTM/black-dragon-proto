#!/usr/bin/env bash
# WP-D3: launch the gz_x500 model under PX4 SITL headless and confirm it comes up
# cleanly, without the pxh> shell spin that happens when stdin isn't a real TTY
# (that spin filled 36GB of disk in the first non-interactive attempt).
set -u
cd /home/ernest/bd/PX4-Autopilot || exit 1

# Hard safety cap: refuse to write more than 500MB no matter what happens.
ulimit -f 512000

export HEADLESS=1
timeout 45 make px4_sitl gz_x500 < /dev/null > /home/ernest/bd/px4_run.log 2>&1
echo "RUN_EXIT:$?"
