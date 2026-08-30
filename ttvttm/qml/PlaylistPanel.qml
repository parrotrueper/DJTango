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

                ListView {
                    z: 0
                    id: playlistView
                    objectName: "playlistView"
                    model: backendObject ? backendObject.playlistModel : null
                    clip: true
                    anchors.fill: parent
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

        // DropArea at root level so ListView.clip doesn't affect it
        DropArea {
            id: playlistDropArea
            z: 100
            anchors.top: parent.top
            anchors.left: parent.left
            anchors.right: parent.right
            anchors.bottom: parent.bottom
            anchors.topMargin: 50  // Account for label
            anchors.leftMargin: 12
            anchors.rightMargin: 12
            anchors.bottomMargin: 12
            
            // Accept both internal drag-drop and external file drops
            keys: [
                "application/x-ttvttm-trackid",  // Internal drag-drop
                "text/uri-list",                   // Files from file manager
                "text/plain"                       // Text from other apps
            ]
            
            Component.onCompleted: {
                console.log("PlaylistPanel DropArea created: x=", x, "y=", y, "width=", width, "height=", height, "visible=", visible)
            }
            
            onEntered: function(drag) {
                console.log("PlaylistPanel DropArea: onEntered fired!")
                console.log("  -> drag.formats:", drag.formats)
                console.log("  -> drag.keys:", drag.keys)
                // Accept the drag with CopyAction
                drag.accept(Qt.CopyAction)
                console.log("  -> Accepted drag with Qt.CopyAction")
            }
            onExited: function() {
                console.log("PlaylistPanel DropArea: onExited fired!")
            }
            onDropped: function(drop) {
                console.log("*** PlaylistPanel DropArea: onDropped fired! ***")
                console.log("  -> drop.formats:", drop.formats)
                var trackId = null
                var uriList = null
                
                // Method 1: Internal drag-drop via trackId
                try {
                    var mimeData = drop.getDataAsString("application/x-ttvttm-trackid")
                    if (mimeData) {
                        trackId = parseInt(mimeData)
                        console.log("  -> Method 1: Extracted trackId from internal MIME:", trackId)
                    }
                } catch(e) {
                    console.log("  -> Method 1 failed:", e)
                }
                
                // Method 2: External files via text/uri-list
                if (!trackId) {
                    try {
                        uriList = drop.getDataAsString("text/uri-list")
                        if (uriList) {
                            console.log("  -> Method 2: Got uri-list:", uriList)
                            // Text/uri-list can contain multiple URIs separated by newlines
                            var uris = uriList.split("\n").filter(function(uri) { return uri.trim().length > 0 })
                            console.log("  -> Parsed", uris.length, "URI(s)")
                            // TODO: Implement importing files from external paths
                        }
                    } catch(e) {
                        console.log("  -> Method 2 failed:", e)
                    }
                }
                
                // Method 3: Fallback to plain text
                if (!trackId && !uriList) {
                    try {
                        var plainText = drop.getDataAsString("text/plain")
                        if (plainText) {
                            console.log("  -> Method 3: Got plain text:", plainText)
                            // TODO: Implement searching for track by text description
                        }
                    } catch(e) {
                        console.log("  -> Method 3 failed:", e)
                    }
                }
                
                // Accept the drop
                drop.accept()
                console.log("  -> Accepted drop")
                
                // Add track to playlist (internal drag-drop)
                if (trackId && backendObject) {
                    console.log("  -> Adding trackId", trackId, "to playlist")
                    backendObject.addTrackToPlaylist(trackId)
                } else if (trackId) {
                    console.log("  -> No backendObject")
                } else {
                    console.log("  -> No valid trackId, uriList, or method to handle dropped data")
                }
            }
        }
    }
