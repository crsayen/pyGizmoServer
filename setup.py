from setuptools import setup

setup(
    name="pyGizmoServer",
    version="0.1.0",
    python_requires=">=3.7",
    packages=[
        "controllers",
        "pyGizmoServer",
        "schemas",
        "controllers.TestCubeComponents"
    ],
    install_requires=["jsonpatch", "dpath", "websockets", "aiohttp", "aiojobs"],
    package_data={"schemas": ["*.txt", "*.json"], "": ["*.md"]},
    entry_points={
        "console_scripts": [
            "gizmo=pyGizmoServer.run:main"
        ]
    },
)