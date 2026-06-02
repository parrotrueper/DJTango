import os

from djtango.UI_djtango import Ui_AudioPlayerDialog
from djtango.qt_compat import QWidget, QDialog, QIcon, QHeaderView, QModelIndex
from djtango import tableModels

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))


class UISetupMixin:
    def _createUI(self):
        self._dialog = Ui_AudioPlayerDialog()
        self._dialog.setupUi(self)

        icon_path = os.path.join(ROOT, 'gui', 'img', 'djt.ico')
        if os.path.exists(icon_path):
            self.setWindowIcon(QIcon(icon_path))

        self._dialog.retranslateUi(self)
        self._setup_track_customization()
        self.playIcon = QIcon('./djtango/img/play-button.png')
        self.pauseIcon = QIcon('./djtango/img/pause-button.png')

        libraryHeader = ['#', ' ', 'Title', 'Artist', 'Album', 'Genre', 'Year', 'BPM', 'Time']
        libraryData = [track.list() for track in self._tangoList.tracks.values()]

        self.sourceModel = tableModels.milongaSource(self, libraryData, libraryHeader, self.TYPE)
        self.sourceProxyModel = tableModels.sourceFilterProxyModel(self)
        self.sourceProxyModel.setSourceModel(self.sourceModel)
        self._dialog.milongaSource.setModel(self.sourceProxyModel)
        self._dialog.milongaSource.horizontalHeader().setSectionResizeMode(QHeaderView.Fixed)

        self.destModel = tableModels.milongaDest(self, [], libraryHeader, self.TYPE)
        self._dialog.milongaDest.setModel(self.destModel)
        self._dialog.milongaDest.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)

        self._dialog.labelsongNB_source.setText(str(self.sourceProxyModel.rowCount(QModelIndex())) + ' track(s)')

        self._setup_tap_window()
        self._setup_track_details_window()
        self._setup_side_window()
        self._setup_info_window()
        self._setup_info_milonga_window()
        self._setup_milonga_select_dialog()
        self._setup_milonga_name_dialog()
        self._setup_ask_delete_dialog()

        self._setup_preferences_window()

        self.set_list_of_type()
        self.set_list_of_artist()
        self.setListOfAlbum()
