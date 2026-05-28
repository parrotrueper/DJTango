import re

try:
    from PySide6 import QtCore, QtGui, QtWidgets
    from PySide6.QtCore import (
        Qt,
        QThread,
        QObject,
        Signal as pyqtSignal,
        Slot as pyqtSlot,
        QDataStream,
        QIODevice,
        QCoreApplication,
        QModelIndex,
        QAbstractTableModel,
        QSortFilterProxyModel,
    )
    try:
        from PySide6.QtCore import QMutex
    except ImportError:
        class QMutex:
            def __init__(self, *args, **kwargs):
                pass

            def lock(self):
                pass

            def unlock(self):
                pass

            def tryLock(self, timeout=0):
                return True

    try:
        from PySide6.QtCore import QRegExp
    except ImportError:
        from PySide6.QtCore import QRegularExpression as QRegExp
    try:
        from PySide6.QtCore import QVariant
    except ImportError:
        QVariant = object
    from PySide6.QtGui import QColor, QIcon, QPalette, QBrush, QImage, QPainter, QPen, QPainterPath, QShortcut, QAction
    from PySide6.QtWidgets import (
        QMainWindow,
        QProgressDialog,
        QWidget,
        QDialog,
        QMenu,
        QMessageBox,
        QStyleFactory,
        QFileDialog,
        QApplication,
        QAbstractItemView,
        QHeaderView,
        QColorDialog,
        QFrame,
        QSizePolicy,
        QDialogButtonBox,
        QPushButton,
        QCheckBox,
        QLabel,
        QLineEdit,
        QSpinBox,
        QHBoxLayout,
        QVBoxLayout,
        QFormLayout,
    )
    QtWidgets.QAction = QAction
    QtWidgets.QShortcut = QShortcut
    if hasattr(QtWidgets, 'QLCDNumber') and not hasattr(QtWidgets.QLCDNumber, 'setNumDigits') and hasattr(QtWidgets.QLCDNumber, 'setDigitCount'):
        QtWidgets.QLCDNumber.setNumDigits = QtWidgets.QLCDNumber.setDigitCount
    try:
        from PySide6.QtWidgets import QDesktopWidget
    except ImportError:
        from PySide6.QtGui import QGuiApplication

        class QDesktopWidget:
            def __init__(self):
                self._app = QGuiApplication.instance() or QGuiApplication([])

            def screenNumber(self, widget):
                screens = self._app.screens() if hasattr(self._app, 'screens') else []
                return 0 if not screens else 0

            def screenCount(self):
                screens = self._app.screens() if hasattr(self._app, 'screens') else []
                return len(screens) if screens else 1

            def availableGeometry(self, index=0):
                screens = self._app.screens() if hasattr(self._app, 'screens') else []
                if screens and 0 <= index < len(screens):
                    return screens[index].availableGeometry()
                return QtCore.QRect(0, 0, 800, 600)

    try:
        from PySide6.QtMultimedia import QMediaPlayer
    except ImportError:
        QMediaPlayer = object
    try:
        from PySide6.QtMultimedia import QMediaContent
    except ImportError:
        QMediaContent = object
except ImportError:
    class DummySignal:
        def connect(self, *args, **kwargs):
            pass

        def emit(self, *args, **kwargs):
            pass

    def pyqtSignal(*args, **kwargs):
        return DummySignal()

    def pyqtSlot(*args, **kwargs):
        def decorator(fn):
            return fn

        return decorator

    class QObject:
        def __init__(self, *args, **kwargs):
            pass

    class QModelIndex:
        def __init__(self, row=-1, column=-1, valid=False):
            self._row = row
            self._column = column
            self._valid = valid

        def row(self):
            return self._row

        def column(self):
            return self._column

        def isValid(self):
            return self._valid

    class QAbstractTableModel(QObject):
        def __init__(self, parent=None, *args, **kwargs):
            super().__init__()
            self.layoutAboutToBeChanged = DummySignal()
            self.layoutChanged = DummySignal()
            self.dataChanged = DummySignal()

        def createIndex(self, row, col, valid=True):
            return QModelIndex(row, col, valid)

        def index(self, row, col, parent=None):
            return self.createIndex(row, col)

    class QSortFilterProxyModel(QObject):
        def __init__(self, parent=None):
            super().__init__()
            self._sourceModel = None
            self._genre = ''
            self._regex = re.compile('.*')
            self._filterKeyColumn = 0

        def setSourceModel(self, source):
            self._sourceModel = source

        def sourceModel(self):
            return self._sourceModel

        def setFilterKeyColumn(self, column):
            self._filterKeyColumn = column

        def setlFilterValues(self, title, genre, album, regex):
            self._genre = genre
            try:
                self._regex = re.compile(regex)
            except re.error:
                self._regex = re.compile('.*')

        def filterAcceptsRow(self, row, parent):
            if self._sourceModel is None:
                return False
            index = self._sourceModel.index(row, 5)
            value = self._sourceModel.data(index, Qt.DisplayRole)
            return value == self._genre

    class QColor:
        def __init__(self, r=0, g=0, b=0, a=255):
            self._r = r
            self._g = g
            self._b = b
            self._a = a

        @classmethod
        def fromRgb(cls, r, g, b, a=255):
            return cls(r, g, b, a)

        def red(self):
            return self._r

        def green(self):
            return self._g

        def blue(self):
            return self._b

        def alpha(self):
            return self._a

    class QIcon:
        def __init__(self, *args, **kwargs):
            pass

        def addPixmap(self, *args, **kwargs):
            pass

    class QPalette:
        Base = 0
        Highlight = 1
        Window = 2
        AlternateBase = 3
        Shadow = 4
        Text = 5

        def __init__(self, *args, **kwargs):
            pass

        def setColor(self, *args, **kwargs):
            pass

    class QBrush:
        def __init__(self, *args, **kwargs):
            pass

        def setStyle(self, *args, **kwargs):
            pass

    class QImage:
        Format_ARGB32 = 0

        def __init__(self, *args, **kwargs):
            pass

        def fill(self, *args, **kwargs):
            pass

    class QPainter:
        Antialiasing = 1
        CompositionMode_Source = 1

        def __init__(self, *args, **kwargs):
            pass

        def setRenderHint(self, *args, **kwargs):
            pass

        def setBrush(self, *args, **kwargs):
            pass

        def setPen(self, *args, **kwargs):
            pass

        def drawEllipse(self, *args, **kwargs):
            pass

        def drawPath(self, *args, **kwargs):
            pass

        def drawImage(self, *args, **kwargs):
            pass

        def drawArc(self, *args, **kwargs):
            pass

        def fillRect(self, *args, **kwargs):
            pass

        def end(self):
            pass

        def setCompositionMode(self, *args, **kwargs):
            pass

    class QPen:
        def __init__(self, *args, **kwargs):
            pass

    class QPainterPath:
        def __init__(self, *args, **kwargs):
            pass

        def setFillRule(self, *args, **kwargs):
            pass

        def moveTo(self, *args, **kwargs):
            pass

        def arcTo(self, *args, **kwargs):
            pass

        def lineTo(self, *args, **kwargs):
            pass

    class QRectF:
        def __init__(self, *args, **kwargs):
            pass

        def adjusted(self, *args, **kwargs):
            return self

    class QPixmap:
        def __init__(self, *args, **kwargs):
            pass

    class QMainWindow(QObject):
        def __init__(self, *args, **kwargs):
            super().__init__()

    class QProgressDialog(QObject):
        pass

    class QShortcut(QObject):
        def __init__(self, *args, **kwargs):
            super().__init__()

    class QWidget(QObject):
        def __init__(self, *args, **kwargs):
            super().__init__()

        def setWindowFlags(self, flags):
            pass

    class QDialog(QWidget):
        pass

    class QMenu(QWidget):
        pass

    class QMessageBox(QWidget):
        pass

    class QFileDialog(QWidget):
        pass

    class QAction(QObject):
        pass

    class QAbstractItemView(QWidget):
        pass

    class QHeaderView(QWidget):
        pass

    class QColorDialog(QWidget):
        pass

    class QDesktopWidget(QWidget):
        pass

    class QThread(QObject):
        def __init__(self, *args, **kwargs):
            super().__init__()

    class QMediaPlayer(QObject):
        def __init__(self, *args, **kwargs):
            super().__init__()

    class QMediaContent(QObject):
        def __init__(self, *args, **kwargs):
            super().__init__()

    class QDataStream:
        pass

    class QIODevice:
        pass

    class QRegExp:
        def __init__(self, pattern=''):
            self._pattern = re.compile(pattern)

        def indexIn(self, text):
            return self._pattern.search(text) is not None

    class QVariant(object):
        pass

    class QtClass:
        ApplicationModal = 1
        WindowModal = 2
        WidgetShortcut = 3
        FramelessWindowHint = 4
        SolidPattern = 5
        Key_Return = 6
        Key_F11 = 7
        CTRL = 0x01000000
        Horizontal = 1
        DisplayRole = 0
        BackgroundRole = 1
        EditRole = 2
        AscendingOrder = 0
        DescendingOrder = 1
        ItemIsDragEnabled = 2
        ItemIsEnabled = 4
        ItemIsSelectable = 8
        Checked = 2
        Unchecked = 0
        PartiallyChecked = 1
        NoBrush = 0
        WindingFill = 0

    Qt = QtClass()

    class DummyStyle:
        def objectName(self):
            return 'Fusion'

        def standardPalette(self):
            return QPalette()

    class QApplication:
        def __init__(self, argv=None):
            pass

        def style(self):
            return DummyStyle()

        def setPalette(self, palette):
            pass

        def setStyleSheet(self, stylesheet):
            pass

        def exec_(self):
            return 0

    class QStyleFactory:
        @staticmethod
        def create(name):
            return DummyStyle()

    class QFrame:
        HLine = 1
        Sunken = 2

    class QSizePolicy:
        Minimum = 0
        Expanding = 1

    class QDialogButtonBox:
        Cancel = 1
        Ok = 2

    class QPushButton(QWidget):
        pass

    class QCheckBox(QWidget):
        pass

    class QLabel(QWidget):
        pass

    class QLineEdit(QWidget):
        pass

    class QSpinBox(QWidget):
        pass

    class QHBoxLayout(object):
        def __init__(self, *args, **kwargs):
            pass

        def addWidget(self, *args, **kwargs):
            pass

        def setObjectName(self, *args, **kwargs):
            pass

    class QVBoxLayout(QHBoxLayout):
        pass

    class QFormLayout(QHBoxLayout):
        pass

    QtCore = type('QtCore', (), {
        'Qt': Qt,
        'QMetaObject': type('QMetaObject', (), {'connectSlotsByName': staticmethod(lambda x: None)}),
        'QString': str,
        'QRectF': QRectF,
        'QRegExp': QRegExp,
        'QCoreApplication': type('QCoreApplication', (), {'translate': staticmethod(lambda a, b, c=None: b), 'instance': staticmethod(lambda: None)}),
        'qRegisterResourceData': staticmethod(lambda *args, **kwargs: None),
        'qUnregisterResourceData': staticmethod(lambda *args, **kwargs: None),
    })

    QtGui = type('QtGui', (), {
        'QColor': QColor,
        'QIcon': QIcon,
        'QPalette': QPalette,
        'QBrush': QBrush,
        'QImage': QImage,
        'QPainter': QPainter,
        'QPen': QPen,
        'QPainterPath': QPainterPath,
        'QPixmap': QPixmap,
    })

    QtWidgets = type('QtWidgets', (), {
        'QMainWindow': QMainWindow,
        'QProgressDialog': QProgressDialog,
        'QShortcut': QShortcut,
        'QWidget': QWidget,
        'QDialog': QDialog,
        'QMenu': QMenu,
        'QMessageBox': QMessageBox,
        'QStyleFactory': QStyleFactory,
        'QFileDialog': QFileDialog,
        'QAction': QAction,
        'QApplication': QApplication,
        'QDesktopWidget': QDesktopWidget,
        'QAbstractItemView': QAbstractItemView,
        'QHeaderView': QHeaderView,
        'QColorDialog': QColorDialog,
        'QFrame': QFrame,
        'QSizePolicy': QSizePolicy,
        'QDialogButtonBox': QDialogButtonBox,
        'QPushButton': QPushButton,
        'QCheckBox': QCheckBox,
        'QLabel': QLabel,
        'QLineEdit': QLineEdit,
        'QSpinBox': QSpinBox,
        'QHBoxLayout': QHBoxLayout,
        'QVBoxLayout': QVBoxLayout,
        'QFormLayout': QFormLayout,
    })

    QDesktopWidget = QDesktopWidget
    QThread = QThread
    QObject = QObject
    QFileDialog = QFileDialog
    QIcon = QIcon
    QAction = QAction
    QAbstractItemView = QAbstractItemView
    QHeaderView = QHeaderView
    QColorDialog = QColorDialog
    QPalette = QPalette
    QSortFilterProxyModel = QSortFilterProxyModel
    QMediaPlayer = QMediaPlayer
    QMediaContent = QMediaContent
    QMainWindow = QMainWindow
    QProgressDialog = QProgressDialog
    QShortcut = QShortcut
    QWidget = QWidget
    QDialog = QDialog
    QMenu = QMenu
    QMessageBox = QMessageBox
    QStyleFactory = QStyleFactory
    QApplication = QApplication
    QAbstractTableModel = QAbstractTableModel
    QColor = QColor
    QDataStream = QDataStream
    QIODevice = QIODevice
    QVariant = QVariant
    QRegExp = QRegExp
    QBrush = QBrush
    QImage = QImage
    QPainter = QPainter
    QPen = QPen
    QPainterPath = QPainterPath
    QRectF = QRectF
    QPixmap = QPixmap
    QFrame = QFrame
    QSizePolicy = QSizePolicy
    QDialogButtonBox = QDialogButtonBox
    QPushButton = QPushButton
    QCheckBox = QCheckBox
    QLabel = QLabel
    QLineEdit = QLineEdit
    QSpinBox = QSpinBox
    QHBoxLayout = QHBoxLayout
    QVBoxLayout = QVBoxLayout
    QFormLayout = QFormLayout
    QtCore = QtCore
    QtGui = QtGui
    QtWidgets = QtWidgets
    Qt = Qt
