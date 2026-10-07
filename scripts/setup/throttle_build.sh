#!/usr/bin/env bash
# Lower CPU/IO priority of an in-progress ninja/gcc build without killing it,
# so the WSL2 VM doesn't starve the Windows host while PX4 compiles.
set -u
count=0
for p in $(pgrep -f 'ninja|cc1plus|cc1 |c\+\+|/usr/bin/gcc|/usr/bin/g\+\+'); do
  renice -n 15 -p "$p" >/dev/null 2>&1
  ionice -c3 -p "$p" >/dev/null 2>&1
  count=$((count+1))
done
echo "RENICED_COUNT:$count"
