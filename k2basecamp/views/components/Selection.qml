pragma ComponentBehavior: Bound
import QtQuick.Layouts
import QtQuick.Controls.Material
import QtQuick 2.15
import QtQuick.Controls 2.15
import QtQuick.Window

// Helper component to abstract some of the dropdown component logic.

RowLayout {
    id: selection
    required property string text
    required property var model
    required property var activatedHandler

    SpacerW {
    }
    Text {
        text: selection.text
        font.pointSize: 12
        Layout.fillWidth: true
        Layout.preferredWidth: 2
        color: "#e0e0e0"
    }
    ComboBox {
        id: control
        textRole: "text"
        valueRole: "value"
        model: selection.model
        Layout.fillWidth: true
        Layout.preferredWidth: 2
        Material.foreground: Material.foreground
        onActivated: () => selection.activatedHandler(currentValue) // qmllint disable use-proper-function
    }
    SpacerW {
    }
}
