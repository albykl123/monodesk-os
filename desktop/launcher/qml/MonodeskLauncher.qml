import QtQuick 2.15
import QtQuick.Controls 2.15
import QtQuick.Layouts 1.15
import "../../themes" 1.0

Rectangle {
    id: launcherOverlay
    visible: false
    width: 680
    height: 520
    radius: MonodeskTheme.radiusPanel
    color: MonodeskTheme.surfacePanel
    border.color: MonodeskTheme.border
    border.width: 1

    function toggle() {
        visible = !visible;
        if (visible) {
            searchInput.text = "";
            searchInput.forceActiveFocus();
        }
    }

    ColumnLayout {
        anchors.fill: parent
        anchors.margins: 24
        spacing: 16

        // Header
        RowLayout {
            Layout.fillWidth: true

            Text {
                text: "APPLICATIONS"
                color: MonodeskTheme.textPrimary
                font.family: MonodeskTheme.fontDisplay
                font.pixelSize: 16
                font.bold: true
                font.letterSpacing: 2
            }

            Item { Layout.fillWidth: true }

            Text {
                text: "ESC to close"
                color: MonodeskTheme.textTertiary
                font.family: MonodeskTheme.fontDisplay
                font.pixelSize: 11
            }
        }

        // Search Input
        Rectangle {
            Layout.fillWidth: true
            height: 42
            radius: MonodeskTheme.radiusCard
            color: MonodeskTheme.surfaceCard
            border.color: searchInput.activeFocus ? MonodeskTheme.borderFocused : MonodeskTheme.border

            RowLayout {
                anchors.fill: parent
                anchors.margins: 10
                spacing: 8

                Text {
                    text: "⌕"
                    color: MonodeskTheme.textSecondary
                    font.pixelSize: 16
                }

                TextInput {
                    id: searchInput
                    Layout.fillWidth: true
                    color: MonodeskTheme.textPrimary
                    font.family: MonodeskTheme.fontBody
                    font.pixelSize: 14
                    clip: true

                    Text {
                        anchors.fill: parent
                        text: "Type to search applications..."
                        color: MonodeskTheme.textTertiary
                        visible: !parent.text && !parent.activeFocus
                        font.pixelSize: 14
                    }

                    Keys.onEscapePressed: launcherOverlay.visible = false
                }
            }
        }

        // Applications Grid
        ListModel {
            id: appCatalog
            ListElement { name: "Files"; category: "System"; exec: "thunar"; desc: "Browse files and drives" }
            ListElement { name: "Terminal"; category: "Development"; exec: "xfce4-terminal"; desc: "Monochrome command prompt" }
            ListElement { name: "Web Browser"; category: "Internet"; exec: "firefox-esr"; desc: "Browse the internet" }
            ListElement { name: "Software Store"; category: "System"; exec: "monodesk-store"; desc: "Discover and install apps" }
            ListElement { name: "System Settings"; category: "Settings"; exec: "monodesk-settings"; desc: "Configure desktop and devices" }
            ListElement { name: "Hardware Centre"; category: "System"; exec: "monodesk-hardware-centre"; desc: "Diagnostic reports and drivers" }
            ListElement { name: "System Monitor"; category: "System"; exec: "monodesk-system-monitor"; desc: "Inspect processes and usage" }
            ListElement { name: "Privacy Dashboard"; category: "Security"; exec: "monodesk-privacy"; desc: "Firewall and permission control" }
            ListElement { name: "Backup Manager"; category: "Utilities"; exec: "monodesk-backup"; desc: "Safeguard personal data" }
            ListElement { name: "Recovery Centre"; category: "System"; exec: "monodesk-recovery"; desc: "System diagnostics and repair" }
            ListElement { name: "Update Manager"; category: "System"; exec: "monodesk-updater"; desc: "Debian security updates" }
            ListElement { name: "Local AI Assistant"; category: "Utilities"; exec: "monodesk-ai"; desc: "Offline private assistant" }
        }

        GridView {
            id: gridView
            Layout.fillWidth: true
            Layout.fillHeight: true
            cellWidth: 200; cellHeight: 80
            clip: true

            model: appCatalog
            delegate: Rectangle {
                width: 190; height: 70
                radius: MonodeskTheme.radiusCard
                color: mouseApp.containsMouse ? MonodeskTheme.surfaceCardHover : MonodeskTheme.surfaceCard
                border.color: MonodeskTheme.border

                RowLayout {
                    anchors.fill: parent
                    anchors.margins: 10
                    spacing: 10

                    Rectangle {
                        width: 38; height: 38
                        radius: MonodeskTheme.radiusCard
                        color: MonodeskTheme.surfaceCardActive
                        Text {
                            anchors.centerIn: parent
                            text: model.name[0]
                            color: MonodeskTheme.accentRed
                            font.family: MonodeskTheme.fontDisplay
                            font.bold: true
                            font.pixelSize: 16
                        }
                    }

                    ColumnLayout {
                        Layout.fillWidth: true
                        spacing: 2
                        Text {
                            text: model.name
                            color: MonodeskTheme.textPrimary
                            font.family: MonodeskTheme.fontBody
                            font.bold: true
                            font.pixelSize: 13
                            elide: Text.ElideRight
                        }
                        Text {
                            text: model.category
                            color: MonodeskTheme.textTertiary
                            font.family: MonodeskTheme.fontDisplay
                            font.pixelSize: 10
                        }
                    }
                }

                MouseArea {
                    id: mouseApp
                    anchors.fill: parent
                    hoverEnabled: true
                    onClicked: {
                        if (typeof shellBridge !== "undefined") {
                            shellBridge.launchApp(model.exec);
                        }
                        launcherOverlay.visible = false;
                    }
                }
            }
        }
    }
}
