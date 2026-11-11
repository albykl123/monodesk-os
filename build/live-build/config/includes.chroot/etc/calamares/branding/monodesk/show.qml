/* ==============================================================================
 * MONODESK OS — Calamares Installer Presentation Slideshow
 * The Monochrome Computing Experience
 * ============================================================================== */

import QtQuick 2.0;
import calamares.slideshow 1.0;

Presentation
{
    id: presentation

    Timer {
        interval: 15000
        repeat: true
        onTriggered: presentation.goToNextSlide()
    }

    Slide {
        Rectangle {
            anchors.fill: parent
            color: "#0b0c10"

            Column {
                anchors.centerIn: parent
                spacing: 16

                Text {
                    anchors.horizontalCenter: parent.horizontalCenter
                    text: "MONODESK OS 1.0"
                    color: "#ffffff"
                    font.pixelSize: 22
                    font.bold: true
                }

                Text {
                    anchors.horizontalCenter: parent.horizontalCenter
                    text: "The Monochrome Computing Experience"
                    color: "#a0a0a0"
                    font.pixelSize: 13
                }

                Text {
                    anchors.horizontalCenter: parent.horizontalCenter
                    text: "Installing system packages, hardware profile, and desktop environment...\nYour universal PC installation will complete in a few minutes."
                    color: "#e0e0e0"
                    font.pixelSize: 12
                    horizontalAlignment: Text.AlignHCenter
                }
            }
        }
    }
}
