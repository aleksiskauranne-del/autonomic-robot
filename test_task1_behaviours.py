"""Task 1:n lehtikäyttäytymisten toiminnalliset testit."""

import math
from types import SimpleNamespace

import py_trees
import pytest
from builtin_interfaces.msg import Time
from geometry_msgs.msg import TwistStamped
from sensor_msgs.msg import LaserScan

from hybrid_assignment.task1_behaviours import (
    DRIVE_SPEED,
    TURN_SPEED,
    DriveForward,
    IsObstacleTooClose,
    TurnAway,
)


class RecordingPublisher:
    """Tallenna testissä julkaistut viestit."""

    def __init__(self):
        self.messages = []

    def publish(self, message):
        self.messages.append(message)


class FakeRosNode:
    """Tarjoa lehtikäyttäytymille rajattu ROS-solmun testikorvike."""

    def __init__(self):
        self.publishers = {}
        self.subscription_callback = None
        self.stamp = Time(sec=1, nanosec=2)

    def create_subscription(self, message_type, topic, callback, queue_size):
        assert message_type is LaserScan
        assert topic == "/scan"
        assert queue_size == 10
        self.subscription_callback = callback
        return object()

    def create_publisher(self, message_type, topic, queue_size):
        assert message_type is TwistStamped
        assert topic == "/cmd_vel"
        assert queue_size == 10
        publisher = RecordingPublisher()
        self.publishers[topic] = publisher
        return publisher

    def get_clock(self):
        return SimpleNamespace(
            now=lambda: SimpleNamespace(to_msg=lambda: self.stamp)
        )


def make_scan():
    """Luo 360 lukeman skannaus, jossa indeksi 0 osoittaa taakse."""
    scan = LaserScan()
    scan.angle_min = -math.pi
    scan.angle_increment = math.tau / 360
    scan.ranges = [math.inf] * 360
    return scan


def test_missing_scan_and_clear_path_return_failure():
    node = FakeRosNode()
    behaviour = IsObstacleTooClose(node)

    assert behaviour.update() is py_trees.common.Status.FAILURE

    node.subscription_callback(make_scan())
    assert behaviour.update() is py_trees.common.Status.FAILURE


def test_obstacles_behind_and_outside_forward_arc_are_ignored():
    node = FakeRosNode()
    behaviour = IsObstacleTooClose(node)
    scan = make_scan()
    scan.ranges[0] = 0.1
    scan.ranges[149] = 0.1
    node.subscription_callback(scan)

    assert behaviour.update() is py_trees.common.Status.FAILURE


@pytest.mark.parametrize("index", [150, 180, 210])
def test_obstacle_inside_forward_arc_returns_success(index):
    node = FakeRosNode()
    behaviour = IsObstacleTooClose(node)
    scan = make_scan()
    scan.ranges[index] = 0.25
    node.subscription_callback(scan)

    assert behaviour.update() is py_trees.common.Status.SUCCESS


@pytest.mark.parametrize("distance", [math.inf, math.nan, 0.0, -0.1, 0.5])
def test_invalid_or_threshold_distance_does_not_trigger(distance):
    node = FakeRosNode()
    behaviour = IsObstacleTooClose(node)
    scan = make_scan()
    scan.ranges[180] = distance
    node.subscription_callback(scan)

    assert behaviour.update() is py_trees.common.Status.FAILURE


def test_turn_away_publishes_a_stamped_spin_in_place_command():
    node = FakeRosNode()
    behaviour = TurnAway(node)

    assert behaviour.update() is py_trees.common.Status.RUNNING

    message = node.publishers["/cmd_vel"].messages[-1]
    assert message.header.stamp == node.stamp
    assert message.twist.linear.x == 0.0
    assert message.twist.angular.z == TURN_SPEED


@pytest.mark.parametrize(
    ("blocked_index", "expected_direction"),
    [(240, -1.0), (120, 1.0)],
)
def test_turn_away_selects_the_clearer_side(blocked_index, expected_direction):
    node = FakeRosNode()
    behaviour = TurnAway(node)
    scan = make_scan()
    scan.ranges[blocked_index] = 0.25
    node.subscription_callback(scan)

    behaviour.initialise()
    assert behaviour.update() is py_trees.common.Status.RUNNING

    message = node.publishers["/cmd_vel"].messages[-1]
    assert message.twist.linear.x == 0.0
    assert message.twist.angular.z == expected_direction * TURN_SPEED


def test_drive_forward_publishes_forward_command_and_keeps_running():
    node = FakeRosNode()
    behaviour = DriveForward(node)

    assert behaviour.update() is py_trees.common.Status.RUNNING

    message = node.publishers["/cmd_vel"].messages[-1]
    assert message.header.stamp == node.stamp
    assert message.twist.linear.x == DRIVE_SPEED
    assert message.twist.angular.z == 0.0