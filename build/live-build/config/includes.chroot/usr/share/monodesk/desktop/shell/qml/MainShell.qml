import QtQuick 2.15
import QtQuick.Window 2.15
import QtQuick.Controls 2.15
import "../../themes" 1.0
import "../../dock/qml" 1.0
import "../../launcher/qml" 1.0
import "../../quick-search/qml" 1.0
import "../../control-centre/qml" 1.0
import "../../notifications/qml" 1.0
import "../../widgets/qml" 1.0

Window {
    id: root
    visible: true
    width: Screen.width
    height: Screen.height
    flags: Qt.FramelessWindowHint | Qt.WindowDoesNotAcceptFocus | Qt.WindowStaysOnBottomHint
    color: theme.surfaceBase

    // Theme instance
    property var theme: MonodeskTheme

    // Layer 0: Solid theme backing (safe fallback without compositor)
    Rectangle {
        anchors.fill: parent
        color: theme.surfaceBase
    }

    // Layer 1: Desktop Background & Watermark
    Image {
        id: wallpaper
        anchors.fill: parent
        source: theme.isDark ?
            "file:///usr/share/backgrounds/monodesk/monodesk-dark-dotmatrix.svg" :
            "file:///usr/share/backgrounds/monodesk/monodesk-light-dotmatrix.svg"
        fillMode: Image.PreserveAspectCrop
        asynchronous: true
    }

    // Layer 2: Desktop Telemetry Widgets (Top-Right / Modular)
    WidgetsContainer {
        id: desktopWidgets
        anchors.top: parent.top
        anchors.right: parent.right
        anchors.margins: 28
    }

    // Layer 3: The MONODESK Dock (Bottom Centered)
    MonodeskDock {
        id: dock
        anchors.bottom: parent.bottom
        anchors.horizontalCenter: parent.horizontalCenter
        anchors.bottomMargin: 16

        onLauncherTriggered: launcher.toggle()
        onControlCentreTriggered: controlCentre.toggle()
        onSearchTriggered: quickSearch.open()
    }

    // Layer 4: Overlays (Launcher, Quick Search, Control Centre, Notifications)
    MonodeskLauncher {
        id: launcher
        anchors.centerIn: parent
    }

    QuickSearch {
        id: quickSearch
        anchors.horizontalCenter: parent.horizontalCenter
        anchors.top: parent.top
        anchors.topMargin: 120
    }

    ControlCentre {
        id: controlCentre
        anchors.right: parent.right
        anchors.bottom: dock.top
        anchors.margins: 16
    }

    NotificationCenter {
        id: notifications
        anchors.top: parent.top
        anchors.right: parent.right
        anchors.topMargin: 296
        anchors.rightMargin: 28
    }

    // Global Shortcut Listener
    Shortcut {
        sequence: "Alt+Space"
        onActivated: quickSearch.toggle()
    }

    Shortcut {
        sequence: "Meta"
        onActivated: launcher.toggle()
    }
}
