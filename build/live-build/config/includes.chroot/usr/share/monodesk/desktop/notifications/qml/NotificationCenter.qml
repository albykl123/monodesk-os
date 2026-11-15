import QtQuick 2.15
import QtQuick.Controls 2.15
import QtQuick.Layouts 1.15
import "../../themes" 1.0

ColumnLayout {
    id: notifCenter
    width: 320
    spacing: 8

    ListModel {
        id: notifModel
        ListElement { title: "MONODESK OS Ready"; message: "Universal PC Edition 1.0 initialized successfully."; time: "Just now"; urgent: false }
        ListElement { title: "Hardware Microcode"; message: "Universal Intel/AMD CPU errata mitigation active."; time: "1m ago"; urgent: false }
    }

    Repeater {
        model: notifModel
        delegate: Rectangle {
            Layout.fillWidth: true
            height: 64
            radius: MonodeskTheme.radiusCard
            color: MonodeskTheme.surfacePanel
            border.color: model.urgent ? MonodeskTheme.accentRed : MonodeskTheme.border
            border.width: 1

            RowLayout {
                anchors.fill: parent
                anchors.margins: 10
                spacing: 10

                Rectangle {
                    width: 6; height: 36
                    radius: 3
                    color: model.urgent ? MonodeskTheme.accentRed : MonodeskTheme.textSecondary
                }

                ColumnLayout {
                    Layout.fillWidth: true
                    spacing: 2
                    RowLayout {
                        Text {
                            text: model.title
                            color: MonodeskTheme.textPrimary
                            font.bold: true
                            font.pixelSize: 12
                        }
                        Item { Layout.fillWidth: true }
                        Text {
                            text: model.time
                            color: MonodeskTheme.textTertiary
                            font.family: MonodeskTheme.fontDisplay
                            font.pixelSize: 9
                        }
                    }
                    Text {
                        text: model.message
                        color: MonodeskTheme.textSecondary
                        font.pixelSize: 11
                        Layout.fillWidth: true
                        elide: Text.ElideRight
                    }
                }

                Text {
                    text: "✕"
                    color: MonodeskTheme.textTertiary
                    font.pixelSize: 12
                    MouseArea {
                        anchors.fill: parent
                        onClicked: notifModel.remove(index)
                    }
                }
            }
        }
    }
}
