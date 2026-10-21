import os

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

import pytest
from PySide6.QtCore import QCoreApplication, QSettings
from PySide6.QtWidgets import QApplication


@pytest.fixture(scope="session")
def app(tmp_path_factory):
    app = QApplication.instance() or QApplication([])
    # impostazioni in una cartella temporanea: i test non toccano quelle dell'utente
    QCoreApplication.setOrganizationName("WireSheetTests")
    QSettings.setDefaultFormat(QSettings.Format.IniFormat)
    QSettings.setPath(QSettings.Format.IniFormat, QSettings.Scope.UserScope,
                      str(tmp_path_factory.mktemp("settings")))
    return app
