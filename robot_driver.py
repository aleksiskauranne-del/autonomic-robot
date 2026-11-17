"""Webotsin TurtleBot3 Burgerin pyörä sekä odometriarvojen ROS ajuri."""

import math
from typing import Any

import rclpy
from geometry_msgs.msg import TwistStamped
from nav_msgs.msg import Odometry


WHEEL_DISTANCE = 0.160
WHEEL_RADIUS = 0.033
MAX_SPEED = 6.67
ODOM_RADIUS_LEFT = 0.033
ODOM_RADIUS_RIGHT = 0.03380


class RobotDriver:
    """Muunna ROS- nopeuskomennot Webotsin moottorinopeuksiksi."""

    def __init__(self):
        """Alusta Webotsin init-callbackissa täydennettävä sisäinen tila."""
        self.__robot: Any = None
        self.__timestep = 0
        self.__left_motor: Any = None
        self.__right_motor: Any = None
        self.__left_sensor: Any = None
        self.__right_sensor: Any = None
        self.__x = 0.0
        self.__y = 0.0
        self.__theta = 0.0
        self.__prev_left: float | None = None
        self.__prev_right: float | None = None
        self.__target_linear = 0.0
        self.__target_angular = 0.0
        self.__node: Any = None
        self.__odom_pub: Any = None

    def init(self, webots_node, _properties):
        """Alusta Webots-laitteet sekä ROS-komento- ja odometria-aiheet."""
        del _properties
        self.__robot = webots_node.robot
        self.__timestep = int(self.__robot.getBasicTimeStep())

        # Aseta pyörien moottorit nopeusohjaukseen sekä aktivoi anturit.
        self.__left_motor = self.__robot.getDevice("left wheel motor")
        self.__right_motor = self.__robot.getDevice("right wheel motor")
        self.__left_motor.setPosition(float("inf"))
        self.__right_motor.setPosition(float("inf"))
        self.__left_motor.setVelocity(0.0)
        self.__right_motor.setVelocity(0.0)

        self.__left_sensor = self.__robot.getDevice("left wheel sensor")
        self.__right_sensor = self.__robot.getDevice("right wheel sensor")
        self.__left_sensor.enable(self.__timestep)
        self.__right_sensor.enable(self.__timestep)

        # Alusta differentiaaliohjauksen sekä odometrian tilamuuttujat.
        self.__x = 0.0
        self.__y = 0.0
        self.__theta = 0.0
        self.__prev_left = None
        self.__prev_right = None
        self.__target_linear = 0.0
        self.__target_angular = 0.0

        rclpy.init(args=None)
        self.__node = rclpy.create_node("robot_driver")
        self.__node.create_subscription(
            TwistStamped, "/cmd_vel", self.__cmd_vel_callback, 1
        )
        self.__odom_pub = self.__node.create_publisher(Odometry, "/odom", 10)

    def __cmd_vel_callback(self, msg):
        """Tallenna Behavior Tree uusin lineaarinen ja kulmanopeus."""
        self.__target_linear = msg.twist.linear.x
        self.__target_angular = msg.twist.angular.z

    def step(self):
        """Aja moottoreita ja julkaise pyöräantureista laskettu odometria."""
        rclpy.spin_once(self.__node, timeout_sec=0)

        # Muunna nopeuskomento differentiaalipyörien radiaaneiksi sekunnissa.
        left_speed = (
            (2 * self.__target_linear - self.__target_angular * WHEEL_DISTANCE)
            / (2 * WHEEL_RADIUS)
            * 1.015
        )
        right_speed = (
            2 * self.__target_linear + self.__target_angular * WHEEL_DISTANCE
        ) / (2 * WHEEL_RADIUS)
        left_speed = max(-MAX_SPEED, min(MAX_SPEED, left_speed))
        right_speed = max(-MAX_SPEED, min(MAX_SPEED, right_speed))
        self.__left_motor.setVelocity(left_speed)
        self.__right_motor.setVelocity(right_speed)

        left_pos = self.__left_sensor.getValue()
        right_pos = self.__right_sensor.getValue()
        if self.__prev_left is None:
            self.__prev_left = left_pos
            self.__prev_right = right_pos
            return

        # Integroi pyörien siirtymät robotin tasosijainniksi sekä suunnaksi.
        delta_left = (left_pos - self.__prev_left) * ODOM_RADIUS_LEFT
        delta_right = (right_pos - self.__prev_right) * ODOM_RADIUS_RIGHT
        self.__prev_left = left_pos
        self.__prev_right = right_pos

        distance = (delta_right + delta_left) / 2.0
        delta_theta = (delta_right - delta_left) / WHEEL_DISTANCE
        self.__x += distance * math.cos(self.__theta + delta_theta / 2.0)
        self.__y += distance * math.sin(self.__theta + delta_theta / 2.0)
        self.__theta += delta_theta

        odometry = Odometry()
        odometry.header.stamp = self.__node.get_clock().now().to_msg()
        odometry.header.frame_id = "odom"
        odometry.child_frame_id = "base_footprint"
        odometry.pose.pose.position.x = self.__x
        odometry.pose.pose.position.y = self.__y
        odometry.pose.pose.orientation.z = math.sin(self.__theta / 2.0)
        odometry.pose.pose.orientation.w = math.cos(self.__theta / 2.0)
        odometry.twist.twist.linear.x = self.__target_linear
        odometry.twist.twist.angular.z = self.__target_angular
        self.__odom_pub.publish(odometry)
