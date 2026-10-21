import json

import pytest
from PySide6.QtWidgets import QMessageBox

from wiresheet import RELEASES_URL, __version__
from wiresheet.ui.main_window import MainWindow
from wiresheet.ui.update_check import is_newer, parse_version, release_from_json


def test_version_is_semver():
    assert parse_version(__version__) is not None and len(parse_version(__version__)) == 3


@pytest.mark.parametrize("text, expected", [
    ("1.0.0", (1, 0, 0)), ("v2.10.3", (2, 10, 3)), (" v1.2 ", (1, 2)),
    ("1.0.0-beta", None), ("latest", None), ("", None),
])
def test_parse_version(text, expected):
    assert parse_version(text) == expected


@pytest.mark.parametrize("latest, current, newer", [
    ("1.0.1", "1.0.0", True), ("v1.1.0", "1.0.9", True), ("2.0", "1.9.9", True),
    ("1.10.0", "1.9.0", True),  # confronto numerico, non alfabetico
    ("1.0.0", "1.0.0", False), ("1.0", "1.0.0", False), ("0.9.0", "1.0.0", False),
    ("nightly", "1.0.0", False),
])
def test_is_newer(latest, current, newer):
    assert is_newer(latest, current) is newer


def test_release_from_json():
    payload = json.dumps({"tag_name": "v1.2.0",
                          "html_url": f"{RELEASES_URL}/tag/v1.2.0"}).encode()
    assert release_from_json(payload) == ("1.2.0", f"{RELEASES_URL}/tag/v1.2.0")
    assert release_from_json(b'{"tag_name": "v1.3.0"}')[1] == f"{RELEASES_URL}/tag/v1.3.0"
    with pytest.raises(KeyError):
        release_from_json(b"{}")


@pytest.fixture
def window(app):
    w = MainWindow()
    yield w
    w._dirty = False
    w.close()


def test_update_found_opens_release_page_only_if_confirmed(window, monkeypatch):
    opened = []
    monkeypatch.setattr("wiresheet.ui.main_window.QDesktopServices.openUrl",
                        lambda url: opened.append(url.toString()))
    url = f"{RELEASES_URL}/tag/v9.0.0"
    monkeypatch.setattr("wiresheet.ui.main_window.QMessageBox.question",
                        lambda *a: QMessageBox.StandardButton.No)
    window._on_update_found("9.0.0", url)
    assert opened == []
    monkeypatch.setattr("wiresheet.ui.main_window.QMessageBox.question",
                        lambda *a: QMessageBox.StandardButton.Yes)
    window._on_update_found("9.0.0", url)
    assert opened == [url]


def test_silent_check_shows_nothing_when_up_to_date_or_offline(window, monkeypatch):
    shown = []
    monkeypatch.setattr("wiresheet.ui.main_window.QMessageBox.information",
                        lambda *a: shown.append("info"))
    monkeypatch.setattr("wiresheet.ui.main_window.QMessageBox.warning",
                        lambda *a: shown.append("warning"))
    window._silent_check = True
    window._on_up_to_date()
    window._on_update_failed("offline")
    assert shown == []
    window._silent_check = False
    window._on_up_to_date()
    window._on_update_failed("offline")
    assert shown == ["info", "warning"]


def test_auto_update_setting_persists(app):
    first = MainWindow()
    assert first.act_auto_update.isChecked()  # attivo di default
    first.act_auto_update.setChecked(False)
    first.close()
    second = MainWindow()
    assert not second.auto_update_enabled() and not second.act_auto_update.isChecked()
    second.act_auto_update.setChecked(True)
    second.close()

