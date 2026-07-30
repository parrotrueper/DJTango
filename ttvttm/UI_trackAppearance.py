
from PySide6 import QtCore, QtWidgets


class Ui_trackAppearance:
    def setupUi(self, trackAppearance):
        trackAppearance.setObjectName("trackAppearance")
        trackAppearance.resize(380, 460)
        self.verticalLayout = QtWidgets.QVBoxLayout(trackAppearance)
        self.verticalLayout.setObjectName("verticalLayout")

        self.header = QtWidgets.QLabel(trackAppearance)
        self.header.setWordWrap(True)
        self.header.setObjectName("header")
        self.verticalLayout.addWidget(self.header)

        self.typesList = QtWidgets.QListWidget(trackAppearance)
        self.typesList.setObjectName("typesList")
        self.typesList.setMaximumHeight(220)
        self.verticalLayout.addWidget(self.typesList)

        self.rowLayout = QtWidgets.QHBoxLayout()
        self.rowLayout.setObjectName("rowLayout")
        self.editTypeField = QtWidgets.QLineEdit(trackAppearance)
        self.editTypeField.setObjectName("editTypeField")
        self.rowLayout.addWidget(self.editTypeField)

        self.addTypeButton = QtWidgets.QPushButton(trackAppearance)
        self.addTypeButton.setObjectName("addTypeButton")
        self.rowLayout.addWidget(self.addTypeButton)

        self.removeTypeButton = QtWidgets.QPushButton(trackAppearance)
        self.removeTypeButton.setObjectName("removeTypeButton")
        self.rowLayout.addWidget(self.removeTypeButton)

        self.verticalLayout.addLayout(self.rowLayout)

        self.groupBoxPreview = QtWidgets.QGroupBox(trackAppearance)
        self.groupBoxPreview.setObjectName("groupBoxPreview")
        self.previewLayout = QtWidgets.QVBoxLayout(self.groupBoxPreview)
        self.previewLayout.setObjectName("previewLayout")

        self.previewLabel = QtWidgets.QLabel(trackAppearance)
        self.previewLabel.setAlignment(QtCore.Qt.AlignCenter)
        self.previewLabel.setObjectName("previewLabel")
        self.previewLabel.setMinimumHeight(70)
        self.previewLayout.addWidget(self.previewLabel)

        self.buttonsLayout = QtWidgets.QHBoxLayout()
        self.buttonsLayout.setObjectName("buttonsLayout")
        self.selectColorButton = QtWidgets.QPushButton(self.groupBoxPreview)
        self.selectColorButton.setObjectName("selectColorButton")
        self.buttonsLayout.addWidget(self.selectColorButton)
        self.selectFontColorButton = QtWidgets.QPushButton(self.groupBoxPreview)
        self.selectFontColorButton.setObjectName("selectFontColorButton")
        self.buttonsLayout.addWidget(self.selectFontColorButton)
        self.selectFontButton = QtWidgets.QPushButton(self.groupBoxPreview)
        self.selectFontButton.setObjectName("selectFontButton")
        self.buttonsLayout.addWidget(self.selectFontButton)
        self.previewLayout.addLayout(self.buttonsLayout)

        self.verticalLayout.addWidget(self.groupBoxPreview)

        self.buttonBox = QtWidgets.QDialogButtonBox(trackAppearance)
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtWidgets.QDialogButtonBox.Cancel | QtWidgets.QDialogButtonBox.Ok)
        self.applyButton = QtWidgets.QPushButton(trackAppearance)
        self.applyButton.setObjectName("applyButton")
        self.buttonBox.addButton(self.applyButton, QtWidgets.QDialogButtonBox.ApplyRole)
        self.buttonBox.setObjectName("buttonBox")
        self.verticalLayout.addWidget(self.buttonBox)

        self.retranslateUi(trackAppearance)
        QtCore.QMetaObject.connectSlotsByName(trackAppearance)

    def retranslateUi(self, trackAppearance):
        _translate = QtCore.QCoreApplication.translate
        trackAppearance.setWindowTitle(_translate("trackAppearance", "Track Appearance"))
        self.header.setText(_translate("trackAppearance", "Select a track type and customize its background color, font color, and font style."))
        self.editTypeField.setPlaceholderText(_translate("trackAppearance", "New track type"))
        self.addTypeButton.setText(_translate("trackAppearance", "Add type"))
        self.removeTypeButton.setText(_translate("trackAppearance", "Remove type"))
        self.groupBoxPreview.setTitle(_translate("trackAppearance", "Appearance preview"))
        self.previewLabel.setText(_translate("trackAppearance", "Track preview text"))
        self.selectColorButton.setText(_translate("trackAppearance", "Choose color"))
        self.selectFontColorButton.setText(_translate("trackAppearance", "Font colour"))
        self.selectFontButton.setText(_translate("trackAppearance", "Choose font"))
        self.applyButton.setText(_translate("trackAppearance", "Apply"))
