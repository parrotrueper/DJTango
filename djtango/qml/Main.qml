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
    property string selectedTrackTitle: ""
    property string selectedTrackArtist: ""
    property int selectedLibraryIndex: -1
    property int selectedLibraryId: -1
    property int selectedPlaylistIndex: -1
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
        property string borders: "#777777"
        property int cornerRadius: 8
        property int headerHeight: 48
    }

    /* App initialization and backend wiring */
    Component.onCompleted: {
        backendObject = backend
        if (backendObject) {
            backendObject.loadLibrary()
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
        height: theme.headerHeight
        width: parent.width
        color: '#debcbbb9'
        border.color: theme.borders
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
                            smooth: true
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
                            smooth: true
                        }
                        Label {
                            text: playlistButton.label
                            color: theme.menuText
                            font.pixelSize: 13
                            verticalAlignment: Label.AlignVCenter
                        }
                    }
                    iconSource: "icons/queue_music_24dp_E3E3E3_FILL0_wght400_GRAD0_opsz24.svg"
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
                            smooth: true
                        }
                        Label {
                            text: viewButton.label
                            color: theme.menuText
                            font.pixelSize: 13
                            verticalAlignment: Label.AlignVCenter
                        }
                    }
                    iconSource: "icons/visibility_24dp_E3E3E3_FILL0_wght400_GRAD0_opsz24.svg"
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
                Button {
                    id: preferencesButton
                    property alias iconSource: iconImagePreferences.source
                    property string label: "Settings"
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
                            smooth: true
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

            Item {
                Layout.fillWidth: true
            }

            Rectangle {
                width: 250
                height: 8
                radius: 4
                color: theme.accent
                border.width: 1
                border.color: theme.text
                Layout.alignment: Qt.AlignVCenter
            }

            RowLayout {
                spacing: 0
                Layout.alignment: Qt.AlignRight

                Button {
                    id: prevButton
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
                    onClicked: backendObject && backendObject.togglePlayPause()
                }
                Button {
                    id: nextButton
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
                border.color: theme.accent
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
                border.color: theme.accent
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
                Layout.preferredHeight: 56
                height: 56
                radius: theme.cornerRadius
                color: "#0C2847"
                border.color: theme.accent
                border.width: 1

                ColumnLayout {
                    anchors.fill: parent
                    anchors.margins: 2
                    spacing: 0

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
                                border.color: theme.accent
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
                            placeholderText: "Playlist name"
                            Layout.preferredWidth: 220
                            implicitHeight: 26
                            background: Rectangle {
                                color: "#0E3A61"
                                radius: theme.cornerRadius
                                border.color: theme.accent
                                border.width: 1
                            }
                            font.pixelSize: 10
                            color: theme.text
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
                    border.color: theme.accent
                    border.width: 1
                    visible: viewMode !== "playlist"

                    ColumnLayout {
                        anchors.fill: parent
                        anchors.margins: 12
                        spacing: 8

                        Label {
                            text: "Library"
                            color: theme.text
                            font.pixelSize: 18
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
                            model: backendObject ? backendObject.libraryModel : null
                            clip: true
                            Layout.fillWidth: true
                            Layout.fillHeight: true
                            delegate: Rectangle {
                                width: libraryView.width
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
                                        text: (index + 1).toString()
                                        color: theme.text
                                        font.pixelSize: 11
                                        Layout.preferredWidth: libraryColWidthNumber
                                    }

                                    Label {
                                        text: title
                                        color: theme.text
                                        elide: Text.ElideRight
                                        Layout.preferredWidth: libraryColWidthTitle
                                        Layout.fillWidth: true
                                    }

                                    Label {
                                        text: artist
                                        color: theme.mutedText
                                        font.pixelSize: 11
                                        horizontalAlignment: Text.AlignLeft
                                        Layout.preferredWidth: libraryColWidthArtist
                                    }

                                    Label {
                                        text: genre
                                        color: theme.mutedText
                                        font.pixelSize: 11
                                        horizontalAlignment: Text.AlignLeft
                                        Layout.preferredWidth: libraryColWidthGenre
                                    }

                                    Label {
                                        text: year > 0 ? year.toString() : ""
                                        color: theme.mutedText
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
                                        color: theme.mutedText
                                        font.pixelSize: 11
                                        horizontalAlignment: Text.AlignRight
                                        Layout.preferredWidth: libraryColWidthDuration
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
                            Layout.preferredHeight: 0
                            height: 0
                            visible: false

                            ComboBox {
                                id: playlistSelector
                                visible: false
                                Layout.fillWidth: true
                                model: backendObject ? backendObject.getSavedPlaylists() : []
                                currentIndex: -1
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
