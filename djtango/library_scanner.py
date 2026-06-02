import logging
from djtango.dirscanningthread import dirScan
from djtango.qt_compat import QThread
from djtango.tracksong import TrackSong

logger = logging.getLogger(__name__)


class LibraryScannerMixin:
    def _setup_library_scanner(self):
        self.scanningDir = False
        self.scanner = dirScan(self._tangoList, self.djData)
        if not self.disableDirScan:
            self.dirthread2 = QThread()
            self.scanner.moveToThread(self.dirthread2)
        else:
            self.dirthread2 = None

    def _connect_library_scanner(self):
        if self.dirthread2 is not None:
            self.dirthread2.started.connect(self.scanner.workOut)
        self.scanner.scanned.connect(self.done)

    def _start_library_scanner(self):
        if self.dirthread2 is not None:
            logger.debug("starting directory scanning")
            self.dirthread2.start()

    def _stop_library_scanner(self):
        if self.dirthread2 is not None:
            self.scanner.stop()
            self.dirthread2.quit()
            if not self.dirthread2.wait(3000):
                logger.warning("dirScan thread did not stop cleanly; forcing termination")
                self.dirthread2.terminate()

    def scannDir(self, nimp):
        if not self.scanningDir:
            self.scanningDir = True
            newfiles = self._tangoList.checkNewFiles()
            if newfiles:
                for path in newfiles:
                    self.djData.insertTrack(TrackSong(path, 0, True))

                self._tangoList.loadTangos(self.djData.getAllTracks())
                data = [track.list() for track in self._tangoList.tracks.values()]
                self.sourceModel.changeData(data)
                self._showInfo(str(len(newfiles)) + " track has been added")

            self.scanningDir = False
