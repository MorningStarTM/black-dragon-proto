#!/usr/bin/env python3
"""Safety cleanup: send disarm regardless of current state. Harmless no-op if
already disarmed."""
import time
import rclpy
from rclpy.node import Node
from rclpy.qos import QoSProfile, ReliabilityPolicy, DurabilityPolicy, HistoryPolicy
from px4_msgs.msg import VehicleCommand

rclpy.init()
n = Node('bd_force_disarm')
qos = QoSProfile(reliability=ReliabilityPolicy.BEST_EFFORT, durability=DurabilityPolicy.TRANSIENT_LOCAL,
                  history=HistoryPolicy.KEEP_LAST, depth=1)
pub = n.create_publisher(VehicleCommand, '/fmu/in/vehicle_command', qos)

for _ in range(10):
    m = VehicleCommand()
    m.timestamp = int(time.time() * 1e6)
    m.command = 400  # ARM_DISARM
    m.param1 = 0.0  # 0 = disarm
    m.param2 = 21196.0  # force
    m.target_system = 1
    m.target_component = 1
    m.source_system = 1
    m.source_component = 1
    m.from_external = True
    pub.publish(m)
    rclpy.spin_once(n, timeout_sec=0.3)

print('disarm commands sent')
