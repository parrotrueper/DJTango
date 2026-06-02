import os
import signal
import sys
import threading

ROOT = os.path.abspath(os.path.dirname(__file__))
QML_FILE = os.path.join(ROOT, "qml", "Main.qml")


def _install_signal_handlers(app):
    def _quit_app(signum, frame):
        if app is not None:
            app.closeAllWindows()
            app.quit()
        timer = threading.Timer(3.0, lambda: os._exit(0))
        timer.daemon = True
        timer.start()

    signal.signal(signal.SIGINT, _quit_app)
    if hasattr(signal, "SIGTERM"):
        signal.signal(signal.SIGTERM, _quit_app)


def create_app(argv=None):
    from PySide6.QtCore import QTimer, QUrl
    from PySide6.QtQml import QQmlApplicationEngine
    from PySide6.QtWidgets import QApplication

    from djtango.qml_backend import QmlBackend

    app = QApplication(argv or [])
    engine = QQmlApplicationEngine()
    backend = QmlBackend()
    engine.rootContext().setContextProperty("backend", backend)
    qml_file = QML_FILE
    engine.load(QUrl.fromLocalFile(qml_file))
    if not engine.rootObjects():
        raise RuntimeError(f"Failed to load QML file: {qml_file}")

    _install_signal_handlers(app)
    timer = QTimer()
    timer.timeout.connect(lambda: None)
    timer.start(1000)

    return app, engine


if __name__ == "__main__":
    app, engine = create_app(sys.argv)
    sys.exit(app.exec())
