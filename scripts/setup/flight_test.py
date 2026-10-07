#!/usr/bin/env python3
"""WP-F3: minimal step-response sanity check. Arms, switches to offboard mode,
commands a small climb (velocity setpoint), then zero velocity to hover, and
logs local position so we can see whether the response is bounded and settles
rather than diverging. Lands and disarms at the end.

PX4 requires a continuous offboard_control_mode + trajectory_setpoint stream
(>2Hz) before it will accept the mode switch and to keep holding it — a single
command isn't enough, which is why this runs on a timer rather than one-shot
like arm_test.py."""
import time
import rclpy
from rclpy.node import Node
from rclpy.qos import QoSProfile, ReliabilityPolicy, DurabilityPolicy, HistoryPolicy
from px4_msgs.msg import (
    VehicleCommand, VehicleCommandAck, VehicleStatus,
    OffboardControlMode, TrajectorySetpoint, VehicleLocalPosition,
)

VEHICLE_CMD_COMPONENT_ARM_DISARM = 400
VEHICLE_CMD_DO_SET_MODE = 176
PX4_CUSTOM_MAIN_MODE_OFFBOARD = 6


class FlightTest(Node):
    def __init__(self):
        super().__init__('bd_flight_test')
        qos = QoSProfile(
            reliability=ReliabilityPolicy.BEST_EFFORT,
            durability=DurabilityPolicy.TRANSIENT_LOCAL,
            history=HistoryPolicy.KEEP_LAST,
            depth=1,
        )
        self.cmd_pub = self.create_publisher(VehicleCommand, '/fmu/in/vehicle_command', qos)
        self.ocm_pub = self.create_publisher(OffboardControlMode, '/fmu/in/offboard_control_mode', qos)
        self.sp_pub = self.create_publisher(TrajectorySetpoint, '/fmu/in/trajectory_setpoint', qos)
        self.create_subscription(VehicleCommandAck, '/fmu/out/vehicle_command_ack_v1', self.on_ack, qos)
        self.create_subscription(VehicleStatus, '/fmu/out/vehicle_status_v4', self.on_status, qos)
        self.create_subscription(VehicleLocalPosition, '/fmu/out/vehicle_local_position_v1', self.on_pos, qos)

        self.arming_state = None
        self.nav_state = None
        self.z = None
        self.target_vz = 0.0
        self.phase = 'wait_pos'
        self.phase_tick = 0
        self.timer = self.create_timer(0.1, self.tick)  # 10Hz offboard stream
        self.ticks = 0

    def on_ack(self, msg):
        self.get_logger().info(f'ACK: command={msg.command} result={msg.result}')

    def on_status(self, msg):
        self.arming_state = msg.arming_state
        self.nav_state = msg.nav_state

    def on_pos(self, msg):
        self.z = msg.z  # NED: negative = up

    def send_offboard_heartbeat(self):
        m = OffboardControlMode()
        m.timestamp = int(time.time() * 1e6)
        m.velocity = True
        self.ocm_pub.publish(m)

    def send_setpoint(self, vz):
        m = TrajectorySetpoint()
        m.timestamp = int(time.time() * 1e6)
        m.position = [float('nan')] * 3
        m.velocity = [0.0, 0.0, vz]
        m.yaw = float('nan')
        self.sp_pub.publish(m)

    def send_command(self, command, p1=0.0, p2=0.0):
        m = VehicleCommand()
        m.timestamp = int(time.time() * 1e6)
        m.command = command
        m.param1 = p1
        m.param2 = p2
        m.target_system = 1
        m.target_component = 1
        m.source_system = 1
        m.source_component = 1
        m.from_external = True
        self.cmd_pub.publish(m)

    def tick(self):
        self.ticks += 1
        self.send_offboard_heartbeat()
        self.send_setpoint(self.target_vz)

        if self.phase == 'wait_pos':
            if self.z is not None:
                self.get_logger().info(f'Have position, z={self.z:.2f}. Switching to offboard.')
                self.phase, self.phase_tick = 'switch_offboard', 0
        elif self.phase == 'switch_offboard':
            self.phase_tick += 1
            if self.phase_tick == 10:  # ~1s of offboard stream before requesting mode
                self.send_command(VEHICLE_CMD_DO_SET_MODE, p1=1.0, p2=float(PX4_CUSTOM_MAIN_MODE_OFFBOARD))
            if self.phase_tick == 20:
                self.send_command(VEHICLE_CMD_COMPONENT_ARM_DISARM, p1=1.0, p2=21196.0)
                self.get_logger().info('Sent offboard+arm')
            if self.phase_tick > 30 and self.arming_state == 2:
                self.get_logger().info(f'ARMED. nav_state={self.nav_state}. Climbing.')
                self.target_vz = -1.0  # NED: climb at 1 m/s
                self.phase, self.phase_tick = 'climb', 0
        elif self.phase == 'climb':
            self.phase_tick += 1
            if self.ticks % 10 == 0:
                self.get_logger().info(f'CLIMB z={self.z:.2f}')
            if self.phase_tick > 120:  # ~12s climb -- PX4's takeoff ramp needs ~8s to build authority
                self.target_vz = 0.0
                self.phase, self.phase_tick = 'hover', 0
                self.get_logger().info('Switching to hover (vz=0)')
        elif self.phase == 'hover':
            self.phase_tick += 1
            if self.ticks % 10 == 0:
                self.get_logger().info(f'HOVER z={self.z:.2f}')
            if self.phase_tick > 60:  # ~6s hover
                self.phase = 'land'
                self.send_command(21)  # VEHICLE_CMD_NAV_LAND
                self.get_logger().info('Sent land command')
        elif self.phase == 'land':
            if self.ticks % 10 == 0:
                self.get_logger().info(f'LANDING z={self.z}, arming_state={self.arming_state}')
            if self.arming_state == 1:  # back to standby = disarmed after landing
                self.get_logger().info('Landed and disarmed. Done.')
                rclpy.shutdown()

        if self.ticks > 350:  # ~35s hard cap
            self.get_logger().warn('Hit hard time cap, shutting down.')
            rclpy.shutdown()


def main():
    rclpy.init()
    node = FlightTest()
    rclpy.spin(node)


if __name__ == '__main__':
    main()
