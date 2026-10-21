"""Controllo aggiornamenti: chiede a GitHub l'ultima release e la confronta con __version__.

Non scarica nulla: se c'e' una versione nuova, la finestra propone di aprire la pagina della release."""

import json
import re

from PySide6.QtCore import QObject, QUrl, Signal
from PySide6.QtNetwork import QNetworkAccessManager, QNetworkReply, QNetworkRequest

from wiresheet import REPOSITORY, RELEASES_URL, __version__

LATEST_API = f"https://api.github.com/repos/{REPOSITORY}/releases/latest"
TIMEOUT_MS = 10_000


def parse_version(text: str) -> tuple[int, ...] | None:
    """'v1.2.3' / '1.2' → (1, 2, 3) / (1, 2); None se non e' una versione numerica."""
    match = re.fullmatch(r"v?(\d+(?:\.\d+)*)", text.strip())
    return tuple(int(part) for part in match.group(1).split(".")) if match else None


def is_newer(latest: str, current: str = __version__) -> bool:
    a, b = parse_version(latest), parse_version(current)
    if a is None or b is None:
        return False
    width = max(len(a), len(b))  # 1.0 == 1.0.0
    return a + (0,) * (width - len(a)) > b + (0,) * (width - len(b))


def release_from_json(payload: bytes) -> tuple[str, str]:
    """(versione, pagina della release) dalla risposta di releases/latest."""
    data = json.loads(payload)
    tag = data["tag_name"]
    return tag.lstrip("v"), data.get("html_url") or f"{RELEASES_URL}/tag/{tag}"


class UpdateChecker(QObject):
    """Una richiesta alla volta; emette found(versione, url), up_to_date() oppure failed(messaggio)."""

    found = Signal(str, str)
    up_to_date = Signal()
    failed = Signal(str)

    def __init__(self, parent: QObject | None = None):
        super().__init__(parent)
        self._network = QNetworkAccessManager(self)
        self._reply: QNetworkReply | None = None

    def check(self) -> None:
        if self._reply is not None:
            return
        request = QNetworkRequest(QUrl(LATEST_API))
        request.setRawHeader(b"Accept", b"application/vnd.github+json")
        request.setRawHeader(b"User-Agent", f"WireSheet/{__version__}".encode())
        request.setTransferTimeout(TIMEOUT_MS)
        self._reply = self._network.get(request)
        self._reply.finished.connect(self._on_finished)

    def _on_finished(self) -> None:
        reply, self._reply = self._reply, None
        reply.deleteLater()
        if reply.attribute(QNetworkRequest.Attribute.HttpStatusCodeAttribute) == 404:
            self.failed.emit("Non ci sono ancora release pubblicate.")
            return
        if reply.error() != QNetworkReply.NetworkError.NoError:
            self.failed.emit(f"Controlla la connessione a internet.\n({reply.errorString()})")
            return
        try:
            version, url = release_from_json(bytes(reply.readAll()))
        except (ValueError, KeyError, TypeError) as e:
            self.failed.emit(f"Risposta non valida da GitHub ({e}).")
            return
        if is_newer(version):
            self.found.emit(version, url)
        else:
            self.up_to_date.emit()
