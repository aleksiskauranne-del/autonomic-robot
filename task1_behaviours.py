"""Hybridisen robotin Behavior Tree lehtikäyttäytymiset."""

import math

import py_trees
from geometry_msgs.msg import TwistStamped
from sensor_msgs.msg import LaserScan


# Liike sekä esteväistön säätöarvot tehtävänannon mukaisesti.
OBSTACLE_THRESHOLD = 0.5
FORWARD_ARC_DEG = 30
DRIVE_SPEED = 0.3
TURN_SPEED = 0.8
TURN_SCAN_ANGLE_DEG = 60.0


# Reaktiivinen ehto. tarkasta esteet vain robotin edessä olevasta sektorista.
class IsObstacleTooClose(py_trees.behaviour.Behaviour):
    """Ilmaise onko etusektorilla kynnysarvoa lähempänä este."""

    def __init__(self, ros_node):
        super().__init__(name="IsObstacleTooClose")
        self.ros_node = ros_node
        self.latest_scan = None
        self.ros_node.create_subscription(
            LaserScan, "/scan", self._scan_callback, 10
        )

    def _scan_callback(self, msg):
        """Tallenna uusin LiDAR skannaus seuraavaa puun tikkiä varten."""
        self.latest_scan = msg

    def update(self):
        """Palauta SUCCESS etusektorin esteestä muutoin FAILURE."""
        scan = self.latest_scan
        if scan is None:
            return py_trees.common.Status.FAILURE

        half_arc = math.radians(FORWARD_ARC_DEG)
        for index, distance in enumerate(scan.ranges):
            angle = scan.angle_min + index * scan.angle_increment
            angle = math.atan2(math.sin(angle), math.cos(angle))
            if abs(angle) > half_arc and not math.isclose(abs(angle), half_arc):
                continue
            if not math.isfinite(distance) or distance <= 0.0:
                continue
            if distance < OBSTACLE_THRESHOLD:
                return py_trees.common.Status.SUCCESS

        return py_trees.common.Status.FAILURE


# Reaktiivinen toiminto pyöri paikallaan esteen ollessa edessä.
class TurnAway(py_trees.behaviour.Behaviour):
    """Käänny paikallaan LiDAR mukaan avoimempaan suuntaan."""

    def __init__(self, ros_node):
        super().__init__(name="TurnAway")
        self.ros_node = ros_node
        self.latest_scan = None
        self.turn_direction = 1.0
        self.ros_node.create_subscription(
            LaserScan, "/scan", self._scan_callback, 10
        )
        self.publisher = self.ros_node.create_publisher(
            TwistStamped, "/cmd_vel", 10
        )

    def _scan_callback(self, msg):
        """Tallenna uusin skannaus kääntymissuunnan valintaa varten."""
        self.latest_scan = msg

    def _sector_clearance(self, scan, center_angle):
        """Palauta sektorin lähin kelvollinen este-etäisyys."""
        half_arc = math.radians(FORWARD_ARC_DEG)
        distances = []
        for index, distance in enumerate(scan.ranges):
            angle = scan.angle_min + index * scan.angle_increment
            angle = math.atan2(math.sin(angle), math.cos(angle))
            relative_angle = math.atan2(
                math.sin(angle - center_angle),
                math.cos(angle - center_angle),
            )
            if abs(relative_angle) > half_arc and not math.isclose(
                abs(relative_angle), half_arc
            ):
                continue
            if math.isfinite(distance) and distance > 0.0:
                distances.append(distance)

        return min(distances, default=math.inf)

    def initialise(self):
        """Valitse väistöjakson alussa puoleltaan väljempi suunta."""
        scan = self.latest_scan
        if scan is None:
            self.turn_direction = 1.0
            return

        side_angle = math.radians(TURN_SCAN_ANGLE_DEG)
        left_clearance = self._sector_clearance(scan, side_angle)
        right_clearance = self._sector_clearance(scan, -side_angle)
        self.turn_direction = (
            1.0 if left_clearance >= right_clearance else -1.0
        )

    def update(self):
        """Julkaise valittuun suuntaan kääntökomento ja palauta RUNNING."""
        msg = TwistStamped()
        msg.header.stamp = self.ros_node.get_clock().now().to_msg()
        msg.twist.linear.x = 0.0
        msg.twist.angular.z = self.turn_direction * TURN_SPEED
        self.publisher.publish(msg)
        return py_trees.common.Status.RUNNING


# Deliberatiivinen perustoiminto aja suoraan kun reaktiivinen haara
# ei ilmoita edessä olevasta esteestä.
class DriveForward(py_trees.behaviour.Behaviour):
    """Julkaise vakionopeutta eteenpäin jatkuvana käyttäytymisenä."""

    def __init__(self, ros_node):
        super().__init__(name="DriveForward")
        self.ros_node = ros_node
        self.publisher = self.ros_node.create_publisher(
            TwistStamped, "/cmd_vel", 10
        )

    def update(self):
        """Julkaise ajokomento sekä ilmaise toiminnon jatkuvan."""
        msg = TwistStamped()
        msg.header.stamp = self.ros_node.get_clock().now().to_msg()
        msg.twist.linear.x = DRIVE_SPEED
        msg.twist.angular.z = 0.0
        self.publisher.publish(msg)
        return py_trees.common.Status.RUNNING
