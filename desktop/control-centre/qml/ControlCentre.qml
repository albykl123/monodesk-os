import QtQuick 2.15
import QtQuick.Controls 2.15
import QtQuick.Layouts 1.15
import "../../themes" 1.0

Rectangle {
    id: controlCentrePanel
    visible: false
    width: 380
    height: 520
    radius: MonodeskTheme.radiusPanel
    color: MonodeskTheme.surfacePanel
    border.color: MonodeskTheme.border
    border.width: 1

    property bool wifiConnected: true
    property string wifiSsid: "Active"
    property bool btActive: true

    Connections {
        target: typeof shellBridge !== "undefined" ? shellBridge : null
        ignoreUnknownSignals: true
        function onWifiChanged(connected, ssid) {
            wifiConnected = connected
            wifiSsid = ssid
        }
        function onBluetoothChanged(powered) {
            btActive = powered
        }
    }

    function toggle() {
        visible = !visible;
    }

    ColumnLayout {
        anchors.fill: parent
        anchors.margins: 18
        spacing: 14

        // Header
        RowLayout {
            Layout.fillWidth: true

            Text {
                text: "CONTROL CENTRE"
                color: MonodeskTheme.textPrimary
                font.family: MonodeskTheme.fontDisplay
                font.pixelSize: 14
                font.bold: true
                font.letterSpacing: 2
            }

            Item { Layout.fillWidth: true }

            // Theme switch pill button
            Rectangle {
                width: 70; height: 26
                radius: MonodeskTheme.radiusPill
                color: MonodeskTheme.surfaceCard
                border.color: MonodeskTheme.border

                Text {
                    anchors.centerIn: parent
                    text: MonodeskTheme.isDark ? "DARK" : "LIGHT"
                    color: MonodeskTheme.textPrimary
                    font.family: MonodeskTheme.fontDisplay
                    font.pixelSize: 10
                    font.bold: true
                }

                MouseArea {
                    anchors.fill: parent
                    onClicked: MonodeskTheme.toggleTheme()
                }
            }
        }

        // Quick Toggles Grid (Wi-Fi & Bluetooth)
        RowLayout {
            Layout.fillWidth: true
            spacing: 10

            Rectangle {
                Layout.fillWidth: true
                height: 54
                radius: MonodeskTheme.radiusCard
                color: wifiConnected ? (wifiMouse.containsMouse ? MonodeskTheme.surfaceCardHover : MonodeskTheme.surfaceCard) : MonodeskTheme.surfaceCardActive
                border.color: wifiConnected ? MonodeskTheme.accentRed : MonodeskTheme.border

                RowLayout {
                    anchors.fill: parent
                    anchors.margins: 10
                    spacing: 8

                    Text {
                        text: "📶"
                        color: wifiConnected ? MonodeskTheme.textPrimary : MonodeskTheme.textTertiary
                        font.pixelSize: 16
                    }

                    ColumnLayout {
                        Text {
                            text: "Wi-Fi"
                            color: MonodeskTheme.textPrimary
                            font.bold: true
                            font.pixelSize: 12
                        }
                        Text {
                            text: wifiConnected ? wifiSsid : "Disconnected"
                            color: MonodeskTheme.textSecondary
                            font.pixelSize: 10
                            elide: Text.ElideRight
                            Layout.maximumWidth: 100
                        }
                    }
                }
                MouseArea {
                    id: wifiMouse
                    anchors.fill: parent
                    onClicked: {
                        if (typeof shellBridge !== "undefined") {
                            shellBridge.toggleWifi(!wifiConnected)
                        }
                    }
                }
            }

            Rectangle {
                Layout.fillWidth: true
                height: 54
                radius: MonodeskTheme.radiusCard
                color: btActive ? (btMouse.containsMouse ? MonodeskTheme.surfaceCardHover : MonodeskTheme.surfaceCard) : MonodeskTheme.surfaceCardActive
                border.color: btActive ? MonodeskTheme.accentRed : MonodeskTheme.border

                RowLayout {
                    anchors.fill: parent
                    anchors.margins: 10
                    spacing: 8

                    Text {
                        text: "ᛒ"
                        color: btActive ? MonodeskTheme.textPrimary : MonodeskTheme.textTertiary
                        font.pixelSize: 16
                    }

                    ColumnLayout {
                        Text {
                            text: "Bluetooth"
                            color: MonodeskTheme.textPrimary
                            font.bold: true
                            font.pixelSize: 12
                        }
                        Text {
                            text: btActive ? "Enabled" : "Disabled"
                            color: MonodeskTheme.textSecondary
                            font.pixelSize: 10
                        }
                    }
                }
                MouseArea {
                    id: btMouse
                    anchors.fill: parent
                    onClicked: {
                        if (typeof shellBridge !== "undefined") {
                            shellBridge.toggleBluetooth(!btActive)
                        }
                    }
                }
            }
        }

        // Sliders (Volume & Brightness)
        ColumnLayout {
            Layout.fillWidth: true
            spacing: 6

            Text {
                text: "AUDIO OUTPUT"
                color: MonodeskTheme.textTertiary
                font.family: MonodeskTheme.fontDisplay
                font.pixelSize: 10
            }

            Slider {
                id: volSlider
                Layout.fillWidth: true
                from: 0; to: 100; value: 65
                onValueChanged: {
                    if (typeof shellBridge !== "undefined") {
                        shellBridge.setSystemVolume("@DEFAULT_SINK@", Math.round(value));
                    }
                }
            }
        }

        ColumnLayout {
            Layout.fillWidth: true
            spacing: 6

            Text {
                text: "DISPLAY BRIGHTNESS"
                color: MonodeskTheme.textTertiary
                font.family: MonodeskTheme.fontDisplay
                font.pixelSize: 10
            }

            Slider {
                id: brightSlider
                Layout.fillWidth: true
                from: 10; to: 100; value: 80
                onValueChanged: {
                    if (typeof shellBridge !== "undefined") {
                        shellBridge.setBrightness(Math.round(value));
                    }
                }
            }
        }

        // Power Profiles Row
        ColumnLayout {
            Layout.fillWidth: true
            spacing: 6

            Text {
                text: "POWER PROFILE"
                color: MonodeskTheme.textTertiary
                font.family: MonodeskTheme.fontDisplay
                font.pixelSize: 10
            }

            RowLayout {
                Layout.fillWidth: true
                spacing: 8

                property string activeProfile: "balanced"

                Repeater {
                    model: ["saver", "balanced", "perf"]
                    delegate: Rectangle {
                        Layout.fillWidth: true
                        height: 32
                        radius: MonodeskTheme.radiusCard
                        color: parent.activeProfile === modelData ? MonodeskTheme.accentRed : MonodeskTheme.surfaceCard
                        border.color: MonodeskTheme.border

                        Text {
                            anchors.centerIn: parent
                            text: modelData.toUpperCase()
                            color: parent.color == MonodeskTheme.accentRed ? "#FFFFFF" : MonodeskTheme.textPrimary
                            font.family: MonodeskTheme.fontDisplay
                            font.pixelSize: 10
                            font.bold: true
                        }

                        MouseArea {
                            anchors.fill: parent
                            onClicked: {
                                parent.parent.activeProfile = modelData;
                                if (typeof shellBridge !== "undefined") {
                                    shellBridge.setPowerProfile(modelData == "saver" ? "lite" : "standard");
                                }
                            }
                        }
                    }
                }
            }
        }

        Item { Layout.fillHeight: true }

        // Session Management Buttons
        RowLayout {
            Layout.fillWidth: true
            spacing: 6

            Button {
                Layout.fillWidth: true
                text: "Lock"
                onClicked: {
                    if (typeof shellBridge !== "undefined") shellBridge.lockScreen()
                    controlCentrePanel.visible = false
                }
            }

            Button {
                Layout.fillWidth: true
                text: "Log Out"
                onClicked: {
                    if (typeof shellBridge !== "undefined") shellBridge.logoutSession()
                    controlCentrePanel.visible = false
                }
            }

            Button {
                Layout.fillWidth: true
                text: "Restart"
                onClicked: {
                    if (typeof shellBridge !== "undefined") shellBridge.restartSystem()
                    controlCentrePanel.visible = false
                }
            }

            Button {
                Layout.fillWidth: true
                text: "Shut Down"
                onClicked: {
                    if (typeof shellBridge !== "undefined") shellBridge.shutdownSystem()
                    controlCentrePanel.visible = false
                }
            }
        }

        // Bottom Navigation Row
        RowLayout {
            Layout.fillWidth: true
            spacing: 8

            Button {
                Layout.fillWidth: true
                text: "Settings"
                onClicked: {
                    if (typeof shellBridge !== "undefined") shellBridge.launchApp("monodesk-settings");
                    controlCentrePanel.visible = false;
                }
            }

            Button {
                Layout.fillWidth: true
                text: "Diagnostics"
                onClicked: {
                    if (typeof shellBridge !== "undefined") shellBridge.launchApp("monodesk-hardware-centre");
                    controlCentrePanel.visible = false;
                }
            }
        }
    }
}
