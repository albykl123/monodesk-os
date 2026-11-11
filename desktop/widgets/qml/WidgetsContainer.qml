import QtQuick 2.15
import QtQuick.Layouts 1.15
import "../../../themes" 1.0

ColumnLayout {
    id: widgetsRoot
    width: 240
    spacing: 12

    // 1. Dot-Matrix Digital Clock & Calendar Widget
    Rectangle {
        Layout.fillWidth: true
        height: 84
        radius: MonodeskTheme.radiusPanel
        color: MonodeskTheme.surfacePanel
        border.color: MonodeskTheme.border
        border.width: 1

        ColumnLayout {
            anchors.centerIn: parent
            spacing: 2

            Text {
                id: clockText
                anchors.horizontalCenter: parent.horizontalCenter
                text: Qt.formatTime(new Date(), "hh:mm:ss")
                color: MonodeskTheme.textPrimary
                font.family: MonodeskTheme.fontDisplay
                font.pixelSize: 28
                font.bold: true
                font.letterSpacing: 2
            }

            Text {
                anchors.horizontalCenter: parent.horizontalCenter
                text: Qt.formatDate(new Date(), "ddd, dd MMM yyyy").toUpperCase()
                color: MonodeskTheme.textTertiary
                font.family: MonodeskTheme.fontDisplay
                font.pixelSize: 11
                font.letterSpacing: 1
            }
        }

        Timer {
            interval: 1000; running: true; repeat: true
            onTriggered: clockText.text = Qt.formatTime(new Date(), "hh:mm:ss")
        }
    }

    // 2. Hardware Resource Telemetry Widget
    Rectangle {
        Layout.fillWidth: true
        height: 140
        radius: MonodeskTheme.radiusPanel
        color: MonodeskTheme.surfacePanel
        border.color: MonodeskTheme.border
        border.width: 1

        ColumnLayout {
            anchors.fill: parent
            anchors.margins: 14
            spacing: 8

            Text {
                text: "SYSTEM TELEMETRY"
                color: MonodeskTheme.textTertiary
                font.family: MonodeskTheme.fontDisplay
                font.pixelSize: 10
                font.letterSpacing: 2
            }

            // CPU
            RowLayout {
                Layout.fillWidth: true
                Text { text: "CPU"; color: MonodeskTheme.textSecondary; font.family: MonodeskTheme.fontDisplay; font.pixelSize: 11 }
                Item { Layout.fillWidth: true }
                Text { id: cpuVal; text: "12%"; color: MonodeskTheme.textPrimary; font.family: MonodeskTheme.fontDisplay; font.pixelSize: 11; font.bold: true }
            }
            Rectangle {
                Layout.fillWidth: true; height: 3; radius: 2; color: MonodeskTheme.surfaceCardActive
                Rectangle { width: parent.width * 0.12; height: parent.height; radius: 2; color: MonodeskTheme.accentRed }
            }

            // RAM
            RowLayout {
                Layout.fillWidth: true
                Text { text: "RAM"; color: MonodeskTheme.textSecondary; font.family: MonodeskTheme.fontDisplay; font.pixelSize: 11 }
                Item { Layout.fillWidth: true }
                Text { id: ramVal; text: "1.8 / 16.0 GB"; color: MonodeskTheme.textPrimary; font.family: MonodeskTheme.fontDisplay; font.pixelSize: 11; font.bold: true }
            }
            Rectangle {
                Layout.fillWidth: true; height: 3; radius: 2; color: MonodeskTheme.surfaceCardActive
                Rectangle { width: parent.width * 0.22; height: parent.height; radius: 2; color: MonodeskTheme.accentRed }
            }

            // Power
            RowLayout {
                Layout.fillWidth: true
                Text { text: "PWR"; color: MonodeskTheme.textSecondary; font.family: MonodeskTheme.fontDisplay; font.pixelSize: 11 }
                Item { Layout.fillWidth: true }
                Text { text: "AC ONLINE"; color: MonodeskTheme.textPrimary; font.family: MonodeskTheme.fontDisplay; font.pixelSize: 11 }
            }
        }

        Connections {
            target: typeof shellBridge !== "undefined" ? shellBridge : null
            function onCpuChanged(val) {
                cpuVal.text = Math.round(val) + "%";
            }
            function onRamChanged(pct, used, total) {
                ramVal.text = used + " / " + total + " GB";
            }
        }
    }
}
