from setuptools import setup

setup(
    name="dune_rover_demo",
    version="0.1.0",
    packages=["dune_rover_demo"],
    data_files=[("share/ament_index/resource_index/packages", ["resource/dune_rover_demo"]), ("share/dune_rover_demo", ["package.xml"])],
    install_requires=["setuptools"],
    maintainer="Huda Mueen",
    description="Closed loop demonstration for hudasol/dune-rover (simulation only)",
    license="All rights reserved",
    entry_points={"console_scripts": ["smoke_test = dune_rover_demo.nodes:smoke_test"]},
)
