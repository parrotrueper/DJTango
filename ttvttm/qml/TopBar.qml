import QtQuick 2.15
import QtQuick.Controls 2.15
import QtQuick.Layouts 1.15

Item {
    id: topBar
    width: parent ? parent.width : implicitWidth
    height: container ? container.height : implicitHeight
    implicitHeight: theme ? theme.headerHeight : 48

    property var backendObject: null
    property int playbackPosition: 0
    property int playbackDuration: 0
    property bool isPlaying: false
    property bool isLiveSession: false
    property int selectedPlaylistId: -1
    property var theme: null
    property int smallIconButtonWidth: 52
    property int smallIconButtonHeight: 24
    property int smallIconSize: 24
    property string viewMode: "both"
    signal viewModeRequested(string mode)
    signal liveSessionToggled(bool enabled)

    Component.onCompleted: {
        if (backendObject) {
            playbackPosition = backendObject.playbackPosition
            playbackDuration = backendObject.playbackDuration
        }
    }

    Connections {
        target: backendObject
        onPlaybackPositionChanged: playbackPosition = backendObject.playbackPosition
        onPlaybackDurationChanged: playbackDuration = backendObject.playbackDuration
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

    Rectangle {
        id: container
        anchors.fill: parent
        height: theme.headerHeight
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
                    onClicked: viewModeRequested("library")
                }
                MenuBarButton {
                    id: playlistButton
                    label: "Playlist"
                    textColor: theme.menuText
                    onClicked: viewModeRequested("playlist")
                }
                MenuBarButton {
                    id: viewButton
                    label: "View"
                    textColor: theme.menuText
                    onClicked: viewPopup.open()
                }

                Popup {
                    id: viewPopup
                    modal: false
                    focus: true
                    x: viewButton.mapToItem(parent, 0, viewButton.height).x
                    y: viewButton.mapToItem(parent, 0, viewButton.height).y
                    width: 180

                    background: Rectangle {
                        color: theme.surface
                        border.color: theme.borders
                        border.width: 1
                        radius: theme.cornerRadius
                    }

                    ColumnLayout {
                        anchors.fill: parent
                        anchors.margins: 8
                        spacing: 2

                        Button {
                            text: "Default"
                            flat: true
                            Layout.fillWidth: true
                            onClicked: {
                                viewModeRequested("both")
                                viewPopup.close()
                            }
                        }
                        Button {
                            text: "Playlist"
                            flat: true
                            Layout.fillWidth: true
                            onClicked: {
                                viewModeRequested("playlist")
                                viewPopup.close()
                            }
                        }
                        Button {
                            text: "Library"
                            flat: true
                            Layout.fillWidth: true
                            onClicked: {
                                viewModeRequested("library")
                                viewPopup.close()
                            }
                        }
                    }
                }

                MenuBarButton {
                    id: preferencesButton
                    label: "Settings"
                    textColor: theme.menuText
                }
            }

            Item { Layout.fillWidth: true }

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
                background: Rectangle { color: "transparent" }
                contentItem: RowLayout {
                    anchors.fill: parent
                    spacing: 8
                    Layout.alignment: Qt.AlignVCenter

                    Image {
                        source: "icons/speaker_group_24dp_E3E3E3_FILL0_wght400_GRAD0_opsz24.svg"
                        width: 18
                        height: 18
                        fillMode: Image.PreserveAspectFit
                        smooth: true
                    }
                    Label { text: backendObject ? backendObject.liveOutputName() : "?"; color: theme.menuText; font.pixelSize: 12 }
                    Label { text: backendObject ? backendObject.liveVolume() + "%" : "80%"; color: theme.menuText; font.pixelSize: 12 }
                    Rectangle { width: 1; height: 18; color: theme.accent }
                    Image {
                        source: isLiveSession ? "icons/radio_button_checked_24dp_E3E3E3_FILL0_wght400_GRAD0_opsz24.svg" : "icons/radio_button_unchecked_24dp_E3E3E3_FILL0_wght400_GRAD0_opsz24.svg"
                        width: 14
                        height: 14
                        fillMode: Image.PreserveAspectFit
                    }
                    Label { text: "LIVE"; color: theme.menuText; font.pixelSize: 12 }
                }
                onClicked: {
                    if (backendObject) backendObject.setLiveSession(!isLiveSession)
                    isLiveSession = !isLiveSession
                    liveSessionToggled(isLiveSession)
                }
            }

            Item { Layout.fillWidth: true }

            ProgressBar {
                id: playbackProgressBar
                objectName: "playbackProgressBar"
                Layout.preferredWidth: parent ? parent.width * 0.30 : 360
                Layout.preferredHeight: 8
                from: 0
                to: 1
                value: backendObject && backendObject.playbackDuration > 0 ? backendObject.playbackPosition / backendObject.playbackDuration : 0
                background: Rectangle { color: theme.surface; radius: 4 }
            }

            RowLayout {
                spacing: 6
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
                spacing: 6
                Layout.alignment: Qt.AlignRight

                Label {
                    objectName: "playbackTimeElapsed"
                    text: formatDuration(playbackPosition)
                    color: theme.menuText
                    font.pixelSize: 11
                }
                Label {
                    objectName: "playbackTimeDuration"
                    text: formatDuration(playbackDuration)
                    color: theme.menuText
                    font.pixelSize: 11
                }
            }
        }
    }
}
