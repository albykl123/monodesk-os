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
            refreshApps();
            searchInput.forceActiveFocus();
        }
    }

    function refreshApps() {
        appCatalog.clear();
        var apps = (typeof shellBridge !== "undefined" && shellBridge.getInstalledApps) ? shellBridge.getInstalledApps() : [];
        if (!apps || apps.length === 0) {
            apps = [
                { name: "Files", category: "System", exec: "thunar", desc: "Browse files and drives", icon: "system-file-manager" },
                { name: "Terminal", category: "Development", exec: "xfce4-terminal", desc: "Command prompt", icon: "utilities-terminal" },
                { name: "Web Browser", category: "Internet", exec: "firefox-esr", desc: "Browse the web", icon: "firefox-esr" },
                { name: "Software Store", category: "System", exec: "monodesk-store", desc: "Software packages", icon: "system-software-install" },
                { name: "System Settings", category: "Settings", exec: "monodesk-settings", desc: "System configuration", icon: "preferences-system" },
                { name: "System Monitor", category: "System", exec: "monodesk-system-monitor", desc: "Task manager", icon: "utilities-system-monitor" },
                { name: "Text Editor", category: "Accessories", exec: "mousepad", desc: "Simple text editor", icon: "accessories-text-editor" },
                { name: "Calculator", category: "Accessories", exec: "galculator", desc: "Scientific calculator", icon: "accessories-calculator" },
                { name: "Document Viewer", category: "Office", exec: "qpdfview", desc: "PDF and document reader", icon: "x-office-document" },
                { name: "Image Viewer", category: "Graphics", exec: "ristretto", desc: "Photo and image viewer", icon: "image-x-generic" },
                { name: "Archive Manager", category: "System", exec: "file-roller", desc: "Archive manager", icon: "package-x-generic" },
                { name: "Screenshot Utility", category: "Accessories", exec: "xfce4-screenshooter", desc: "Screen capture tool", icon: "applets-screenshooter" },
                { name: "Hardware Centre", category: "System", exec: "monodesk-hardware-centre", desc: "Diagnostic reports", icon: "hardware" },
                { name: "Install MONODESK OS", category: "System", exec: "calamares", desc: "Universal PC Installer", icon: "calamares" }
            ];
        }
        var filter = searchInput.text.toLowerCase().trim();
        for (var i = 0; i < apps.length; i++) {
            var item = apps[i];
            if (!filter || item.name.toLowerCase().indexOf(filter) !== -1 || (item.desc && item.desc.toLowerCase().indexOf(filter) !== -1) || (item.category && item.category.toLowerCase().indexOf(filter) !== -1)) {
                appCatalog.append(item);
            }
        }
    }

    Component.onCompleted: refreshApps()

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
                    onTextChanged: launcherOverlay.refreshApps()

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

                        Image {
                            anchors.centerIn: parent
                            width: 24; height: 24
                            source: "image://icon/" + (model.icon || "application-x-executable")
                            fillMode: Image.PreserveAspectFit
                            visible: status === Image.Ready
                        }

                        Text {
                            anchors.centerIn: parent
                            visible: parent.children[0].status !== Image.Ready
                            text: model.name ? model.name[0] : "M"
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
