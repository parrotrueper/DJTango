import QtQuick 2.15
import QtQuick.Controls 2.15
import QtQuick.Layouts 1.15

Item {
    id: nowPlayingPanel
    Layout.fillWidth: true
    Layout.preferredHeight: implicitHeight
    implicitHeight: nowPlayingContent.implicitHeight

    property bool isPlaying: false
    property string selectedTrackTitle: ""
    property string selectedTrackArtist: ""
    property var theme: null
    property int trackInfoSectionHeight: 82
    property int trackInfoSectionMinHeight: 82
    property int trackInfoSectionMaxHeight: 300
    signal trackInfoSectionHeightUpdated(int height)

    ColumnLayout {
        id: nowPlayingContent
        anchors.fill: parent
        anchors.margins: 12
        spacing: 2

        Rectangle {
            clip: true
            Layout.fillWidth: true
            Layout.preferredHeight: nowPlayingPanel.trackInfoSectionHeight
            height: nowPlayingPanel.trackInfoSectionHeight
            implicitHeight: nowPlayingPanel.trackInfoSectionHeight
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
                        text: "Track info height: " + nowPlayingPanel.trackInfoSectionHeight
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
            height: 8
            radius: theme.cornerRadius
            color: theme.surface
            border.color: theme.borders
            border.width: 0

            RowLayout {
                anchors.fill: parent
                anchors.margins: 2
                Layout.alignment: Qt.AlignHCenter | Qt.AlignVCenter

                Rectangle {
                    width: 80
                    height: 2
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
                property real dragStartHeight: nowPlayingPanel.trackInfoSectionHeight

                onPressed: function(mouse) {
                    dragStartY = mouse.y
                    dragStartHeight = nowPlayingPanel.trackInfoSectionHeight
                }
                onPositionChanged: function(mouse) {
                    if (!pressedButtons) return
                    var delta = mouse.y - dragStartY
                    nowPlayingPanel.trackInfoSectionHeight = Math.max(nowPlayingPanel.trackInfoSectionMinHeight, Math.min(nowPlayingPanel.trackInfoSectionMaxHeight, dragStartHeight + delta))
                    trackInfoSectionHeightUpdated(nowPlayingPanel.trackInfoSectionHeight)
                }
            }
        }
    }
}
