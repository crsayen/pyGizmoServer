from setuptools import setup

setup(
    name="pyGizmoServer",
    version="1.0.2",
    python_requires=">=3.7",
    packages=[
        "TestCubeUSB",
        "MockUSB",
        "pyGizmoServer",
        "tests",
        "static",
        "templates",
        "config",
        "MockUSB",
    ],
    install_requires=[
        "jsonpatch",
        "dpath",
        "websockets",
        "aiohttp",
        "jinja2",
        "aiohttp-jinja2",
        "pyusb",
        "aiojobs",
        "pytest",
        "app-settings",
        "pep8-naming",
    ],
    package_data={"schemas": ["*.txt", "*.json"], "": ["*.md"]},
    entry_points={"console_scripts": ["gizmo=pyGizmoServer.run:main"]},
)
