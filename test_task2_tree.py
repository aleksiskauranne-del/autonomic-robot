"""Task 2 Behavior Tree rakenne sekä prioriteetin testaus."""

import math
import time

import py_trees
import pytest
import rclpy
from sensor_msgs.msg import LaserScan

from hybrid_assignment.task2_tree import PatrolTreeNode, TICK_RATE_HZ


@pytest.fixture(scope="module", autouse=True)
def ros_context():
    """Käynnistä ROS 2 testimoduuliin. Lopuksi sulje se."""
    rclpy.init()
    yield
    rclpy.shutdown()


@pytest.fixture(name="patrol_node")
def patrol_node_fixture():
    """Luo testisolmu sekä vapauta sen ROS-resurssit testin jälkeen."""
    node = PatrolTreeNode()
    yield node
    node.destroy_node()


def make_scan(front_distance=math.inf):
    """Luo testiskannaus, jonka indeksi 0 osoittaa robotin taakse."""
    scan = LaserScan()
    scan.angle_min = -math.pi
    scan.angle_increment = math.tau / 360
    scan.ranges = [math.inf] * 360
    scan.ranges[180] = front_distance
    return scan


def test_tree_has_reactive_priority_over_deliberative_branch(patrol_node):
    root = patrol_node.tree.root
    reactive_branch, deliberative_branch = root.children

    assert isinstance(root, py_trees.composites.Selector)
    assert [child.name for child in root.children] == [
        "Reactive",
        "Deliberative",
    ]
    assert [child.name for child in reactive_branch.children] == [
        "IsObstacleTooClose",
        "TurnAway",
    ]
    assert [child.name for child in deliberative_branch.children] == [
        "DriveForward",
    ]
    assert patrol_node.tick_timer.timer_period_ns == int(1e9 / TICK_RATE_HZ)


def test_clear_path_runs_drive_forward(patrol_node):
    root = patrol_node.tree.root
    reactive_branch, deliberative_branch = root.children
    obstacle_check, turn = reactive_branch.children
    drive = deliberative_branch.children[0]
    obstacle_check.latest_scan = make_scan()

    patrol_node.tree.tick()

    assert root.status is py_trees.common.Status.RUNNING
    assert reactive_branch.status is py_trees.common.Status.FAILURE
    assert turn.status is py_trees.common.Status.INVALID
    assert deliberative_branch.status is py_trees.common.Status.RUNNING
    assert drive.status is py_trees.common.Status.RUNNING


def test_obstacle_preempts_drive_and_clear_path_resumes_it(patrol_node):
    root = patrol_node.tree.root
    reactive_branch, deliberative_branch = root.children
    obstacle_check, turn = reactive_branch.children
    drive = deliberative_branch.children[0]
    scan = make_scan(front_distance=0.25)
    obstacle_check.latest_scan = scan

    patrol_node.tree.tick()

    assert reactive_branch.status is py_trees.common.Status.RUNNING
    assert obstacle_check.status is py_trees.common.Status.SUCCESS
    assert turn.status is py_trees.common.Status.RUNNING
    assert deliberative_branch.status is py_trees.common.Status.INVALID
    assert drive.status is py_trees.common.Status.INVALID

    scan.ranges[180] = math.inf
    patrol_node.tree.tick()

    assert reactive_branch.status is py_trees.common.Status.FAILURE
    assert turn.status is py_trees.common.Status.INVALID
    assert deliberative_branch.status is py_trees.common.Status.RUNNING
    assert drive.status is py_trees.common.Status.RUNNING


def test_timer_ticks_and_prints_tree_with_runtime_statuses(patrol_node, capsys):
    deadline = time.monotonic() + 1.0
    while patrol_node.tree.count == 0 and time.monotonic() < deadline:
        rclpy.spin_once(patrol_node, timeout_sec=0.05)

    output = capsys.readouterr().out

    assert "Root" in output
    assert "Reactive" in output
    assert "Deliberative" in output
    assert patrol_node.tree.count >= 1