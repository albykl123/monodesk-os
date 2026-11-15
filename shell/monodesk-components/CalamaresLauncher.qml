import QtQuick
import QtQuick.Controls

Button {
    id: calamaresBtn
    text: "Install MONODESK OS"
    icon.name: "system-installer"
    visible: true

    contentItem: Row {
        spacing: 8
        Image {
            source: "/usr/share/icons/hicolor/scalable/apps/monodesk-icon.svg"
            width: 24
            height: 24
            fillMode: Image.PreserveAspectFit
        }
        Text {
            text: calamaresBtn.text
            color: "#FFFFFF"
            font.pixelSize: 13
            font.bold: true
            font.family: "Inter"
            verticalAlignment: Text.AlignVCenter
        }
    }

    background: Rectangle {
        color: calamaresBtn.hovered ? "#242424" : "#121212"
        radius: 6
        border.color: "#FFFFFF"
        border.width: 1
    }

    onClicked: {
        // Launches Calamares installer
        Qt.openUrlExternally("file:///usr/bin/calamares")
    }
}
