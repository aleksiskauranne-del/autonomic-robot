"""Hybridisen partiorobotin Behavior Treen kokoaminen ja tikitys."""

import py_trees
import rclpy
from rclpy.node import Node

from hybrid_assignment.task1_behaviours import (
    DriveForward,
    IsObstacleTooClose,
    TurnAway,
)


TICK_RATE_HZ = 10.0


class PatrolTreeNode(Node):
    """Rakenna ja aja reaktiivis-deliberatiivinen partiointipuu."""

    def __init__(self):
        super().__init__("patrol_behaviour_tree")

        # Luo puun tehtäväkohtaiset ehdot ja toimintalehdet.
        obstacle_check = IsObstacleTooClose(self)
        turn = TurnAway(self)
        drive = DriveForward(self)

        # Reaktiivinen haara tarkistaa esteen ennen väistötoimintoa.
        reactive_branch = py_trees.composites.Sequence(
            name="Reactive",
            memory=False,
            children=[obstacle_check, turn],
        )

        # Deliberatiivinen haara ajaa eteenpäin, kun este-ehto epäonnistuu.
        deliberative_branch = py_trees.composites.Sequence(
            name="Deliberative",
            memory=False,
            children=[drive],
        )

        # Selector tarkistaa korkeamman prioriteetin reaktiivisen haaran ensin.
        root = py_trees.composites.Selector(
            name="Root",
            memory=False,
            children=[reactive_branch, deliberative_branch],
        )

        # Alusta puu ja ajasta sen päivitys tehtävänannon 10 Hz:n taajuudella.
        self.tree = py_trees.trees.BehaviourTree(root=root)
        self.tree.setup(timeout=15)
        self.tick_timer = self.create_timer(1.0 / TICK_RATE_HZ, self._tick)

        self.get_logger().info("PatrolTree käynnistyi.")
        self.get_logger().info(
            "Puun rakenne:\n"
            + py_trees.display.unicode_tree(root=root, show_status=False)
        )
        self.get_logger().info("Aseta este Webotsissa reaktiivisen haaran testaamiseksi.")

    def _tick(self):
        """Tavuta Behavior Tree kerran ja tulosta sen ajantasainen tila."""
        self.tree.tick()
        print(
            py_trees.display.unicode_tree(
                root=self.tree.root,
                show_status=True,
            )
        )


def main(args=None):
    """Käynnistä ROS 2 -solmu ja pidä sitä ajossa keskeytykseen asti."""
    rclpy.init(args=args)
    node = PatrolTreeNode()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        if rclpy.ok():
            rclpy.shutdown()


if __name__ == "__main__":
    main()
