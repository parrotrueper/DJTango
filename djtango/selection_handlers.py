from djtango.qt_compat import Qt


class SelectionHandlerMixin:
    def _handleLibrarySelectionChanged(self, selected, deselected):
        if self._isMilongaPlaying:
            return
        self._updateSelectedLibraryRow()

    def _handleLibrarySelectionClicked(self, index):
        if self._isMilongaPlaying:
            return
        if index.isValid():
            self._updateSelectedLibraryRow()

    def _updateSelectedLibraryRow(self):
        indexes = self._dialog.milongaSource.selectionModel().selectedRows()
        if len(indexes) == 1:
            self._currentIndex = self.sourceProxyModel.data(indexes[0], Qt.DisplayRole)
            self.curLibraryRow = indexes[0].row()
            self.curTango = self._tangoList.tangos[self._currentIndex]
            self._updateSideScreen()
            self.update_tango_infos(self.curTango)
            if self.propWindow.isVisible():
                self.updateTangoProp()
        elif len(indexes) == 0:
            self.curTango = None
            self._updateSideScreen()
