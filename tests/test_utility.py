import pytest
from pyGizmoServer.utility import makeresolver, loadconfig, ensurelist
from tests.mock_variables import MockVars


resolver = makeresolver(MockVars().mock_schema)


def test_resolver_1():
    props = resolver("/relayController/relays/0")
    assert props == {"w": "setRelay", "args": [0], "$type": "boolean"}


def test_resolver_2():
    props = resolver("/relayController/relays/5")
    assert props == {"w": "setRelay", "args": [5], "$type": "boolean"}


def test_resolver_3():
    props = resolver("/frequencyInputController/frequencyInputs/2/enabled")
    assert props == {"w": "setFrequencyInputEnabled", "args": [2], "$type": "boolean"}


def test_bad_lookup_1():
    assert resolver("/relayController/relays/6") is None


def test_bad_lookup_2():
    assert resolver("/relayController") is None


def test_get_config():
    cfg = loadconfig("mock")
    assert cfg.tcp.ip == "0.0.0.0"
    assert cfg.tcp.ip == "0.0.0.0"
    assert cfg.tcp.port == 36364
    assert cfg.ws.ip == "0.0.0.0"
    assert cfg.ws.port == 11111
    assert cfg.ws.url == "ws://localhost"
    assert cfg.controller == "MockUSB"
    assert cfg.logging.file.loglevel == "DEBUG"
    assert cfg.logging.file.filename == "gizmo.mock.log"
    assert cfg.logging.console.loglevel == "DEBUG"


def test_bad_config():
    with pytest.raises(Exception):
        assert loadconfig("notreal")
