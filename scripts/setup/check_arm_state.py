#!/usr/bin/env python3
import rclpy
from rclpy.node import Node
from rclpy.qos import QoSProfile, ReliabilityPolicy, DurabilityPolicy, HistoryPolicy
from px4_msgs.msg import VehicleStatus

rclpy.init()
n = Node('bd_check_arm')
qos = QoSProfile(reliability=ReliabilityPolicy.BEST_EFFORT, durability=DurabilityPolicy.TRANSIENT_LOCAL,
                  history=HistoryPolicy.KEEP_LAST, depth=1)


def cb(m):
    print('arming_state', m.arming_state)


n.create_subscription(VehicleStatus, '/fmu/out/vehicle_status_v4', cb, qos)
rclpy.spin_once(n, timeout_sec=5)
