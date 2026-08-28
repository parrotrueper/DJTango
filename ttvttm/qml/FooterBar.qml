import QtQuick 2.15
import QtQuick.Controls 2.15
import QtQuick.Layouts 1.15

Rectangle {
    id: footerBar
    Layout.fillWidth: true
    height: 40
    property var theme: null
    color: theme ? theme.secondary : "#000000"
    border.color: theme ? theme.borders : "#000000"
    border.width: 1

    property int libraryCount: 0
    property int playlistCount: 0

    RowLayout {
        anchors.fill: parent
        anchors.margins: 12
        spacing: 12

        Label {
            text: "Library tracks: " + libraryCount + " | Playlist tracks: " + playlistCount
            color: theme.text
        }

        Item { Layout.fillWidth: true }

        Label {
            text: "Search is live and filters the library list."
            color: theme.mutedText
        }
    }
}
