class InfoDisplayMixin:
    def _showInfo(self, info):
        self.infoContent.labelInfo.setText(info)
        width = self.infoContent.labelInfo.fontMetrics().boundingRect(self.infoContent.labelInfo.text()).width()
        self.infoWindow.resize(width + 60, 40)
        self.infoWindow.move(
            self.geometry().x() + (self.geometry().width() - self.infoWindow.geometry().width()) / 2,
            self.geometry().y() + 5,
        )
        self.infoWindow.show()
        self.info_thread.render(5)

    def closeInfo(self):
        self.infoWindow.close()

    def _showInfoMilonga(self):
        self.infoMilongaContent.labelInfo.setText(self.infoMilongaSentence)
        width = self.infoMilongaContent.labelInfo.fontMetrics().boundingRect(self.infoContent.labelInfo.text()).width()
        height = self.infoMilongaContent.labelInfo.fontMetrics().boundingRect(
            self.infoContent.labelInfo.text()
        ).height()
        self.infoMilongaWindow.resize(width + 10, height + 10)
        self.infoMilongaWindow.move(
            self.geometry().x() + (self.geometry().width() - self.infoMilongaWindow.geometry().width()) / 2,
            self.geometry().y() + (self.geometry().height() - self.infoMilongaWindow.geometry().height()) / 2,
        )
        self.infoMilongaWindow.show()

    def closeInfoMilonga(self):
        self.infoMilongaWindow.close()
