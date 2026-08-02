import QtQuick 2.15
import QtQuick.Controls 2.15
import QtQuick.Layouts 1.15
import "."

ApplicationWindow {
    visible: true
    width: 1200
    height: 820
    title: "ttvttm"
    color: theme.background

    property var backendObject: null
    property string searchText: ""
    property string searchScope: "Library"
    property bool searchFiltersEnabled: true
    property string selectedArtistFilter: "All artists"
    property string selectedAlbumFilter: "All albums"
    property string selectedGenreFilter: "All genres"
    property var searchArtistOptions: ["All artists", "All artists"]
    property var searchAlbumOptions: ["All albums", "All albums"]
    property var searchGenreOptions: ["All genres", "All genres"]
    property var searchScopeOptions: ["Library", "Playlists", "Library 2", "Live", "WIP"]
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
    property int trackInfoSectionHeight: 56
    property int trackInfoSectionMinHeight: 40
    property int trackInfoSectionMaxHeight: Math.round(height * 0.35)
    property alias theme: themeObject
    property int libraryColWidthNumber: 32
    property int libraryColWidthTitle: 320
    property int libraryColWidthArtist: 180
    property int libraryColWidthGenre: 130
    property int libraryColWidthYear: 60
    property int libraryColWidthDuration: 80
    property int smallIconButtonWidth: 52
    property int smallIconButtonHeight: 24
    property int smallIconSize: 24

    function formatDuration(seconds) {
        var total = Math.max(0, Math.round(seconds))
        var minutes = Math.floor(total / 60)
        var secs = total % 60
        return minutes + ":" + (secs < 10 ? "0" + secs : secs)
    }

    /* Theme object and shared UI colors */
    Theme {
        id: themeObject
    }

    /* App initialization and backend wiring */
    Component.onCompleted: {
        backendObject = backend
        if (backendObject) {
            backendObject.loadLibrary()
            wipContextOptions = backendObject.getWipContexts()
            wipContext = backendObject.currentWipContext()
            m3u8Playlists = []
        }
    }


    /* Signal connections from the backend */
    Connections {
        target: backendObject
        function onPlaybackStateChanged(playing) {
            isPlaying = playing
        }
        function onPlaylistChanged() {
            console.log('backend playlistChanged', 'playlistModel.rowCount=', backendObject ? backendObject.playlistModel.rowCount() : 'null')
        }
    }

    /* Top menu bar / action header */
    Rectangle {
        id: menuBar
        height: theme.headerHeight
        width: parent.width
        color: theme.background
        border.color: theme.borders
        border.width: 1

        RowLayout {
            anchors.fill: parent
            anchors.margins: 12
            spacing: 12

            RowLayout {
                spacing: 8
                Layout.alignment: Qt.AlignVCenter

                MenuBarButton {
                    id: libraryButton
                    label: "Library"
                    textColor: theme.menuText
                }
                MenuBarButton {
                    id: playlistButton
                    label: "Playlist"
                    textColor: theme.menuText
                    onClicked: playlistMenu.open()
                }

                Menu {
                    id: playlistMenu
                    title: "Playlist"
                    MenuItem {
                        text: "Add to playlist"
                        enabled: selectedLibraryId >= 0
                        onTriggered: backendObject && backendObject.addTrackToPlaylist(selectedLibraryId)
                    }
                    MenuItem {
                        text: "Remove from playlist"
                        enabled: playlistView.currentIndex >= 0
                        onTriggered: backendObject && backendObject.removeTrackFromPlaylist(playlistView.currentIndex)
                    }
                    MenuSeparator {}
                    MenuItem {
                        text: "Save playlist"
                        enabled: saveNameField.text !== ""
                        onTriggered: {
                            backendObject && backendObject.savePlaylist(saveNameField.text)
                            if (backendObject) playlistSelector.model = backendObject.getSavedPlaylists()
                        }
                    }
                    MenuItem {
                        text: "Load playlist"
                        enabled: playlistSelector.currentIndex >= 0
                        onTriggered: backendObject && backendObject.loadPlaylist(playlistSelector.currentText)
                    }
                }
                MenuBarButton {
                    id: viewButton
                    label: "View"
                    textColor: theme.menuText
                    onClicked: viewMenu.open()
                }

                Menu {
                    id: viewMenu
                    title: "View"
                    MenuItem {
                        text: "Library"
                        onTriggered: viewMode = "library"
                    }
                    MenuItem {
                        text: "Playlist"
                        onTriggered: viewMode = "playlist"
                    }
                    MenuItem {
                        text: "Both"
                        onTriggered: viewMode = "both"
                    }
                }
                MenuBarButton {
                    id: preferencesButton
                    label: "Settings"
                    textColor: theme.menuText
                }
            }

            Item {
                Layout.fillWidth: true
            }

            Button {
                id: liveSessionButton
                objectName: "liveSessionButton"
                flat: true
                Layout.alignment: Qt.AlignVCenter
                padding: 0
                leftPadding: 0
                rightPadding: 0
                topPadding: 0
                bottomPadding: 0
                background: Rectangle {
                    color: "transparent"
                }
                contentItem: RowLayout {
                    spacing: 8
                    anchors.fill: parent
                    Layout.alignment: Qt.AlignVCenter

                    Image {
                        source: "icons/speaker_group_24dp_E3E3E3_FILL0_wght400_GRAD0_opsz24.svg"
                        width: 18
                        height: 18
                        fillMode: Image.PreserveAspectFit
                        smooth: true
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
                onClicked: {
                    if (backendObject) {
                        backendObject.setLiveSession(!isLiveSession)
                    }
                    isLiveSession = !isLiveSession
                }
            }

            Item {
                Layout.fillWidth: true
            }

            ProgressBar {
                id: playbackProgressBar
                objectName: "playbackProgressBar"
                Layout.fillWidth: true
                Layout.preferredHeight: 8
                from: 0
                to: 1
                value: backendObject && backendObject.playbackDuration > 0 ? backendObject.playbackPosition / backendObject.playbackDuration : 0
                background: Rectangle {
                    color: theme.surface
                    radius: 4
                }
            }

            RowLayout {
                spacing: 0
                Layout.alignment: Qt.AlignRight

                Button {
                    id: prevButton
                    objectName: "prevButton"
                    property alias iconSource: iconImagePrev.source
                    flat: true
                    width: smallIconButtonWidth
                    height: smallIconButtonHeight
                    implicitWidth: smallIconButtonWidth
                    implicitHeight: smallIconButtonHeight
                    Layout.minimumWidth: smallIconButtonWidth
                    Layout.maximumWidth: smallIconButtonWidth
                    Layout.minimumHeight: smallIconButtonHeight
                    Layout.maximumHeight: smallIconButtonHeight
                    padding: 0
                    leftPadding: 0
                    rightPadding: 0
                    topPadding: 0
                    bottomPadding: 0
                    contentItem: Image {
                        id: iconImagePrev
                        anchors.centerIn: parent
                        width: smallIconSize
                        height: smallIconSize
                        fillMode: Image.PreserveAspectFit
                        smooth: true
                        source: prevButton.iconSource
                    }
                    iconSource: "icons/skip_previous_24dp_E3E3E3_FILL0_wght400_GRAD0_opsz24.svg"
                }
                Button {
                    id: playPauseButton
                    objectName: "playPauseButton"
                    property alias iconSource: iconImagePlayPause.source
                    flat: true
                    width: smallIconButtonWidth
                    height: smallIconButtonHeight
                    implicitWidth: smallIconButtonWidth
                    implicitHeight: smallIconButtonHeight
                    Layout.minimumWidth: smallIconButtonWidth
                    Layout.maximumWidth: smallIconButtonWidth
                    Layout.minimumHeight: smallIconButtonHeight
                    Layout.maximumHeight: smallIconButtonHeight
                    padding: 0
                    leftPadding: 0
                    rightPadding: 0
                    topPadding: 0
                    bottomPadding: 0
                    contentItem: Image {
                        id: iconImagePlayPause
                        anchors.centerIn: parent
                        width: smallIconSize
                        height: smallIconSize
                        fillMode: Image.PreserveAspectFit
                        smooth: true
                        source: playPauseButton.iconSource
                    }
                    iconSource: isPlaying ? "icons/pause_circle_24dp_E3E3E3_FILL0_wght400_GRAD0_opsz24.svg" : "icons/play_circle_24dp_E3E3E3_FILL0_wght400_GRAD0_opsz24.svg"
                    onClicked: {
                        console.log('playPauseButton clicked', 'isPlaying', isPlaying, 'selectedPlaylistId', selectedPlaylistId)
                        if (!isPlaying && selectedPlaylistId >= 0) {
                            backendObject && backendObject.playPlaylistTrack(selectedPlaylistId)
                        } else {
                            backendObject && backendObject.togglePlayPause()
                        }
                    }
                }
                Button {
                    id: nextButton
                    objectName: "nextButton"
                    property alias iconSource: iconImageNext.source
                    flat: true
                    width: smallIconButtonWidth
                    height: smallIconButtonHeight
                    implicitWidth: smallIconButtonWidth
                    implicitHeight: smallIconButtonHeight
                    Layout.minimumWidth: smallIconButtonWidth
                    Layout.maximumWidth: smallIconButtonWidth
                    Layout.minimumHeight: smallIconButtonHeight
                    Layout.maximumHeight: smallIconButtonHeight
                    padding: 0
                    leftPadding: 0
                    rightPadding: 0
                    topPadding: 0
                    bottomPadding: 0
                    contentItem: Image {
                        id: iconImageNext
                        anchors.centerIn: parent
                        width: smallIconSize
                        height: smallIconSize
                        fillMode: Image.PreserveAspectFit
                        smooth: true
                        source: nextButton.iconSource
                    }
                    iconSource: "icons/skip_next_24dp_E3E3E3_FILL0_wght400_GRAD0_opsz24.svg"
                }
            }

            RowLayout {
                spacing: 8
                Layout.alignment: Qt.AlignRight

                Label {
                    objectName: "playbackTimeElapsed"
                    text: formatDuration(backendObject ? backendObject.playbackPosition : 0)
                    color: theme.menuText
                    font.pixelSize: 11
                }
                Label {
                    objectName: "playbackTimeDuration"
                    text: formatDuration(backendObject ? backendObject.playbackDuration : 0)
                    color: theme.menuText
                    font.pixelSize: 11
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

            Rectangle {
                clip: true
                Layout.fillWidth: true
                Layout.preferredHeight: trackInfoSectionHeight
                height: trackInfoSectionHeight
                implicitHeight: trackInfoSectionHeight
                radius: theme.cornerRadius
                color: theme.surface
                border.color: theme.borders
                border.width: 1

                RowLayout {
                    anchors.fill: parent
                    anchors.margins: 12
                    spacing: 12
                    Layout.fillWidth: true
                    Layout.fillHeight: true
                    Layout.alignment: Qt.AlignHCenter | Qt.AlignVCenter

                    Image {
                        source: selectedTrackTitle === "" && !isPlaying ? "icons/music_off_24dp_E3E3E3_FILL0_wght400_GRAD0_opsz24.svg" : "icons/speaker_group_24dp_E3E3E3_FILL0_wght400_GRAD0_opsz24.svg"
                        width: 48
                        height: 48
                        fillMode: Image.PreserveAspectFit
                        smooth: true
                        Layout.alignment: Qt.AlignVCenter
                    }

                    ColumnLayout {
                        spacing: 2
                        Layout.alignment: Qt.AlignHCenter | Qt.AlignVCenter
                        Layout.fillWidth: true

                        Label {
                            text: selectedTrackTitle !== "" ? selectedTrackTitle : (isPlaying ? "Playing now" : "No track selected")
                            color: theme.text
                            font.pixelSize: 24
                            font.bold: true
                            elide: Text.ElideRight
                            horizontalAlignment: Text.AlignHCenter
                            Layout.fillWidth: true
                        }

                        Label {
                            text: selectedTrackTitle !== "" ? selectedTrackArtist : (isPlaying ? "Playback active" : "Select a track to show info")
                            color: theme.mutedText
                            font.pixelSize: 18
                            elide: Text.ElideRight
                            horizontalAlignment: Text.AlignHCenter
                            Layout.fillWidth: true
                        }

                        Label {
                            text: "Track info height: " + trackInfoSectionHeight
                            color: theme.accent
                            font.pixelSize: 11
                            horizontalAlignment: Text.AlignHCenter
                            elide: Text.ElideRight
                            Layout.fillWidth: true
                        }
                    }
                }
            }

            Rectangle {
                Layout.fillWidth: true
                height: 18
                radius: theme.cornerRadius
                color: theme.surface
                border.color: theme.borders
                border.width: 1

                RowLayout {
                    anchors.fill: parent
                    anchors.margins: 8
                    Layout.alignment: Qt.AlignHCenter | Qt.AlignVCenter

                    Rectangle {
                        width: 80
                        height: 4
                        color: theme.accent
                        radius: 2
                        Layout.alignment: Qt.AlignHCenter | Qt.AlignVCenter
                    }
                }

                MouseArea {
                    anchors.fill: parent
                    cursorShape: Qt.SizeVerCursor
                    acceptedButtons: Qt.LeftButton
                    preventStealing: true
                    hoverEnabled: true
                    property real dragStartY: 0
                    property real dragStartHeight: trackInfoSectionHeight
                    onPressed: function(mouse) {
                        dragStartY = mouse.y
                        dragStartHeight = trackInfoSectionHeight
                    }
                    onPositionChanged: function(mouse) {
                        if (!pressedButtons) return
                        var delta = mouse.y - dragStartY
                        trackInfoSectionHeight = Math.max(trackInfoSectionMinHeight, Math.min(trackInfoSectionMaxHeight, dragStartHeight + delta))
                    }
                }
            }

            /* Search field and filter controls */
            Rectangle {
                Layout.fillWidth: true
                Layout.preferredHeight: searchContent.implicitHeight + 4
                radius: theme.cornerRadius
                color: "#0C2847"
                border.color: theme.borders
                border.width: 1
                id: searchContainer

                ColumnLayout {
                    id: searchContent
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
                            text: ""
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

                        Button {
                            id: filterButton
                            property alias iconSource: iconImageFilter.source
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
                                id: iconImageFilter
                                anchors.centerIn: parent
                                width: 18
                                height: 18
                                fillMode: Image.PreserveAspectFit
                                smooth: true
                                source: filterButton.iconSource
                            }
                            checkable: true
                            checked: searchFiltersEnabled
                            iconSource: "icons/search_gear_24dp_E3E3E3_FILL0_wght400_GRAD0_opsz24.svg"
                            onClicked: searchFiltersEnabled = !searchFiltersEnabled
                        }

                        ComboBox {
                            id: artistFilterCombo
                            Layout.preferredWidth: 120
                            implicitHeight: 24
                            Layout.preferredHeight: 24
                            font.pixelSize: 10
                            model: searchArtistOptions
                            currentIndex: searchArtistOptions.indexOf(selectedArtistFilter)
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
                            currentIndex: searchAlbumOptions.indexOf(selectedAlbumFilter)
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
                            currentIndex: searchGenreOptions.indexOf(selectedGenreFilter)
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
                            currentIndex: searchScopeOptions.indexOf(searchScope)
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
                                if (backendObject) {
                                    backendObject.savePlaylist(saveNameField.text)
                                    playlistSelector.model = backendObject.getSavedPlaylists()
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
                            model: backendObject ? backendObject.getSavedPlaylists() : []
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
                                    playlistSelector.model = backendObject.getSavedPlaylists()
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
                        visible: m3u8Playlists.length > 0

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
                                    width: parent.width
                                    height: 32
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
                    border.color: theme.borders
                    border.width: 1
                    visible: viewMode !== "playlist"

                    ColumnLayout {
                        anchors.fill: parent
                        anchors.margins: 12
                        spacing: 8

                        Label {
                            text: "WIP — " + wipContext
                            color: theme.text
                            font.pixelSize: 18
                        }

                        RowLayout {
                            Layout.fillWidth: true
                            spacing: 8

                            Label {
                                text: "WIP context:"
                                color: theme.mutedText
                                font.pixelSize: 11
                            }

                            ComboBox {
                                id: wipContextCombo
                                Layout.preferredWidth: 180
                                implicitHeight: 28
                                font.pixelSize: 11
                                model: wipContextOptions
                                currentIndex: wipContextOptions.indexOf(wipContext)
                                onCurrentTextChanged: {
                                    if (backendObject && backendObject.selectWipContext(currentText)) {
                                        wipContext = currentText
                                    } else {
                                        currentIndex = wipContextOptions.indexOf(wipContext)
                                    }
                                }
                            }
                        }

                        RowLayout {
                            Layout.fillWidth: true
                            Layout.margins: 8
                            spacing: 4

                            Label {
                                text: "#"
                                color: theme.mutedText
                                font.pixelSize: 10
                                Layout.preferredWidth: libraryColWidthNumber
                            }

                            Rectangle {
                                width: 8
                                height: parent.height
                                color: "#000000"
                                border.width: 1
                                border.color: "#000000"
                                MouseArea {
                                    anchors.fill: parent
                                    hoverEnabled: true
                                    cursorShape: Qt.SizeHorCursor
                                    property int dragStartX: 0
                                    onEntered: hovered = true
                                    onExited: hovered = false
                                    onPressed: dragStartX = mouse.x
                                    onPositionChanged: if (pressedButtons) {
                                        var delta = mouse.x - dragStartX
                                        libraryColWidthTitle = Math.max(120, libraryColWidthTitle + delta)
                                        dragStartX = mouse.x
                                    }
                                }
                            }

                            Label {
                                text: "Title"
                                color: theme.mutedText
                                font.pixelSize: 10
                                Layout.preferredWidth: libraryColWidthTitle
                                Layout.fillWidth: true
                            }

                            Rectangle {
                                width: 8
                                height: parent.height
                                color: "#000000"
                                border.width: 1
                                border.color: "#000000"
                                MouseArea {
                                    anchors.fill: parent
                                    hoverEnabled: true
                                    cursorShape: Qt.SizeHorCursor
                                    property int dragStartX: 0
                                    onPressed: dragStartX = mouse.x
                                    onPositionChanged: if (pressedButtons) {
                                        var delta = mouse.x - dragStartX
                                        libraryColWidthArtist = Math.max(100, libraryColWidthArtist + delta)
                                        dragStartX = mouse.x
                                    }
                                }
                            }

                            Label {
                                text: "Artist"
                                color: theme.mutedText
                                font.pixelSize: 10
                                Layout.preferredWidth: libraryColWidthArtist
                            }

                            Rectangle {
                                width: 8
                                height: parent.height
                                color: "#000000"
                                border.width: 1
                                border.color: "#000000"
                                MouseArea {
                                    anchors.fill: parent
                                    hoverEnabled: true
                                    cursorShape: Qt.SizeHorCursor
                                    property int dragStartX: 0
                                    onPressed: dragStartX = mouse.x
                                    onPositionChanged: if (pressedButtons) {
                                        var delta = mouse.x - dragStartX
                                        libraryColWidthGenre = Math.max(100, libraryColWidthGenre + delta)
                                        dragStartX = mouse.x
                                    }
                                }
                            }

                            Label {
                                text: "Genre"
                                color: theme.mutedText
                                font.pixelSize: 10
                                Layout.preferredWidth: libraryColWidthGenre
                            }

                            Rectangle {
                                width: 8
                                height: parent.height
                                color: "#000000"
                                border.width: 1
                                border.color: "#000000"
                                MouseArea {
                                    anchors.fill: parent
                                    hoverEnabled: true
                                    cursorShape: Qt.SizeHorCursor
                                    property int dragStartX: 0
                                    onPressed: dragStartX = mouse.x
                                    onPositionChanged: if (pressedButtons) {
                                        var delta = mouse.x - dragStartX
                                        libraryColWidthYear = Math.max(40, libraryColWidthYear + delta)
                                        dragStartX = mouse.x
                                    }
                                }
                            }

                            Label {
                                text: "Year"
                                color: theme.mutedText
                                font.pixelSize: 10
                                Layout.preferredWidth: libraryColWidthYear
                            }

                            Rectangle {
                                width: 8
                                height: parent.height
                                color: "#000000"
                                border.width: 1
                                border.color: "#000000"
                                MouseArea {
                                    anchors.fill: parent
                                    hoverEnabled: true
                                    cursorShape: Qt.SizeHorCursor
                                    property int dragStartX: 0
                                    onPressed: dragStartX = mouse.x
                                    onPositionChanged: if (pressedButtons) {
                                        var delta = mouse.x - dragStartX
                                        libraryColWidthDuration = Math.max(60, libraryColWidthDuration + delta)
                                        dragStartX = mouse.x
                                    }
                                }
                            }

                            Label {
                                text: "Duration"
                                color: theme.mutedText
                                font.pixelSize: 10
                                Layout.preferredWidth: libraryColWidthDuration
                            }
                        }

                        ListView {
                            id: libraryView
                            objectName: "libraryView"
                            model: backendObject ? (wipContext === "Last playlist" ? backendObject.playlistModel : backendObject.libraryModel) : null
                            clip: true
                            Layout.fillWidth: true
                            Layout.fillHeight: true
                            delegate: Rectangle {
                                width: libraryView.width
                                height: 42
                                color: libraryView.currentIndex === index ? theme.accent : (index % 2 === 0 ? theme.background : theme.surface)
                                visible: searchText === "" || title.toLowerCase().indexOf(searchText.toLowerCase()) !== -1 || artist.toLowerCase().indexOf(searchText.toLowerCase()) !== -1 || album.toLowerCase().indexOf(searchText.toLowerCase()) !== -1
                                property int currentTrackId: trackId

                                MouseArea {
                                    anchors.fill: parent
                                    z: 0
                                    hoverEnabled: true
                                    acceptedButtons: Qt.LeftButton
                                    onClicked: {
                                        libraryView.currentIndex = index
                                        selectedLibraryIndex = index
                                        selectedLibraryId = trackId
                                        selectedTrackTitle = title
                                        selectedTrackArtist = artist
                                    }
                                }

                                RowLayout {
                                    z: 1
                                    Layout.fillWidth: true
                                    Layout.fillHeight: true
                                    Layout.margins: 8
                                    spacing: 12

                                    Label {
                                        text: (index + 1).toString()
                                        color: libraryView.currentIndex === index ? theme.background : theme.text
                                        font.pixelSize: 11
                                        Layout.preferredWidth: libraryColWidthNumber
                                    }

                                    Label {
                                        text: title
                                        color: libraryView.currentIndex === index ? theme.background : theme.text
                                        elide: Text.ElideRight
                                        Layout.preferredWidth: libraryColWidthTitle
                                        Layout.fillWidth: true
                                    }

                                    Label {
                                        text: artist
                                        color: libraryView.currentIndex === index ? theme.background : theme.mutedText
                                        font.pixelSize: 11
                                        horizontalAlignment: Text.AlignLeft
                                        Layout.preferredWidth: libraryColWidthArtist
                                    }

                                    Label {
                                        text: genre
                                        color: libraryView.currentIndex === index ? theme.background : theme.mutedText
                                        font.pixelSize: 11
                                        horizontalAlignment: Text.AlignLeft
                                        Layout.preferredWidth: libraryColWidthGenre
                                    }

                                    Label {
                                        text: year > 0 ? year.toString() : ""
                                        color: libraryView.currentIndex === index ? theme.background : theme.mutedText
                                        font.pixelSize: 11
                                        horizontalAlignment: Text.AlignCenter
                                        Layout.preferredWidth: libraryColWidthYear
                                    }

                                    Label {
                                        text: {
                                            var totalSeconds = Math.round(duration)
                                            var minutes = Math.floor(totalSeconds / 60)
                                            var seconds = totalSeconds % 60
                                            return minutes + ":" + (seconds < 10 ? "0" + seconds : seconds)
                                        }
                                        color: libraryView.currentIndex === index ? theme.background : theme.mutedText
                                        font.pixelSize: 11
                                        horizontalAlignment: Text.AlignRight
                                        Layout.preferredWidth: libraryColWidthDuration
                                    }

                                    Button {
                                        id: addButton
                                        objectName: "libraryAddButton"
                                        z: 2
                                        text: "+"
                                        flat: true
                                        enabled: true
                                        Layout.preferredWidth: 40
                                        Layout.preferredHeight: 28
                                        implicitHeight: 28
                                        onClicked: {
                                            console.log('libraryAddButton clicked', trackId)
                                            selectedLibraryIndex = index
                                            selectedLibraryId = trackId
                                            var added = false
                                            if (backendObject) {
                                                added = backendObject.addTrackToPlaylist(parseInt(trackId))
                                                console.log('addTrackToPlaylist returned', added, 'trackId', trackId)
                                                if (backendObject.playlistModel) {
                                                    console.log('playlistModel.rowCount', backendObject.playlistModel.rowCount())
                                                }
                                            }
                                        }
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
                    border.color: theme.borders
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

                        Item {
                            Layout.fillWidth: true
                            Layout.fillHeight: true

                            DropArea {
                                width: parent.width
                                height: parent.height
                                z: 1
                                onDropped: function(drop) {
                                    var mimeData = null
                                    if (drop && drop.mimeData) {
                                        mimeData = drop.mimeData
                                    } else if (drop && drop.drag && drop.drag.mimeData) {
                                        mimeData = drop.drag.mimeData
                                    }
                                    if (mimeData) {
                                        var trackIdString = null
                                        if (mimeData.hasFormat && mimeData.hasFormat("application/x-ttvttm-trackid")) {
                                            trackIdString = mimeData.data("application/x-ttvttm-trackid")
                                        } else {
                                            trackIdString = mimeData["application/x-ttvttm-trackid"]
                                        }
                                        var trackId = parseInt(trackIdString)
                                        if (!isNaN(trackId) && backendObject) {
                                            backendObject.addTrackToPlaylist(trackId)
                                        }
                                    }
                                }
                            }

                            ListView {
                                z: 0
                                id: playlistView
                                objectName: "playlistView"
                                model: backendObject ? backendObject.playlistModel : null
                                clip: true
                                anchors.fill: parent
                                Layout.fillWidth: true
                                Layout.fillHeight: true
                                onCountChanged: {
                                    console.log('playlistView.count changed', count)
                                }
                                onVisibleChanged: {
                                    console.log('playlistView visible changed', visible, 'viewMode', viewMode)
                                }
                                onHeightChanged: {
                                    console.log('playlistView.height changed', height, 'parent.height', parent ? parent.height : 'null')
                                }
                                Component.onCompleted: {
                                    console.log('playlistView initialized', 'visible', visible, 'count', count, 'model', model, 'height', height, 'parent.height', parent ? parent.height : 'null')
                                }
                                delegate: Rectangle {
                                    width: parent.width
                                    height: 42
                                    border.width: 1
                                    border.color: "blue"
                                    color: playlistView.currentIndex === index ? theme.accent : (index % 2 === 0 ? theme.background : theme.surface)

                                    MouseArea {
                                        anchors.fill: parent
                                        onClicked: {
                                            playlistView.currentIndex = index
                                            selectedPlaylistIndex = index
                                            selectedPlaylistId = trackId
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
                                            color: playlistView.currentIndex === index ? theme.background : theme.text
                                            elide: Text.ElideRight
                                            Layout.fillWidth: true
                                        }

                                        Label {
                                            text: artist
                                            color: playlistView.currentIndex === index ? theme.background : theme.mutedText
                                            horizontalAlignment: Text.AlignRight
                                            Layout.preferredWidth: 220
                                        }
                                    }
                                }
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
        border.color: theme.borders
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
