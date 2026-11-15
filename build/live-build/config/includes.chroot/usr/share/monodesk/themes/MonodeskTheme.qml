pragma Singleton
import QtQuick 2.15

Item {
    id: theme

    // Mode: "dark" | "light" | "auto"
    property string mode: "dark"
    property bool isDark: mode === "dark" || (mode === "auto" && autoIsDark)
    property bool autoIsDark: true
    property bool reducedMotion: false

    // Color Palette
    readonly property color surfaceBase: isDark ? "#0A0A0C" : "#F6F6F8"
    readonly property color surfacePanel: isDark ? Qt.rgba(0.05, 0.05, 0.07, 0.94) : Qt.rgba(1.0, 1.0, 1.0, 0.94)
    readonly property color surfaceCard: isDark ? "#16161A" : "#FFFFFF"
    readonly property color surfaceCardHover: isDark ? "#222228" : "#EDEDF2"
    readonly property color surfaceCardActive: isDark ? "#2C2C34" : "#E0E0E6"
    readonly property color border: isDark ? "#26262C" : "#D8D8E0"
    readonly property color borderFocused: isDark ? "#FFFFFF" : "#000000"

    readonly property color textPrimary: isDark ? "#FFFFFF" : "#0E0E10"
    readonly property color textSecondary: isDark ? "#A0A0A8" : "#5C5C66"
    readonly property color textTertiary: isDark ? "#6C6C76" : "#8E8E98"

    readonly property color accentRed: "#E63946"
    readonly property color accentRedHover: isDark ? "#FF4D5E" : "#D62839"

    // Typography
    readonly property string fontDisplay: "JetBrains Mono"
    readonly property string fontBody: "Inter"

    // Geometry & Radii
    readonly property int radiusSmall: 4
    readonly property int radiusCard: 8
    readonly property int radiusPanel: 12
    readonly property int radiusPill: 999

    // Animation Timings
    readonly property int animFast: reducedMotion ? 0 : 120
    readonly property int animNormal: reducedMotion ? 0 : 200
    readonly property int animSlow: reducedMotion ? 0 : 350

    function toggleTheme() {
        if (mode === "dark") {
            mode = "light";
        } else {
            mode = "dark";
        }
    }
}
