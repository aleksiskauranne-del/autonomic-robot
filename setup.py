"""ROS 2 -paketin asennusmääritykset."""

import os
from glob import glob

from setuptools import find_packages, setup


package_name = "hybrid_assignment"

setup(
	name=package_name,
	version="0.0.1",
	packages=find_packages(exclude=["test"]),
	data_files=[
		(
			"share/ament_index/resource_index/packages",
			["resource/" + package_name],
		),
		(os.path.join("share", package_name), ["package.xml"]),
		(
			os.path.join("share", package_name, "launch"),
			glob("launch/*.launch.py"),
		),
		(
			os.path.join("share", package_name, "resource"),
			glob("resource/*"),
		),
		(
			os.path.join("share", package_name, "worlds"),
			glob("worlds/*.wbt"),
		),
	],
	install_requires=["setuptools"],
	zip_safe=True,
	maintainer="Student",
	maintainer_email="student@example.com",
	description="Hybridinen ROS 2 -tehtävä Behavior Tree -arkkitehtuurista",
	license="Apache-2.0",
	tests_require=["pytest"],
	entry_points={
		"console_scripts": [
			"task2_tree = hybrid_assignment.task2_tree:main",
		],
	},
)
