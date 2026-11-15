import QtQuick 2.15
import QtQuick.Controls 2.15
import QtQuick.Layouts 1.15
import "../../themes" 1.0

Rectangle {
    id: quickSearchBox
    visible: false
    width: 620
    height: searchCol.implicitHeight + 28
    radius: MonodeskTheme.radiusPanel
    color: MonodeskTheme.surfacePanel
    border.color: MonodeskTheme.borderFocused
    border.width: 1

    function toggle() {
        visible = !visible;
        if (visible) {
            queryInput.text = "";
            queryInput.forceActiveFocus();
        }
    }

    function open() {
        visible = true;
        queryInput.text = "";
        queryInput.forceActiveFocus();
    }

    ColumnLayout {
        id: searchCol
        anchors.fill: parent
        anchors.margins: 14
        spacing: 12

        // Input Field
        RowLayout {
            Layout.fillWidth: true
            spacing: 10

            Text {
                text: "⌕"
                color: MonodeskTheme.accentRed
                font.pixelSize: 20
                font.bold: true
            }

            TextInput {
                id: queryInput
                Layout.fillWidth: true
                color: MonodeskTheme.textPrimary
                font.family: MonodeskTheme.fontBody
                font.pixelSize: 16
                clip: true

                Text {
                    anchors.fill: parent
                    text: "Search apps, settings, or actions (e.g. 'lock', 'settings', 'terminal')..."
                    color: MonodeskTheme.textTertiary
                    visible: !parent.text && !parent.activeFocus
                    font.pixelSize: 14
                }

                Keys.onEscapePressed: quickSearchBox.visible = false
                Keys.onReturnPressed: {
                    if (resultsList.count > 0) {
                        executeAction(resultsModel.get(resultsList.currentIndex));
                    }
                }
            }

            Text {
                text: "ESC"
                color: MonodeskTheme.textTertiary
                font.family: MonodeskTheme.fontDisplay
                font.pixelSize: 10
            }
        }

        Rectangle {
            Layout.fillWidth: true
            height: 1
            color: MonodeskTheme.border
        }

        // Search Results List
        ListModel {
            id: resultsModel
            ListElement { title: "Terminal"; type: "App"; action: "xfce4-terminal"; subtitle: "Open MONODESK Terminal" }
            ListElement { title: "Settings"; type: "App"; action: "monodesk-settings"; subtitle: "System Configuration" }
            ListElement { title: "Files"; type: "App"; action: "thunar"; subtitle: "File Manager" }
            ListElement { title: "Software Store"; type: "App"; action: "monodesk-store"; subtitle: "Install Packages" }
            ListElement { title: "Lock Screen"; type: "Action"; action: "xflock4"; subtitle: "Secure desktop session" }
            ListElement { title: "Power Off"; type: "Action"; action: "xfce4-session-logout"; subtitle: "Shut down system" }
        }

        ListView {
            id: resultsList
            Layout.fillWidth: true
            height: Math.min(resultsModel.count * 44, 220)
            clip: true
            model: resultsModel
            currentIndex: 0

            delegate: Rectangle {
                width: resultsList.width
                height: 40
                radius: MonodeskTheme.radiusCard
                color: ListView.isCurrentItem || mouseItem.containsMouse ? MonodeskTheme.surfaceCardHover : "transparent"

                RowLayout {
                    anchors.fill: parent
                    anchors.margins: 8
                    spacing: 12

                    Text {
                        text: model.title
                        color: MonodeskTheme.textPrimary
                        font.family: MonodeskTheme.fontBody
                        font.bold: true
                        font.pixelSize: 13
                    }

                    Text {
                        text: "• " + model.subtitle
                        color: MonodeskTheme.textSecondary
                        font.family: MonodeskTheme.fontBody
                        font.pixelSize: 12
                        Layout.fillWidth: true
                        elide: Text.ElideRight
                    }

                    Rectangle {
                        width: 48; height: 20
                        radius: 4
                        color: MonodeskTheme.surfaceCardActive
                        Text {
                            anchors.centerIn: parent
                            text: model.type
                            color: MonodeskTheme.textTertiary
                            font.family: MonodeskTheme.fontDisplay
                            font.pixelSize: 9
                        }
                    }
                }

                MouseArea {
                    id: mouseItem
                    anchors.fill: parent
                    hoverEnabled: true
                    onClicked: executeAction(model)
                }
            }
        }
    }

    function executeAction(item) {
        if (!item) return;
        if (typeof shellBridge !== "undefined") {
            shellBridge.launchApp(item.action);
        }
        quickSearchBox.visible = false;
    }
}
