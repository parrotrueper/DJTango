import QtQuick 2.15
import QtQuick.Controls 2.15
import QtQuick.Layouts 1.15

Rectangle {
    id: searchPanel
    Layout.fillWidth: true
    Layout.preferredHeight: searchContent.implicitHeight + 4
    radius: theme ? theme.cornerRadius : 0
    color: "#0C2847"
    border.color: theme ? theme.borders : "#444444"
    border.width: 1

    property var backendObject: null
    property var theme: null
    property string searchText: ""
    property bool searchFiltersEnabled: true
    property string selectedArtistFilter: "All artists"
    property string selectedAlbumFilter: "All albums"
    property string selectedGenreFilter: "All genres"
    property string searchScope: "Library"
    property var searchArtistOptions: ["All artists", "All artists"]
    property var searchAlbumOptions: ["All albums", "All albums"]
    property var searchGenreOptions: ["All genres", "All genres"]
    property var searchScopeOptions: ["Library", "Playlists", "Library 2", "Live", "WIP"]
    property string playlistDirectory: ""
    property var m3u8Playlists: []
    property string selectedM3u8Playlist: ""
    property var savedPlaylists: []
    property alias saveNameField: saveNameField
    property alias playlistSaveButton: playlistSaveButton
    property alias playlistSelector: playlistSelector
    property alias playlistLoadButton: playlistLoadButton
    property alias playlistRefreshButton: playlistRefreshButton

    function formatDuration(timeValue) {
        var totalSeconds = Math.max(0, Math.round(timeValue))
        if (totalSeconds > 1000) {
            totalSeconds = Math.round(timeValue / 1000)
        }
        var minutes = Math.floor(totalSeconds / 60)
        var secs = totalSeconds % 60
        return minutes + ":" + (secs < 10 ? "0" + secs : secs)
    }

    ColumnLayout {
        id: searchContent
        anchors.fill: parent
        anchors.margins: 2
        spacing: 6

        RowLayout {
            id: searchHeader
            anchors.fill: parent
            anchors.margins: 2
            spacing: 6

            RowLayout {
                Layout.fillWidth: true
                Layout.preferredHeight: 32
                spacing: 6
                Layout.alignment: Qt.AlignVCenter

                TextField {
                    id: searchField
                    Layout.preferredWidth: 205
                    implicitHeight: 26
                    Layout.preferredHeight: 26
                    placeholderText: "Search library by title, artist, album, genre, path..."
                    text: searchText
                    onTextChanged: searchText = text
                    background: Rectangle {
                        color: "#0E3A61"
                        radius: theme.cornerRadius
                        border.color: theme.borders
                        border.width: 1
                    }
                    font.pixelSize: 10
                    color: theme.text
                }

                Button {
                    id: searchButton
                    property alias iconSource: iconImageSearch.source
                    flat: true
                    Layout.preferredWidth: 36
                    Layout.preferredHeight: 28
                    implicitWidth: 36
                    implicitHeight: 28
                    padding: 0
                    leftPadding: 0
                    rightPadding: 0
                    topPadding: 0
                    bottomPadding: 0
                    contentItem: Image {
                        id: iconImageSearch
                        anchors.centerIn: parent
                        width: 18
                        height: 18
                        fillMode: Image.PreserveAspectFit
                        smooth: true
                        source: searchButton.iconSource
                    }
                    iconSource: "icons/search_24dp_E3E3E3_FILL0_wght400_GRAD0_opsz24.svg"
                    onClicked: searchText = searchField.text
                }

                CheckBox {
                    id: filterCheckbox
                    objectName: "filterCheckbox"
                    Layout.preferredHeight: 28
                    checked: searchFiltersEnabled
                    onCheckedChanged: searchFiltersEnabled = checked
                }

                ComboBox {
                    id: artistFilterCombo
                    Layout.preferredWidth: 120
                    implicitHeight: 24
                    Layout.preferredHeight: 24
                    font.pixelSize: 10
                    model: searchArtistOptions
                    currentIndex: searchArtistOptions ? searchArtistOptions.indexOf(selectedArtistFilter) : -1
                    onCurrentTextChanged: selectedArtistFilter = currentText
                    enabled: searchFiltersEnabled
                }

                ComboBox {
                    id: albumFilterCombo
                    Layout.preferredWidth: 120
                    implicitHeight: 24
                    Layout.preferredHeight: 24
                    font.pixelSize: 10
                    model: searchAlbumOptions
                    currentIndex: searchAlbumOptions ? searchAlbumOptions.indexOf(selectedAlbumFilter) : -1
                    onCurrentTextChanged: selectedAlbumFilter = currentText
                    enabled: searchFiltersEnabled
                }

                ComboBox {
                    id: genreFilterCombo
                    Layout.preferredWidth: 120
                    implicitHeight: 24
                    Layout.preferredHeight: 24
                    font.pixelSize: 10
                    model: searchGenreOptions
                    currentIndex: searchGenreOptions ? searchGenreOptions.indexOf(selectedGenreFilter) : -1
                    onCurrentTextChanged: selectedGenreFilter = currentText
                    enabled: searchFiltersEnabled
                }

                ComboBox {
                    id: scopeCombo
                    Layout.preferredWidth: 110
                    implicitHeight: 24
                    Layout.preferredHeight: 24
                    font.pixelSize: 10
                    model: searchScopeOptions
                    currentIndex: searchScopeOptions ? searchScopeOptions.indexOf(searchScope) : -1
                    onCurrentTextChanged: searchScope = currentText
                }

                Item {
                    Layout.fillWidth: true
                }

                TextField {
                    id: saveNameField
                    objectName: "saveNameField"
                    placeholderText: "Playlist name"
                    Layout.preferredWidth: 220
                    implicitHeight: 26
                    background: Rectangle {
                        color: "#0E3A61"
                        radius: theme.cornerRadius
                        border.color: theme.borders
                        border.width: 1
                    }
                    font.pixelSize: 10
                    color: theme.text
                }
            }

            RowLayout {
                Layout.fillWidth: true
                Layout.preferredHeight: 32
                spacing: 8

                Button {
                    id: playlistSaveButton
                    objectName: "playlistSaveButton"
                    text: "Save"
                    flat: true
                    enabled: saveNameField.text !== ""
                    onClicked: {
                        if (backendObject && backendObject.savePlaylist(saveNameField.text)) {
                            savedPlaylists = backendObject.getSavedPlaylists()
                            if (playlistSelector.count > 0) {
                                playlistSelector.currentIndex = 0
                            }
                        }
                    }
                }

                ComboBox {
                    id: playlistSelector
                    objectName: "playlistSelector"
                    Layout.fillWidth: true
                    model: savedPlaylists
                    currentIndex: -1
                }

                Button {
                    id: playlistLoadButton
                    objectName: "playlistLoadButton"
                    text: "Load"
                    flat: true
                    enabled: playlistSelector.currentIndex >= 0
                    onClicked: backendObject && backendObject.loadPlaylist(playlistSelector.currentText)
                }

                Button {
                    id: playlistRefreshButton
                    objectName: "playlistRefreshButton"
                    text: "Refresh"
                    flat: true
                    onClicked: {
                        if (backendObject) {
                            savedPlaylists = backendObject.getSavedPlaylists()
                        }
                    }
                }
            }

            RowLayout {
                Layout.fillWidth: true
                Layout.preferredHeight: 28
                spacing: 8

                TextField {
                    id: playlistDirField
                    placeholderText: "Playlist directory"
                    Layout.fillWidth: true
                    implicitHeight: 26
                    text: playlistDirectory
                    onTextChanged: playlistDirectory = text
                    background: Rectangle {
                        color: "#0E3A61"
                        radius: theme.cornerRadius
                        border.color: theme.borders
                        border.width: 1
                    }
                    font.pixelSize: 10
                    color: theme.text
                }

                Button {
                    text: "Scan"
                    flat: true
                    Layout.preferredWidth: 90
                    Layout.preferredHeight: 28
                    onClicked: {
                        if (backendObject) {
                            m3u8Playlists = backendObject.getM3u8Playlists(playlistDirectory)
                        }
                    }
                }
            }

            Rectangle {
                Layout.fillWidth: true
                Layout.preferredHeight: 180
                radius: theme.cornerRadius
                color: theme.surface
                border.color: theme.borders
                border.width: 1
                visible: m3u8Playlists ? m3u8Playlists.length > 0 : false

                ColumnLayout {
                    anchors.fill: parent
                    anchors.margins: 12
                    spacing: 8

                    Label {
                        text: "Found .m3u8 playlists"
                        color: theme.text
                        font.pixelSize: 16
                    }

                    ListView {
                        id: m3u8PlaylistView
                        model: m3u8Playlists
                        clip: true
                        Layout.fillWidth: true
                        Layout.fillHeight: true
                        delegate: Rectangle {
                              width: m3u8PlaylistView.width
                            color: ListView.isCurrentItem ? theme.accent : (index % 2 === 0 ? theme.background : theme.surface)

                            MouseArea {
                                anchors.fill: parent
                                onClicked: {
                                    m3u8PlaylistView.currentIndex = index
                                    selectedM3u8Playlist = modelData
                                }
                            }

                            RowLayout {
                                anchors.fill: parent
                                anchors.margins: 8
                                spacing: 8

                                Label {
                                    text: modelData
                                    color: theme.text
                                    font.pixelSize: 12
                                    elide: Text.ElideRight
                                    Layout.fillWidth: true
                                }
                            }
                        }
                    }
                }
            }
        }
    }
}
