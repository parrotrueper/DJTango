import QtQuick 2.15
import QtQuick.Controls 2.15

ComboBox {
    id: comboBox
    property int boxWidth: 200
    property int boxHeight: 24
    property int maxPopupHeight: 300  // Maximum height for scrollable popup
    
    implicitWidth: boxWidth
    implicitHeight: boxHeight
    
    indicator: null
    
    background: Rectangle {
        color: "#0E3A61"
        border.color: "#444444"
        border.width: 1
        radius: 2
    }
    
    contentItem: Text {
        text: comboBox.currentText
        font.pixelSize: 10
        color: "#FFFFFF"
        horizontalAlignment: Text.AlignLeft
        verticalAlignment: Text.AlignVCenter
        width: parent.width
        height: parent.height
        leftPadding: 8
        rightPadding: 8
        elide: Text.ElideRight
    }
    
    popup: Popup {
        width: boxWidth
        implicitWidth: boxWidth
        implicitHeight: Math.min(listView.contentHeight, maxPopupHeight)
        
        contentItem: ListView {
            id: listView
            width: boxWidth
            implicitWidth: boxWidth
            model: comboBox.model
            clip: true
            
            // Add scrollbar
            ScrollBar.vertical: ScrollBar {
                policy: ScrollBar.AsNeeded
                width: 12
            }
            
            delegate: ItemDelegate {
                width: boxWidth - (listView.ScrollBar.vertical.visible ? 12 : 0)
                height: boxHeight
                highlighted: ListView.isCurrentItem
                background: Rectangle {
                    color: highlighted ? "#0E3A61" : "transparent"
                }
                contentItem: Text {
                    text: modelData
                    font.pixelSize: 10
                    color: "#FFFFFF"
                    horizontalAlignment: Text.AlignLeft
                    verticalAlignment: Text.AlignVCenter
                    leftPadding: 8
                    rightPadding: 8
                    elide: Text.ElideRight
                    wrapMode: Text.NoWrap
                }
                onClicked: {
                    comboBox.currentIndex = index
                    comboBox.popup.close()
                }
            }
        }
        
        background: Rectangle {
            color: "#0C2847"
            border.color: "#444444"
            border.width: 1
        }
    }
}



