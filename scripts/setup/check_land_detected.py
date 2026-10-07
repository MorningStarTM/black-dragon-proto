#!/usr/bin/env python3
import rclpy
from rclpy.node import Node
from rclpy.qos import QoSProfile, ReliabilityPolicy, DurabilityPolicy, HistoryPolicy
from px4_msgs.msg import VehicleLandDetected, VehicleStatus, VehicleLocalPosition


class Check(Node):
    def __init__(self):
        super().__init__('bd_check')
        qos = QoSProfile(
            reliability=ReliabilityPolicy.BEST_EFFORT,
            durability=DurabilityPolicy.TRANSIENT_LOCAL,
            history=HistoryPolicy.KEEP_LAST,
            depth=1,
        )
        self.create_subscription(VehicleLandDetected, '/fmu/out/vehicle_land_detected', self.on_land, qos)
        self.create_subscription(VehicleStatus, '/fmu/out/vehicle_status_v4', self.on_status, qos)
        self.create_subscription(VehicleLocalPosition, '/fmu/out/vehicle_local_position_v1', self.on_pos, qos)

    def on_land(self, msg):
        self.get_logger().info(
            f'LAND_DETECTED landed={msg.landed} maybe_landed={msg.maybe_landed} '
            f'ground_contact={msg.ground_contact} in_ground_effect={msg.in_ground_effect}')

    def on_status(self, msg):
        self.get_logger().info(f'STATUS arming={msg.arming_state} nav={msg.nav_state} failsafe={msg.failsafe}')

    def on_pos(self, msg):
        self.get_logger().info(f'POS z={msg.z:.3f} vz={msg.vz:.3f} dist_bottom={getattr(msg, "dist_bottom", float("nan")):.3f}')


def main():
    rclpy.init()
    node = Check()
    rclpy.spin(node)


if __name__ == '__main__':
    main()
