import QtQuick 2.15
import QtQuick.Controls 2.15
import QtQuick.Layouts 1.15

ApplicationWindow {
    visible: true
    width: 1200
    height: 820
    title: "DJTango"
    color: theme.background

    property var backendObject: null
    property string searchText: ""
    property string searchScope: "Library"
    property bool isPlaying: false
    property bool isLiveSession: false
    property string viewMode: "both"
    property string wipContext: "Library"
    property string selectedTrackTitle: ""
    property string selectedTrackArtist: ""
    property int selectedLibraryIndex: -1
    property int selectedLibraryId: -1
    property int selectedPlaylistIndex: -1
    property alias theme: themeObject

    /* Theme object and shared UI colors */
    QtObject {
        id: themeObject
        property string primary: "#a0344d"
        property string secondary: "#2a2a2a"
        property string accent: "#00ffff"
        property string surface: "#2a2a2a"
        property string background: "#161616"
        property string text: "#ffffff"
        property string menuText: "#000000"
        property string mutedText: "#d3d3d3"
        property int cornerRadius: 8
        property int headerHeight: 48
    }

    /* App initialization and backend wiring */
    Component.onCompleted: {
        backendObject = backend
    }

    Rectangle {
        id: titleBar
        width: parent.width
        height: 48
        color: theme.secondary

        RowLayout {
            anchors.fill: parent
            anchors.margins: 12
            spacing: 12

            Label {
                text: backendObject ? backendObject.appTitle() + " v" + backendObject.appVersion() : "DJTango"
                color: theme.text
                font.pixelSize: 16
                Layout.alignment: Qt.AlignVCenter
                Layout.fillWidth: true
            }

            RowLayout {
                spacing: 12
                Layout.alignment: Qt.AlignVCenter

                Label {
                    text: backendObject ? backendObject.liveOutputName() : "Output"
                    color: theme.text
                    font.pixelSize: 12
                }
                Label {
                    text: backendObject ? backendObject.liveVolume() + "%" : "100%"
                    color: theme.text
                    font.pixelSize: 12
                }
            }
        }
    }

    /* Signal connections from the backend */
    Connections {
        target: backendObject
        function onPlaybackStateChanged(playing) {
            isPlaying = playing
        }
    }

    /* Top menu bar / action header */
    Rectangle {
        id: menuBar
        anchors.top: titleBar.bottom
        height: theme.headerHeight
        width: parent.width
        color: "#dedddac1"
        border.color: theme.accent
        border.width: 1

        RowLayout {
            anchors.fill: parent
            anchors.margins: 12
            spacing: 12

            RowLayout {
                spacing: 8
                Layout.alignment: Qt.AlignVCenter

                Button {
                    id: libraryButton
                    property alias iconSource: iconImageLibrary.source
                    property string label: "Library"
                    flat: true
                    font.pixelSize: 13
                    contentItem: RowLayout {
                        anchors.fill: parent
                        spacing: 4
                        Image {
                            id: iconImageLibrary
                            width: 18
                            height: 18
                            fillMode: Image.PreserveAspectFit
                        }
                        Label {
                            text: libraryButton.label
                            color: theme.menuText
                            font.pixelSize: 13
                            verticalAlignment: Label.AlignVCenter
                        }
                    }
                    iconSource: "icons/music_note_add_24dp_E3E3E3_FILL0_wght400_GRAD0_opsz24.svg"
                }
                Button {
                    id: playlistButton
                    property alias iconSource: iconImagePlaylist.source
                    property string label: "Playlist"
                    flat: true
                    font.pixelSize: 13
                    contentItem: RowLayout {
                        anchors.fill: parent
                        spacing: 4
                        Image {
                            id: iconImagePlaylist
                            width: 18
                            height: 18
                            fillMode: Image.PreserveAspectFit
                        }
                        Label {
                            text: playlistButton.label
                            color: theme.menuText
                            font.pixelSize: 13
                            verticalAlignment: Label.AlignVCenter
                        }
                    }
                    iconSource: "icons/queue_music_24dp_E3E3E3_FILL0_wght400_GRAD0_opsz24.svg"
                }
                Button {
                    id: viewButton
                    property alias iconSource: iconImageView.source
                    property string label: "View"
                    flat: true
                    font.pixelSize: 13
                    contentItem: RowLayout {
                        anchors.fill: parent
                        spacing: 4
                        Image {
                            id: iconImageView
                            width: 18
                            height: 18
                            fillMode: Image.PreserveAspectFit
                        }
                        Label {
                            text: viewButton.label
                            color: theme.menuText
                            font.pixelSize: 13
                            verticalAlignment: Label.AlignVCenter
                        }
                    }
                    iconSource: "icons/visibility_24dp_E3E3E3_FILL0_wght400_GRAD0_opsz24.svg"
                }
                Button {
                    id: preferencesButton
                    property alias iconSource: iconImagePreferences.source
                    property string label: "Preferences"
                    flat: true
                    font.pixelSize: 13
                    contentItem: RowLayout {
                        anchors.fill: parent
                        spacing: 4
                        Image {
                            id: iconImagePreferences
                            width: 18
                            height: 18
                            fillMode: Image.PreserveAspectFit
                        }
                        Label {
                            text: preferencesButton.label
                            color: theme.menuText
                            font.pixelSize: 13
                            verticalAlignment: Label.AlignVCenter
                        }
                    }
                    iconSource: "icons/tune_24dp_E3E3E3_FILL0_wght400_GRAD0_opsz24.svg"
                }
            }

            Item {
                Layout.fillWidth: true
            }

            /* Live output status and session state */
            RowLayout {
                spacing: 8
                Layout.alignment: Qt.AlignVCenter

                Image {
                    source: "icons/speaker_group_24dp_E3E3E3_FILL0_wght400_GRAD0_opsz24.svg"
                    width: 18
                    height: 18
                    fillMode: Image.PreserveAspectFit
                }
                Label {
                    text: backendObject ? backendObject.liveOutputName() : "?"
                    color: theme.menuText
                    font.pixelSize: 12
                }
                Label {
                    text: backendObject ? backendObject.liveVolume() + "%" : "80%"
                    color: theme.menuText
                    font.pixelSize: 12
                }
                Rectangle {
                    width: 1
                    height: 18
                    color: theme.accent
                }
                Image {
                    source: isLiveSession ? "icons/radio_button_checked_24dp_E3E3E3_FILL0_wght400_GRAD0_opsz24.svg" : "icons/radio_button_unchecked_24dp_E3E3E3_FILL0_wght400_GRAD0_opsz24.svg"
                    width: 14
                    height: 14
                    fillMode: Image.PreserveAspectFit
                }
                Label {
                    text: "LIVE"
                    color: theme.menuText
                    font.pixelSize: 12
                }
            }

            Rectangle {
                width: 180
                height: 8
                radius: 4
                color: theme.accent
                border.width: 1
                border.color: theme.text
                Layout.alignment: Qt.AlignVCenter
            }

            RowLayout {
                spacing: 1
                Layout.alignment: Qt.AlignVCenter

                Button {
                    id: prevButton
                    property alias iconSource: iconImagePrev.source
                    flat: true
                    width: 40
                    height: 28
                    contentItem: Image {
                        id: iconImagePrev
                        anchors.centerIn: parent
                        width: 18
                        height: 18
                        fillMode: Image.PreserveAspectFit
                        source: prevButton.iconSource
                    }
                    iconSource: "icons/skip_previous_24dp_E3E3E3_FILL0_wght400_GRAD0_opsz24.svg"
                }
                Button {
                    id: playPauseButton
                    property alias iconSource: iconImagePlayPause.source
                    flat: true
                    width: 40
                    height: 28
                    contentItem: Image {
                        id: iconImagePlayPause
                        anchors.centerIn: parent
                        width: 18
                        height: 18
                        fillMode: Image.PreserveAspectFit
                        source: playPauseButton.iconSource
                    }
                    iconSource: isPlaying ? "icons/pause_circle_24dp_E3E3E3_FILL0_wght400_GRAD0_opsz24.svg" : "icons/play_circle_24dp_E3E3E3_FILL0_wght400_GRAD0_opsz24.svg"
                    onClicked: backendObject && backendObject.togglePlayPause()
                }
                Button {
                    id: nextButton
                    property alias iconSource: iconImageNext.source
                    flat: true
                    width: 40
                    height: 28
                    contentItem: Image {
                        id: iconImageNext
                        anchors.centerIn: parent
                        width: 18
                        height: 18
                        fillMode: Image.PreserveAspectFit
                        source: nextButton.iconSource
                    }
                    iconSource: "icons/skip_next_24dp_E3E3E3_FILL0_wght400_GRAD0_opsz24.svg"
                }
            }
        }
    }

    /* Main content area below the menu bar */
    Rectangle {
        anchors.left: parent.left
        anchors.right: parent.right
        anchors.top: menuBar.bottom
        anchors.bottom: parent.bottom
        color: theme.background

        ColumnLayout {
            anchors.fill: parent
            anchors.margins: 12
            spacing: 12

            /* Search field and quick actions */
            RowLayout {
                Layout.fillWidth: true
                spacing: 8

                TextField {
                    id: searchField
                    Layout.fillWidth: true
                    placeholderText: "Search library by title, artist, or album"
                    text: ""
                    onTextChanged: searchText = text
                    background: Rectangle {
                        color: theme.surface
                        radius: theme.cornerRadius
                        border.color: theme.accent
                    }
                }

                Button {
                    text: isPlaying ? "Pause" : "Play"
                    enabled: true
                    onClicked: backendObject && backendObject.togglePlayPause()
                }

                Button {
                    text: "Refresh"
                    onClicked: backendObject && backendObject.loadLibrary()
                }
            }

            /* Search scope selection buttons */
            RowLayout {
                Layout.fillWidth: true
                spacing: 8

                Label {
                    text: "Search scope:"
                    color: theme.text
                }

                Button {
                    text: "Library"
                    checkable: true
                    checked: searchScope === "Library"
                    onClicked: searchScope = "Library"
                }

                Button {
                    text: "Playlists"
                    checkable: true
                    checked: searchScope === "Playlists"
                    onClicked: searchScope = "Playlists"
                }

                Button {
                    text: "Library 2"
                    checkable: true
                    checked: searchScope === "Library 2"
                    onClicked: searchScope = "Library 2"
                }

                Button {
                    text: "Live"
                    checkable: true
                    checked: searchScope === "Live"
                    onClicked: searchScope = "Live"
                }

                Button {
                    text: "WIP"
                    checkable: true
                    checked: searchScope === "WIP"
                    onClicked: searchScope = "WIP"
                }
            }

            /* Selected track info and view mode toggles */
            RowLayout {
                Layout.fillWidth: true
                spacing: 12

                Label {
                    text: selectedTrackTitle !== "" ? "Selected: " + selectedTrackTitle + " — " + selectedTrackArtist : "No track selected"
                    color: theme.text
                    Layout.fillWidth: true
                    elide: Text.ElideRight
                }

                Switch {
                    id: modeSwitch
                    checked: isLiveSession
                    text: isLiveSession ? "Live session" : "WIP mode"
                    onCheckedChanged: isLiveSession = checked
                }

                Button {
                    text: "Library"
                    onClicked: viewMode = "library"
                }

                Button {
                    text: "Playlist"
                    onClicked: viewMode = "playlist"
                }

                Button {
                    text: "Both"
                    onClicked: viewMode = "both"
                }
            }

            /* Main panel split: WIP library panel and Live playlist panel */
            RowLayout {
                Layout.fillWidth: true
                Layout.fillHeight: true
                spacing: 12

                /* WIP / Library panel */
                Rectangle {
                    Layout.fillWidth: true
                    Layout.preferredWidth: 600
                    Layout.fillHeight: true
                    radius: theme.cornerRadius
                    color: theme.surface
                    border.color: theme.accent
                    border.width: 1
                    visible: viewMode !== "playlist"

                    ColumnLayout {
                        anchors.fill: parent
                        anchors.margins: 12
                        spacing: 8

                        RowLayout {
                            spacing: 8
                            Layout.fillWidth: true

                            Label {
                                text: "WIP Context:"
                                color: theme.text
                                font.pixelSize: 16
                            }

                            ComboBox {
                                id: wipContextCombo
                                model: backendObject ? backendObject.getWipContexts() : ["Library", "Library 2", "Last playlist"]
                                currentIndex: backendObject ? backendObject.getWipContexts().indexOf(wipContext) : 0
                                onCurrentTextChanged: {
                                    wipContext = currentText
                                    if (backendObject) backendObject.selectWipContext(currentText)
                                }
                                Layout.fillWidth: true
                            }
                        }

                        Label {
                            text: "Library"
                            color: theme.text
                            font.pixelSize: 18
                        }

                        ListView {
                            id: libraryView
                            model: backendObject ? backendObject.libraryModel : null
                            clip: true
                            Layout.fillWidth: true
                            Layout.fillHeight: true
                            delegate: Rectangle {
                                width: parent.width
                                height: 42
                                color: libraryView.currentIndex === index ? theme.accent : (index % 2 === 0 ? theme.background : theme.surface)
                                visible: searchText === "" || title.toLowerCase().indexOf(searchText.toLowerCase()) !== -1 || artist.toLowerCase().indexOf(searchText.toLowerCase()) !== -1 || album.toLowerCase().indexOf(searchText.toLowerCase()) !== -1

                                MouseArea {
                                    anchors.fill: parent
                                    onClicked: {
                                        libraryView.currentIndex = index
                                        selectedLibraryIndex = index
                                        selectedLibraryId = trackId
                                        selectedTrackTitle = title
                                        selectedTrackArtist = artist
                                    }
                                }

                                RowLayout {
                                    anchors.fill: parent
                                    anchors.margins: 8
                                    spacing: 12

                                    Label {
                                        text: title
                                        color: theme.text
                                        elide: Text.ElideRight
                                        Layout.fillWidth: true
                                    }

                                    Label {
                                        text: artist
                                        color: theme.mutedText
                                        horizontalAlignment: Text.AlignRight
                                        Layout.preferredWidth: 220
                                    }
                                }
                            }
                        }
                    }
                }

                /* Live playlist panel */
                Rectangle {
                    Layout.fillWidth: true
                    Layout.preferredWidth: 520
                    Layout.fillHeight: true
                    radius: theme.cornerRadius
                    color: theme.surface
                    border.color: theme.accent
                    border.width: 1
                    visible: viewMode !== "library"

                    ColumnLayout {
                        anchors.fill: parent
                        anchors.margins: 12
                        spacing: 8

                        Label {
                            text: "Live playlist"
                            color: theme.text
                            font.pixelSize: 18
                        }

                        ListView {
                            id: playlistView
                            model: backendObject ? backendObject.playlistModel : null
                            clip: true
                            Layout.fillWidth: true
                            Layout.fillHeight: true
                            delegate: Rectangle {
                                width: parent.width
                                height: 42
                                color: playlistView.currentIndex === index ? theme.accent : (index % 2 === 0 ? theme.background : theme.surface)

                                MouseArea {
                                    anchors.fill: parent
                                    onClicked: {
                                        playlistView.currentIndex = index
                                        selectedTrackTitle = title
                                        selectedTrackArtist = artist
                                    }
                                }

                                RowLayout {
                                    anchors.fill: parent
                                    anchors.margins: 8
                                    spacing: 12

                                    Label {
                                        text: title
                                        color: theme.text
                                        elide: Text.ElideRight
                                        Layout.fillWidth: true
                                    }

                                    Label {
                                        text: artist
                                        color: theme.mutedText
                                        horizontalAlignment: Text.AlignRight
                                        Layout.preferredWidth: 220
                                    }
                                }
                            }
                        }

                        RowLayout {
                            Layout.fillWidth: true
                            spacing: 8

                            Button {
                                text: "Add to playlist"
                                enabled: selectedLibraryId >= 0
                                onClicked: {
                                    if (selectedLibraryId >= 0) {
                                        backendObject && backendObject.addTrackToPlaylist(selectedLibraryId)
                                    }
                                }
                            }

                            Button {
                                text: "Remove from playlist"
                                enabled: playlistView.currentIndex >= 0
                                onClicked: backendObject && backendObject.removeTrackFromPlaylist(playlistView.currentIndex)
                            }
                        }

                        RowLayout {
                            Layout.fillWidth: true
                            spacing: 8

                            TextField {
                                id: saveNameField
                                placeholderText: "Playlist name"
                                Layout.fillWidth: true
                                background: Rectangle {
                                    color: theme.background
                                    radius: theme.cornerRadius
                                    border.color: theme.accent
                                }
                            }

                            Button {
                                text: "Save"
                                enabled: saveNameField.text !== ""
                                onClicked: {
                                    backendObject && backendObject.savePlaylist(saveNameField.text)
                                    if (backendObject) playlistSelector.model = backendObject.getSavedPlaylists()
                                }
                            }
                        }

                        RowLayout {
                            Layout.fillWidth: true
                            spacing: 8

                            ComboBox {
                                id: playlistSelector
                                Layout.fillWidth: true
                                model: backendObject ? backendObject.getSavedPlaylists() : []
                                currentIndex: -1
                            }

                            Button {
                                text: "Load"
                                enabled: playlistSelector.currentIndex >= 0
                                onClicked: backendObject && backendObject.loadPlaylist(playlistSelector.currentText)
                            }
                        }
                    }
                }
            }
        }
    }

    /* Footer / status bar */
    footer: Rectangle {
        height: 40
        width: parent.width
        color: theme.secondary
        border.color: theme.accent
        border.width: 1

        RowLayout {
            anchors.fill: parent
            anchors.margins: 12
            spacing: 12

            Label {
                text: "Library tracks: " + libraryView.count + " | Playlist tracks: " + playlistView.count
                color: theme.text
            }

            Item {
                Layout.fillWidth: true
            }

            Label {
                text: "Search is live and filters the library list."
                color: theme.mutedText
            }
        }
    }
}
