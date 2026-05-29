class ConnectionsMixin:
    def _connect(self):
        self._connect_library_scanner()

        self._dialog.actionPreferences.triggered.connect(self._handelPrefClose)
        self._dialog.actionTrackAppearance.triggered.connect(self._openTrackAppearanceDialog)
        self._dialog.actionEdit_details_of_current_song.triggered.connect(self.handelOpenPropWidow)
        self._dialog.actionLoad_BPM_from_ID3_Tag.triggered.connect(self._load_bpm_from_id3_tag)
        self._dialog.actionTap_yourself_BPM.triggered.connect(self._handelBpmTappingAction)

        self._dialog.actionFullscreen.triggered.connect(self._handelFullScren)

        self._dialog.actionImport_file.triggered.connect(self.open_files_dialog)
        self._dialog.actionImport_directory.triggered.connect(self.open_file_dialog)

        self._dialog.actionDisplay_side_screen.setChecked(False)
        self._dialog.actionDisplay_side_screen.triggered.connect(self._handelDisplaySideScreen)

        self._dialog.milongaSource.resizeEvent = self.resizeHeaderSource

        self.destModel.dataChanged.connect(self.updateMilongaInfos)
        self.destModel.rowsRemoved.connect(self.updateMilongaInfos)

        self.tapContent.tapButton.pressed.connect(self._handelBpmTapping)
        self.tapContent.validate.clicked.connect(self._handelValidatebpm)
        self.tapContent.cancel.clicked.connect(self._handelCancelbpm)
        self.tapContent.next.clicked.connect(self._handelTapingNext)
        self.tapContent.previous.clicked.connect(self._handelTapingPrevious)

        self.prefContent.addTypeButton.clicked.connect(self._addTangoType)
        self.prefContent.removeTypeButton.clicked.connect(self._removeTangoType)
        self.prefContent.pushButtonSelectPath.clicked.connect(self.open_file_dialog)

        self.info_thread.finished.connect(self.closeInfo)

        self._dialog.playToolButton.clicked.connect(self._handelPlayPause)
        self._dialog.checkBoxLetCortinaUntilEnd.clicked.connect(self.handle_cortina_checkbox)

        self._dialog.lineEditFilter.returnPressed.connect(self._handel_filter_change)
        self._dialog.pushButtonRandom.clicked.connect(self.sourceModel.randomize)

        self._dialog.milongaDest.pressed.connect(self.destModel.pressed)

        self.infoContent.pushButtonClose.clicked.connect(self.closeInfo)

        self.detailsContent.closeButton.clicked.connect(self._handlePropWindowClose)
        self.detailsContent.nextButton.clicked.connect(self._handlePropWindowNext)
        self.detailsContent.previousButton.clicked.connect(self._handlePropWindowPrevious)

        self.player.durationChanged.connect(self.durationChanged)
        self.player.positionChanged.connect(self.position_changed)
        if hasattr(self.player, 'playbackStateChanged'):
            self.player.playbackStateChanged.connect(self._handel_state_changed)
        else:
            self.player.stateChanged.connect(self._handel_state_changed)

        self._dialog.songSlider.sliderMoved.connect(self.seek)
        self._dialog.songSlider.valueChanged.connect(self.sliderValueChanged)

        self._dialog.pushButtonHideSource.clicked.connect(self._handelHideSource)
        self._dialog.pushButtonHideDest.clicked.connect(self._handelHideDest)

        self._dialog.milongaSource.doubleClicked.connect(self._libraryClicked)
        self._dialog.milongaSource.clicked.connect(self._handleLibrarySelectionClicked)
        self._dialog.milongaSource.selectionModel().selectionChanged.connect(self._handleLibrarySelectionChanged)
        self._dialog.milongaDest.doubleClicked.connect(self._destLibraryClicked)

        self._dialog.milongaSource.customContextMenuRequested.connect(self.popupLibrary)
        self._dialog.milongaDest.customContextMenuRequested.connect(self.popupMilonga)

        self._dialog.stopToolButton.clicked.connect(self.stop_media)

        self._dialog.comboBoxArtist.currentIndexChanged.connect(self._handel_filter_change)
        self._dialog.comboBoxAlbum.currentIndexChanged.connect(self._handel_filter_change)
        self._dialog.comboBoxGenre.currentIndexChanged.connect(self._handel_filter_change)
        self._dialog.pushButtonClearFilter.clicked.connect(self._clear_filter)

        self._dialog.pushButtonSaveMilonga.clicked.connect(self._save_milonga)
        self._dialog.pushButtonSaveMilongaAs.clicked.connect(self._save_milonga_as)
        self._dialog.pushButtonDeleteMilonga.clicked.connect(self._delete_milonga)
        self._dialog.pushButtonLoadMilonga.clicked.connect(self._load_milonga)
        self._dialog.pushButtonMilongaClear.clicked.connect(self._clearMilonga)

        self._dialog.pushButtonInfoMilonga.clicked.connect(self._showInfoMilonga)
        self.infoMilongaContent.pushButtonClose.clicked.connect(self.closeInfoMilonga)
        self.selectMilongaListContent.listWidgetMilongas.doubleClicked.connect(self._doubleClickedMilongaSelect)
