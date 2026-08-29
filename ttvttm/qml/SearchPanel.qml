import QtQuick 2.15
import QtQuick.Controls 2.15
import QtQuick.Layouts 1.15

Rectangle {
    id: searchPanel
    Layout.fillWidth: true
    Layout.preferredHeight: 42
    implicitHeight: 42
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
    property var searchArtistOptions: ["All artists"]
    property var searchAlbumOptions: ["All albums"]
    property var searchGenreOptions: ["All genres"]
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

    function performSearch() {
        if (backendObject) {
            backendObject.performSearch(
                searchText,
                selectedArtistFilter,
                selectedAlbumFilter,
                selectedGenreFilter,
                searchScope
            )
        }
    }

    function updateFilterOptions() {
        if (!backendObject) {
            return
        }
        searchArtistOptions = ["All artists"].concat(backendObject.getLibraryArtists())
        searchAlbumOptions = ["All albums"].concat(backendObject.getLibraryAlbums())
        searchGenreOptions = ["All genres"].concat(backendObject.getLibraryGenres())
    }

    Component.onCompleted: {
        if (backendObject) {
            updateFilterOptions()
        }
    }

    onBackendObjectChanged: updateFilterOptions()

    Connections {
        target: backendObject
        function onLibraryChanged() {
            updateFilterOptions()
        }
    }

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
        anchors.left: parent.left
        anchors.right: parent.right
        anchors.top: parent.top
        anchors.margins: 2
        spacing: 6

        RowLayout {
            id: searchHeader
            Layout.fillWidth: true
            Layout.preferredHeight: 32
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
                    Keys.onReturnPressed: performSearch()
                    Keys.onEnterPressed: performSearch()
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
                    onClicked: performSearch()
                }

                CheckBox {
                    id: filterCheckbox
                    objectName: "filterCheckbox"
                    Layout.preferredHeight: 28
                    checked: searchFiltersEnabled
                    onCheckedChanged: searchFiltersEnabled = checked
                }

                FilterComboBox {
                    id: artistFilterButton
                    objectName: "artistFilterButton"
                    Layout.preferredWidth: 200
                    Layout.preferredHeight: 24
                    Layout.fillWidth: false
                    boxWidth: 200
                    boxHeight: 24
                    model: searchArtistOptions
                    currentIndex: Math.max(0, searchArtistOptions.indexOf(selectedArtistFilter))
                    enabled: searchFiltersEnabled
                    onCurrentTextChanged: {
                        selectedArtistFilter = currentText
                        performSearch()
                    }
                }

                FilterComboBox {
                    id: albumFilterButton
                    objectName: "albumFilterButton"
                    Layout.preferredWidth: 200
                    Layout.preferredHeight: 24
                    Layout.fillWidth: false
                    boxWidth: 200
                    boxHeight: 24
                    model: searchAlbumOptions
                    currentIndex: Math.max(0, searchAlbumOptions.indexOf(selectedAlbumFilter))
                    enabled: searchFiltersEnabled
                    onCurrentTextChanged: {
                        selectedAlbumFilter = currentText
                        performSearch()
                    }
                }

                FilterComboBox {
                    id: genreFilterButton
                    objectName: "genreFilterButton"
                    Layout.preferredWidth: 200
                    Layout.preferredHeight: 24
                    Layout.fillWidth: false
                    boxWidth: 200
                    boxHeight: 24
                    model: searchGenreOptions
                    currentIndex: Math.max(0, searchGenreOptions.indexOf(selectedGenreFilter))
                    enabled: searchFiltersEnabled
                    onCurrentTextChanged: {
                        selectedGenreFilter = currentText
                        performSearch()
                    }
                }

                FilterComboBox {
                    id: scopeButton
                    objectName: "scopeButton"
                    Layout.preferredWidth: 140
                    Layout.preferredHeight: 24
                    Layout.fillWidth: false
                    boxWidth: 140
                    boxHeight: 24
                    model: searchScopeOptions
                    currentIndex: Math.max(0, searchScopeOptions.indexOf(searchScope))
                    onCurrentTextChanged: {
                        searchScope = currentText
                        performSearch()
                    }
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
                                Layout.fillWidth: true
                                Layout.fillHeight: true
                                Layout.margins: 8
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
