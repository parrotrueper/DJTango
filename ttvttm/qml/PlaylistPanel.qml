import QtQuick 2.15
import QtQuick.Controls 2.15
import QtQuick.Layouts 1.15

Rectangle {
    id: playlistPanel
    Layout.fillWidth: true
    Layout.preferredWidth: 600
    Layout.fillHeight: true
    radius: theme.cornerRadius
    color: theme.surface
    border.color: theme.borders
    border.width: 1
    visible: !viewModeLibraryOnly

    property var backendObject: null
    property bool viewModeLibraryOnly: false
    property int selectedPlaylistIndex: -1
    property int selectedPlaylistId: -1
    property string selectedTrackTitle: ""
    property string selectedTrackArtist: ""
    property var theme: null
    property alias playlistView: playlistView
    signal selectionChanged(int index, int trackId, string title, string artist)

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
                    delegate: Rectangle {
                        width: playlistView.width
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
                                selectionChanged(index, trackId, title, artist)
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
