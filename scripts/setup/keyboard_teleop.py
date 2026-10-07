#!/usr/bin/env python3
"""Manual keyboard control for the PX4/Gazebo x500, for live demos.
Run after the agent and PX4 SITL are up (2 terminals; see repo chat history /
scripts/setup for the launch commands). This script needs only itself besides
that -- it includes its own MAVLink GCS-heartbeat stand-in, because PX4
refuses to arm with "No connection to the GCS" otherwise (discovered during
WP-E/F testing; easy to forget since it's not needed for anything else).

Controls (press a key, no Enter needed):
  c       arm + engage offboard mode
  w/s     forward / backward
  a/d     left / right
  r/f     up / down
  q/e     yaw left / right
  k       stop (hover in place)
  x       land + disarm
  Ctrl+C  quit (also disarms)
"""
import sys
import termios
import tty
import threading
import time

import rclpy
from rclpy.node import Node
from rclpy.qos import QoSProfile, ReliabilityPolicy, DurabilityPolicy, HistoryPolicy
from px4_msgs.msg import (
    VehicleCommand, OffboardControlMode, TrajectorySetpoint,
    VehicleStatus, VehicleCommandAck,
)

SPEED = 2.0       # m/s horizontal/vertical
YAW_RATE = 1.0    # rad/s

NAV_STATE_NAMES = {14: 'OFFBOARD', 18: 'AUTO_LAND', 4: 'AUTO_MISSION'}
ARMING_STATE_NAMES = {1: 'STANDBY', 2: 'ARMED'}


def gcs_heartbeat_thread():
    """Stand-in GCS so PX4's 'No connection to the GCS' prearm check passes."""
    from pymavlink import mavutil
    try:
        conn = mavutil.mavlink_connection('udpin:0.0.0.0:14550')
        conn.wait_heartbeat()  # learns PX4's address -- without this, sends go nowhere
        while True:
            conn.mav.heartbeat_send(
                mavutil.mavlink.MAV_TYPE_GCS,
                mavutil.mavlink.MAV_AUTOPILOT_INVALID, 0, 0, 0)
            time.sleep(1)
    except Exception as e:
        print(f'\n[gcs heartbeat thread died: {e}]')


class Teleop(Node):
    def __init__(self):
        super().__init__('bd_keyboard_teleop')
        qos = QoSProfile(reliability=ReliabilityPolicy.BEST_EFFORT,
                          durability=DurabilityPolicy.TRANSIENT_LOCAL,
                          history=HistoryPolicy.KEEP_LAST, depth=1)
        self.cmd_pub = self.create_publisher(VehicleCommand, '/fmu/in/vehicle_command', qos)
        self.ocm_pub = self.create_publisher(OffboardControlMode, '/fmu/in/offboard_control_mode', qos)
        self.sp_pub = self.create_publisher(TrajectorySetpoint, '/fmu/in/trajectory_setpoint', qos)
        self.create_subscription(VehicleStatus, '/fmu/out/vehicle_status_v4', self.on_status, qos)
        self.create_subscription(VehicleCommandAck, '/fmu/out/vehicle_command_ack_v1', self.on_ack, qos)
        self.arming_state = None
        self.nav_state = None
        self.vx = self.vy = self.vz = self.yaw_rate = 0.0
        self.last_print = ''
        self.timer = self.create_timer(0.1, self.stream)  # 10Hz, required by PX4

    def on_status(self, msg):
        if msg.arming_state != self.arming_state or msg.nav_state != self.nav_state:
            self.arming_state, self.nav_state = msg.arming_state, msg.nav_state
            a = ARMING_STATE_NAMES.get(self.arming_state, self.arming_state)
            n = NAV_STATE_NAMES.get(self.nav_state, self.nav_state)
            print(f'\n[state] arming={a} nav={n}')

    def on_ack(self, msg):
        result = 'ACCEPTED' if msg.result == 0 else f'REJECTED({msg.result})'
        print(f'\n[ack] command={msg.command} -> {result}')

    def send_command(self, command, p1=0.0, p2=0.0):
        m = VehicleCommand()
        m.timestamp = int(time.time() * 1e6)
        m.command, m.param1, m.param2 = command, p1, p2
        m.target_system = m.target_component = 1
        m.source_system = m.source_component = 1
        m.from_external = True
        self.cmd_pub.publish(m)

    def stream(self):
        m = OffboardControlMode()
        m.timestamp = int(time.time() * 1e6)
        m.velocity = True
        self.ocm_pub.publish(m)

        sp = TrajectorySetpoint()
        sp.timestamp = int(time.time() * 1e6)
        sp.position = [float('nan')] * 3
        sp.velocity = [self.vx, self.vy, self.vz]
        sp.yaw = float('nan')
        sp.yawspeed = self.yaw_rate
        self.sp_pub.publish(sp)

    def engage(self):
        print('\nengaging offboard + arm (watch [state]/[ack] lines below)...')
        self.send_command(176, p1=1.0, p2=6.0)   # DO_SET_MODE -> offboard
        time.sleep(1.0)
        self.send_command(400, p1=1.0, p2=21196.0)  # ARM (force)

    def land(self):
        self.vx = self.vy = self.vz = self.yaw_rate = 0.0
        self.send_command(21)  # NAV_LAND
        print('\nland sent')


def getch():
    fd = sys.stdin.fileno()
    old = termios.tcgetattr(fd)
    try:
        tty.setraw(fd)
        return sys.stdin.read(1)
    finally:
        termios.tcsetattr(fd, termios.TCSADRAIN, old)


def input_loop(node):
    print(__doc__)
    while rclpy.ok():
        ch = getch()
        if ch == '\x03':  # Ctrl+C
            node.land()
            time.sleep(1)
            node.send_command(400, p1=0.0, p2=21196.0)  # force disarm
            rclpy.shutdown()
            break
        elif ch == 'c':
            node.engage()
        elif ch == 'w':
            node.vx, node.vy = SPEED, 0.0
        elif ch == 's':
            node.vx, node.vy = -SPEED, 0.0
        elif ch == 'a':
            node.vx, node.vy = 0.0, -SPEED
        elif ch == 'd':
            node.vx, node.vy = 0.0, SPEED
        elif ch == 'r':
            node.vz = -SPEED  # NED: negative = up
        elif ch == 'f':
            node.vz = SPEED
        elif ch == 'q':
            node.yaw_rate = -YAW_RATE
        elif ch == 'e':
            node.yaw_rate = YAW_RATE
        elif ch == 'k':
            node.vx = node.vy = node.vz = node.yaw_rate = 0.0
            print('\nhover')
        elif ch == 'x':
            node.land()


def main():
    threading.Thread(target=gcs_heartbeat_thread, daemon=True).start()
    rclpy.init()
    node = Teleop()
    t = threading.Thread(target=input_loop, args=(node,), daemon=True)
    t.start()
    rclpy.spin(node)


if __name__ == '__main__':
    main()
