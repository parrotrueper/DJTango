import QtQuick 2.15
import QtQuick.Controls 2.15
import QtQuick.Layouts 1.15

Rectangle {
    id: libraryPanel
    Layout.fillWidth: true
    Layout.preferredWidth: 600
    Layout.fillHeight: true
    radius: theme ? theme.cornerRadius : 0
    color: theme ? theme.surface : "#222222"
    border.color: theme ? theme.borders : "#444444"
    border.width: 1
    visible: !viewModePlaylistOnly

    property var backendObject: null
    property string searchText: ""
    property string wipContext: "Library"
    property var wipContextOptions: []
    property bool viewModePlaylistOnly: false
    property string selectedTrackTitle: ""
    property string selectedTrackArtist: ""
    property int selectedLibraryIndex: -1
    property int selectedLibraryId: -1
    property int libraryColWidthNumber: 32
    property int libraryColWidthTitle: 300
    property int libraryColWidthArtist: 180
    property int libraryColWidthGenre: 130
    property int libraryColWidthYear: 60
    property int libraryColWidthDuration: 80
    property var theme: null
    property alias libraryView: libraryView
    signal selectionChanged(int index, int trackId, string title, string artist)

    ColumnLayout {
        anchors.fill: parent
        anchors.margins: 12
        spacing: 8

        Label {
            text: "WIP — " + wipContext
            color: theme ? theme.text : "#ffffff"
            font.pixelSize: 18
        }

        RowLayout {
            Layout.fillWidth: true
            spacing: 8

            Label {
                text: "WIP context:"
                color: theme ? theme.mutedText : "#bbbbbb"
                font.pixelSize: 11
            }

            ComboBox {
                id: wipContextCombo
                Layout.preferredWidth: 180
                implicitHeight: 28
                font.pixelSize: 11
                model: wipContextOptions
                currentIndex: wipContextOptions ? wipContextOptions.indexOf(wipContext) : -1
                onCurrentTextChanged: {
                    if (backendObject && backendObject.selectWipContext(currentText)) {
                        wipContext = currentText
                    } else {
                        currentIndex = wipContextOptions.indexOf(wipContext)
                    }
                }
            }
        }

        ListView {
            id: libraryView
            objectName: "libraryView"
            model: backendObject ? (wipContext === "Last playlist" ? backendObject.playlistModel : backendObject.libraryModel) : null
            clip: true
            Layout.fillWidth: true
            Layout.fillHeight: true
            onCountChanged: console.log("LibraryPanel libraryView count ->", count)
            onModelChanged: console.log("LibraryPanel model changed ->", model)

            delegate: Rectangle {
                width: libraryView.width
                height: 42
                color: index % 2 === 0 ? (theme ? theme.background : "#1e1e1e") : (theme ? theme.surface : "#2c2c2c")

                MouseArea {
                    anchors.fill: parent
                    onClicked: {
                        libraryView.currentIndex = index
                        selectedLibraryIndex = index
                        selectedLibraryId = trackId
                        selectedTrackTitle = title
                        selectedTrackArtist = artist
                        selectionChanged(index, trackId, title, artist)
                    }
                }

                RowLayout {
                    anchors.fill: parent
                    anchors.margins: 8
                    spacing: 12

                    Label {
                        text: title
                        color: theme ? theme.text : "#ffffff"
                        elide: Text.ElideRight
                        Layout.preferredWidth: libraryColWidthTitle
                        Layout.fillWidth: true
                    }

                    Label {
                        text: artist
                        color: theme ? theme.mutedText : "#cccccc"
                        font.pixelSize: 11
                        Layout.preferredWidth: libraryColWidthArtist
                    }

                    Button {
                        id: libraryAddButton
                        objectName: "libraryAddButton"
                        text: "Add"
                        flat: true
                        Layout.preferredWidth: 80
                        onClicked: {
                            if (backendObject) {
                                backendObject.addTrackToPlaylist(trackId)
                            }
                        }
                    }
                }
            }
        }
    }
}
