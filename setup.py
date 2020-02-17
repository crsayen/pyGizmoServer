from setuptools import setup

setup(
    name="pyGizmoServer",
    version="1.0.3",
    python_requires=">=3.6",
    packages=[
        "TestCubeUSB",
        "MockUSB",
        "pyGizmoServer",
        "tests",
        "static",
        "templates",
        "config",
        "MockUSB",
        "public",
        "src"
    ],
    install_requires=[
        "jsonpatch",
        "dpath",
        "websockets",
        "aiohttp",
        "aiojobs",
        "jinja2",
        "aiohttp-jinja2",
        "pyusb",
        "pytest",
        "PyYAML",
    ],
    package_data={"schemas": ["*.txt", "*.json"], "": ["*.md"]},
    entry_points={
        "console_scripts": [
            "egizmo=pyGizmoServer.run:main",
            "egizmocli=tests.mock_client:main",
            "ejustusb=TestCubeUSB.justusb:main",
        ]
    },
)
