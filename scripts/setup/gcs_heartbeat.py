#!/usr/bin/env python3
"""Minimal stand-in GCS: PX4's prearm checks include "No connection to the
GCS", which fails whenever nothing is listening on the MAVLink link (we only
run ROS2/uXRCE-DDS, no QGroundControl). This just sends MAVLink heartbeats
on PX4 SITL's default GCS port so that specific check passes, without pulling
in a full ground control station. Runs until killed."""
import time
from pymavlink import mavutil

conn = mavutil.mavlink_connection('udpin:0.0.0.0:14550')
print('Listening for PX4 on udp:14550...')
conn.wait_heartbeat()
print(f'Got heartbeat from system {conn.target_system} component {conn.target_component}')

while True:
    conn.mav.heartbeat_send(
        mavutil.mavlink.MAV_TYPE_GCS,
        mavutil.mavlink.MAV_AUTOPILOT_INVALID,
        0, 0, 0,
    )
    time.sleep(1)
