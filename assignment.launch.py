"""Käynnistä Webotsin TurtleBot-ohjain ja Behavior Tree -solmu."""

import os

import launch
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch_ros.actions import Node
from webots_ros2_driver.webots_controller import WebotsController


def generate_launch_description():
    """Luo launch kuvaus avoinna olevaan Webots-maailmaan liittymiseksi."""
    package_share = get_package_share_directory("hybrid_assignment")
    robot_description = os.path.join(
        package_share, "resource", "TurtleBot3Burger.urdf"
    )

    # Liitä TurtleBot3Burgerin Webots laitteet ROS 2 aiheisiin.
    webots_controller = WebotsController(
        robot_name="TurtleBot3Burger",
        parameters=[{"robot_description": robot_description}],
        output="screen",
    )

    # Käynnistä Behavior Tree, joka ohjaa robottia /cmd_vel aiheen kautta.
    behaviour_tree = Node(
        package="hybrid_assignment",
        executable="task2_tree",
        name="hybrid_behaviour_tree",
        output="screen",
    )

    # Sulje ROS launch jos Webots ohjain päättyy.
    shutdown_on_controller_exit = launch.actions.RegisterEventHandler(
        event_handler=launch.event_handlers.OnProcessExit(
            target_action=webots_controller,
            on_exit=[
                launch.actions.EmitEvent(event=launch.events.Shutdown())
            ],
        )
    )

    return LaunchDescription(
        [webots_controller, behaviour_tree, shutdown_on_controller_exit]
    )
