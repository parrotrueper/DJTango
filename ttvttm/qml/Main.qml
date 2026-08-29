import QtQuick 2.15
import QtQuick.Controls 2.15
import QtQuick.Layouts 1.15
import "."

ApplicationWindow {
    id: appWindow
    visible: true
    width: 1200
    height: 820
    title: "ttvttm"
    color: theme.background

    property var backendObject: backend
    property string searchText: ""
    property string searchScope: "Library"
    property bool searchFiltersEnabled: true
    property string selectedArtistFilter: "All artists"
    property string selectedAlbumFilter: "All albums"
    property string selectedGenreFilter: "All genres"
    property bool isPlaying: false
    property bool isLiveSession: false
    property string viewMode: "both"
    property string wipContext: "Library"
    property var wipContextOptions: ["Library", "Library 2", "Last playlist"]
    property string playlistDirectory: ""

    property var m3u8Playlists: []
    property string selectedM3u8Playlist: ""
    property string selectedTrackTitle: ""
    property string selectedTrackArtist: ""
    property int selectedLibraryIndex: -1
    property int selectedLibraryId: -1
    property int selectedPlaylistIndex: -1
    property int selectedPlaylistId: -1
    property int trackInfoSectionHeight: 82
    property int trackInfoSectionMinHeight: 82
    property int trackInfoSectionMaxHeight: Math.round(height * 0.35)
    property alias theme: themeObject

    Shortcut {
        sequence: "Ctrl+Q"
        onActivated: Qt.quit()
    }

    Theme {
        id: themeObject
    }

    Component.onCompleted: {
        console.log("Main.qml loaded", {
            viewMode: viewMode,
            width: width,
            height: height,
            searchScope: searchScope,
            isLiveSession: isLiveSession
        })

        backendObject = backend
        if (backendObject) {
            backendObject.loadLibrary()
            wipContextOptions = backendObject.getWipContexts()
            wipContext = backendObject.currentWipContext()
            m3u8Playlists = []
        }
    }

    Connections {
        target: backendObject
        function onPlaybackStateChanged(playing) {
            isPlaying = playing
        }
        function onPlaylistChanged() {
            // playlist change notifications are handled by the model bindings
        }
        function onLibraryChanged() {
            if (backendObject) {
                searchPanel.updateFilterOptions()
            }
        }
    }

    TopBar {
        id: topBar
        anchors.top: parent.top
        anchors.left: parent.left
        anchors.right: parent.right
        backendObject: appWindow.backendObject
        theme: themeObject
        isPlaying: isPlaying
        isLiveSession: isLiveSession
        selectedPlaylistId: selectedPlaylistId
        viewMode: appWindow.viewMode
        onViewModeRequested: function(mode) { appWindow.viewMode = mode }
        onLiveSessionToggled: function(enabled) { isLiveSession = enabled }
    }

    ColumnLayout {
        anchors.top: topBar.bottom
        anchors.left: parent.left
        anchors.right: parent.right
        anchors.bottom: parent.bottom
        anchors.margins: 12
        spacing: 12

        NowPlayingPanel {
            id: nowPlayingPanel
            objectName: "nowPlayingPanel"
            theme: themeObject
            isPlaying: isPlaying
            selectedTrackTitle: selectedTrackTitle
            selectedTrackArtist: selectedTrackArtist
            trackInfoSectionHeight: trackInfoSectionHeight
            trackInfoSectionMinHeight: trackInfoSectionMinHeight
            trackInfoSectionMaxHeight: trackInfoSectionMaxHeight
            onTrackInfoSectionHeightUpdated: trackInfoSectionHeight = height
        }

        SearchPanel {
            id: searchPanel
            objectName: "searchPanel"
            Layout.fillWidth: true
            Layout.fillHeight: false
            Layout.preferredHeight: implicitHeight
            backendObject: appWindow.backendObject
            theme: themeObject
            searchText: searchText
            searchFiltersEnabled: searchFiltersEnabled
            selectedArtistFilter: selectedArtistFilter
            selectedAlbumFilter: selectedAlbumFilter
            selectedGenreFilter: selectedGenreFilter
            searchScope: searchScope
        }

        RowLayout {
            Layout.fillWidth: true
            Layout.fillHeight: true
            spacing: 12

            LibraryPanel {
                id: libraryPanel
                objectName: "libraryPanel"
                Layout.fillWidth: true
                Layout.fillHeight: true
                backendObject: appWindow.backendObject
                theme: themeObject
                searchText: searchText
                wipContext: wipContext
                wipContextOptions: wipContextOptions
                viewModePlaylistOnly: viewMode === "playlist"
                selectedTrackTitle: selectedTrackTitle
                selectedTrackArtist: selectedTrackArtist
                selectedLibraryIndex: selectedLibraryIndex
                selectedLibraryId: selectedLibraryId
                libraryColWidthNumber: 32
                libraryColWidthTitle: 320
                libraryColWidthArtist: 180
                libraryColWidthGenre: 130
                libraryColWidthYear: 60
                libraryColWidthDuration: 80
                onSelectionChanged: {
                    selectedLibraryIndex = index
                    selectedLibraryId = trackId
                    selectedTrackTitle = title
                    selectedTrackArtist = artist
                }
            }

            PlaylistPanel {
                id: playlistPanel
                objectName: "playlistPanel"
                Layout.fillWidth: true
                Layout.fillHeight: true
                backendObject: appWindow.backendObject
                theme: themeObject
                viewModeLibraryOnly: viewMode === "library"
                selectedTrackTitle: selectedTrackTitle
                selectedTrackArtist: selectedTrackArtist
                onSelectionChanged: {
                    selectedPlaylistIndex = index
                    selectedPlaylistId = trackId
                    selectedTrackTitle = title
                    selectedTrackArtist = artist
                }
            }
        }
    }

    footer: FooterBar {
        theme: themeObject
        libraryCount: libraryPanel.libraryView ? libraryPanel.libraryView.count : 0
        playlistCount: playlistPanel.playlistView ? playlistPanel.playlistView.count : 0
    }
}
