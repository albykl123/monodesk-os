import QtQuick 2.15
import QtQuick.Controls 2.15
import QtQuick.Layouts 1.15
import "../../themes" 1.0

Rectangle {
    id: dock
    height: 56
    radius: MonodeskTheme.radiusPanel
    color: MonodeskTheme.surfacePanel
    border.color: MonodeskTheme.border
    border.width: 1

    signal launcherTriggered()
    signal controlCentreTriggered()
    signal searchTriggered()

    implicitWidth: dockLayout.implicitWidth + 24

    RowLayout {
        id: dockLayout
        anchors.centerIn: parent
        spacing: 10

        // 1. MONODESK Launcher Button
        Rectangle {
            id: btnLauncher
            width: 40; height: 40
            radius: MonodeskTheme.radiusCard
            color: mouseLauncher.containsMouse ? MonodeskTheme.surfaceCardHover : "transparent"

            Image {
                anchors.centerIn: parent
                width: 22; height: 22
                source: "file:///usr/share/icons/hicolor/scalable/apps/monodesk-icon.svg"
            }

            MouseArea {
                id: mouseLauncher
                anchors.fill: parent
                hoverEnabled: true
                onClicked: dock.launcherTriggered()
            }
        }

        // Separator
        Rectangle {
            width: 1; height: 24
            color: MonodeskTheme.border
        }

        // 2. Pinned & Core Applications Repeater
        ListModel {
            id: pinnedApps
            ListElement { name: "Files"; icon: "system-file-manager"; exec: "thunar"; running: false }
            ListElement { name: "Terminal"; icon: "utilities-terminal"; exec: "xfce4-terminal"; running: false }
            ListElement { name: "Browser"; icon: "firefox-esr"; exec: "firefox-esr"; running: false }
            ListElement { name: "Store"; icon: "system-software-install"; exec: "monodesk-store"; running: false }
            ListElement { name: "Settings"; icon: "preferences-system"; exec: "monodesk-settings"; running: false }
            ListElement { name: "Monitor"; icon: "utilities-system-monitor"; exec: "monodesk-system-monitor"; running: false }
        }

        Repeater {
            model: pinnedApps
            delegate: Rectangle {
                id: appItem
                width: 40; height: 40
                radius: MonodeskTheme.radiusCard
                color: itemMouse.containsMouse ? MonodeskTheme.surfaceCardHover : "transparent"

                Column {
                    anchors.centerIn: parent
                    spacing: 3

                    Image {
                        width: 24; height: 24
                        source: "image://icon/" + model.icon
                        fillMode: Image.PreserveAspectFit
                        // Fallback icon placeholder if icon theme unavailable
                        Rectangle {
                            anchors.fill: parent
                            visible: parent.status !== Image.Ready
                            color: MonodeskTheme.surfaceCardActive
                            radius: 4
                            Text {
                                anchors.centerIn: parent
                                text: model.name[0]
                                color: MonodeskTheme.textPrimary
                                font.family: MonodeskTheme.fontDisplay
                                font.bold: true
                            }
                        }
                    }

                    // Dot-matrix active running indicator
                    Rectangle {
                        width: 4; height: 4
                        radius: 2
                        color: model.running ? MonodeskTheme.accentRed : "transparent"
                        anchors.horizontalCenter: parent.horizontalCenter
                    }
                }

                MouseArea {
                    id: itemMouse
                    anchors.fill: parent
                    hoverEnabled: true
                    onClicked: {
                        if (typeof shellBridge !== "undefined") {
                            shellBridge.launchApp(model.exec);
                        }
                    }
                }
            }
        }

        // Separator
        Rectangle {
            width: 1; height: 24
            color: MonodeskTheme.border
        }

        // 3. Quick Search Button
        Rectangle {
            id: btnSearch
            width: 36; height: 36
            radius: MonodeskTheme.radiusCard
            color: searchMouse.containsMouse ? MonodeskTheme.surfaceCardHover : "transparent"

            Text {
                anchors.centerIn: parent
                text: "⌕"
                color: MonodeskTheme.textPrimary
                font.pixelSize: 18
            }

            MouseArea {
                id: searchMouse
                anchors.fill: parent
                hoverEnabled: true
                onClicked: dock.searchTriggered()
            }
        }

        // 4. Control Centre Quick Toggle Button
        Rectangle {
            id: btnControl
            width: 36; height: 36
            radius: MonodeskTheme.radiusCard
            color: controlMouse.containsMouse ? MonodeskTheme.surfaceCardHover : "transparent"

            Text {
                anchors.centerIn: parent
                text: "⚙"
                color: MonodeskTheme.textPrimary
                font.pixelSize: 16
            }

            MouseArea {
                id: controlMouse
                anchors.fill: parent
                hoverEnabled: true
                onClicked: dock.controlCentreTriggered()
            }
        }
    }
}
