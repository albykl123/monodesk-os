import QtQuick
import QtQuick.Controls

Item {
    id: profileBridge

    property string currentProfile: "standard"

    function loadProfile() {
        // Reads /etc/monodesk/profile or calls monodesk-profile-ctl --get
        var xhr = new XMLHttpRequest();
        xhr.open("GET", "file:///etc/monodesk/profile");
        xhr.onreadystatechange = function() {
            if (xhr.readyState === XMLHttpRequest.DONE) {
                if (xhr.status === 200 || xhr.responseText) {
                    profileBridge.currentProfile = xhr.responseText.trim();
                }
            }
        };
        xhr.send();
    }

    Component.onCompleted: loadProfile()
}
