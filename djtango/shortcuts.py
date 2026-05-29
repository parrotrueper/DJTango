from djtango.qt_compat import QShortcut, Qt, QtCore
from djtango.qt_compat import QApplication


class ShortcutsMixin:
    def _createShorcuts(self):
        playSourceOnEnter = QShortcut(self._dialog.milongaSource)
        playSourceOnEnter.setContext(Qt.WidgetShortcut)
        playSourceOnEnter.setKey(QtCore.Qt.Key_Return)
        playSourceOnEnter.activated.connect(self.playSelectedSource)

        displaySideWindowOnCrtlF11 = QShortcut(self)
        displaySideWindowOnCrtlF11.setContext(Qt.WidgetShortcut)
        displaySideWindowOnCrtlF11.setKey(QtCore.Qt.CTRL | QtCore.Qt.Key_F11)
        displaySideWindowOnCrtlF11.activated.connect(self._handelDisplaySideScreen)

        fullScreenOnF11 = QShortcut(self)
        fullScreenOnF11.setContext(Qt.WidgetShortcut)
        fullScreenOnF11.setKey(QtCore.Qt.Key_F11)
        fullScreenOnF11.activated.connect(self._handelFullScren)
