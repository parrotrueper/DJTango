import QtQuick 2.15
import QtQuick.Controls 2.15

Button {
    property string label: ""
    property color textColor: "#ffffff"

    flat: true
    font.pixelSize: 13

    contentItem: Label {
        text: parent.label
        color: parent.textColor
        font.pixelSize: 13
        verticalAlignment: Label.AlignVCenter
    }
}
