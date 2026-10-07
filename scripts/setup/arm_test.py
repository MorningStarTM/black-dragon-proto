#!/usr/bin/env python3
"""WP-E4: send MAV_CMD_COMPONENT_ARM_DISARM over /fmu/in/vehicle_command and
watch /fmu/out/vehicle_command_ack_v1 + /fmu/out/vehicle_status_v4 for the
result. This is the Phase 1 exit criterion: a command sent over ROS2 moving
the drone's state in the PX4/Gazebo simulation."""
import time
import rclpy
from rclpy.node import Node
from rclpy.qos import QoSProfile, ReliabilityPolicy, DurabilityPolicy, HistoryPolicy
from px4_msgs.msg import VehicleCommand, VehicleCommandAck, VehicleStatus

VEHICLE_CMD_COMPONENT_ARM_DISARM = 400


class ArmTest(Node):
    def __init__(self):
        super().__init__('bd_arm_test')
        qos = QoSProfile(
            reliability=ReliabilityPolicy.BEST_EFFORT,
            durability=DurabilityPolicy.TRANSIENT_LOCAL,
            history=HistoryPolicy.KEEP_LAST,
            depth=1,
        )
        self.cmd_pub = self.create_publisher(VehicleCommand, '/fmu/in/vehicle_command', qos)
        self.ack_sub = self.create_subscription(
            VehicleCommandAck, '/fmu/out/vehicle_command_ack_v1', self.on_ack, qos)
        self.status_sub = self.create_subscription(
            VehicleStatus, '/fmu/out/vehicle_status_v4', self.on_status, qos)
        self.got_ack = False
        self.last_status = None
        self.timer = self.create_timer(0.5, self.tick)
        self.ticks = 0

    def on_ack(self, msg):
        self.got_ack = True
        self.get_logger().info(
            f'ACK: command={msg.command} result={msg.result} '
            f'(0=ACCEPTED, see MAV_RESULT enum for others)')

    def on_status(self, msg):
        self.last_status = msg
        self.get_logger().info(f'STATUS: arming_state={msg.arming_state}')

    def tick(self):
        self.ticks += 1
        if self.ticks == 4:  # let subscriptions settle (~2s) before sending
            self.send_arm()
        if self.ticks > 20:  # ~10s total, enough to see the ack arrive
            rclpy.shutdown()

    def send_arm(self):
        msg = VehicleCommand()
        msg.timestamp = int(time.time() * 1e6)
        msg.command = VEHICLE_CMD_COMPONENT_ARM_DISARM
        msg.param1 = 1.0  # 1 = arm
        # 21196 is PX4/MAVLink's documented "force" magic number for param2,
        # bypassing prearm checks that assume a MAVLink GCS is attached (we
        # only have the ROS2/uXRCE-DDS link, no GCS, so "No connection to
        # the GCS" fails by design otherwise). Fine for this smoke test;
        # not something to carry into real flight logic.
        msg.param2 = 21196.0
        msg.target_system = 1
        msg.target_component = 1
        msg.source_system = 1
        msg.source_component = 1
        msg.from_external = True
        self.cmd_pub.publish(msg)
        self.get_logger().info('Sent arm command')


def main():
    rclpy.init()
    node = ArmTest()
    rclpy.spin(node)
    node.destroy_node()


if __name__ == '__main__':
    main()
