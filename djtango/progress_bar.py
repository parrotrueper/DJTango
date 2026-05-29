from djtango.circularprogressbar import QRoundProgressBar
from djtango.qt_compat import QColor, QPalette, QtGui


class ProgressBarMixin:
    def _setup_progress_bar(self):
        pbPalette = QPalette()
        pbPalette.setColor(QPalette.Base, QtGui.QColor.fromRgb(42, 42, 42))
        pbPalette.setColor(QPalette.Highlight, QtGui.QColor.fromRgb(160, 52, 77))
        pbPalette.setColor(QPalette.Window, QtGui.QColor.fromRgb(160, 52, 77, 0))
        pbPalette.setColor(QPalette.AlternateBase, QtGui.QColor.fromRgb(160, 52, 77, 0))
        pbPalette.setColor(QPalette.Shadow, QtGui.QColor.fromRgb(160, 52, 77, 0))
        pbPalette.setColor(QPalette.Text, QtGui.QColor.fromRgb(255, 255, 255))

        self.bar = QRoundProgressBar()
        self.bar.setPalette(pbPalette)
        self.bar.setFixedSize(140, 140)
        self.bar.setDataPenWidth(10)
        self.bar.setOutlinePenWidth(3)
        self.bar.setDonutThicknessRatio(0.7)
        self.bar.setDecimals(1)
        self.bar.setFormat('%t')
        self.bar.setNullPosition(90)
        self.bar.setBarStyle(QRoundProgressBar.StyleDonut)
        self.bar.setDataColors([(1., QtGui.QColor.fromRgb(160, 52, 77)), ])
        self.bar.setRange(0, 100)
        self.bar.setValue(75)
