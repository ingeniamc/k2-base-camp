pragma ComponentBehavior: Bound
import QtQuick
import QtQuick.Controls.Material
import QtQuick.Layouts
import qmltypes.controllers 1.0
import "components" as Components

ApplicationWindow {
    id: page
    title: qsTr("K2 Base Camp")
    width: 800
    height: 600
    visible: true
    required property ConnectionController connectionController
    required property BootloaderController bootloaderController

    Connections {
        // Receive signals coming from the controllers.
        target: page.connectionController
        function onDrive_connected_triggered() {
            stack.push(controlsPage);
        }
        function onError_triggered(error_message) {
            errorMessageDialogLabel.text = error_message;
            errorMessageDialog.open();
        }
    }

    Shortcut {
        // Binds the emergency shutdown command to a keyboard key.
        sequence: "F12"
        context: Qt.ApplicationShortcut
        autoRepeat: false
        onActivated: () => page.connectionController.emergency_stop()
    }

    Dialog {
        // Error messages are displayed in this dialog.
        id: errorMessageDialog
        modal: true
        title: qsTr("An error occured")
        x: (parent.width - width) / 2
        y: (parent.height - height) / 2
        Label {
            id: errorMessageDialogLabel
        }
        standardButtons: Dialog.Ok
    }

    header: ToolBar {
        background: Rectangle {
            color: '#1b1b1b'
        }
        RowLayout {
            anchors.fill: parent
            ToolButton {
                id: disconnectButton
                text: qsTr("< Disconnect")
                visible: stack.depth == 3
                contentItem: Text {
                    text: disconnectButton.text
                    font: disconnectButton.font
                    opacity: enabled ? 1.0 : 0.3
                    color: disconnectButton.down ? "#009688" : "#e0e0e0"
                    horizontalAlignment: Text.AlignHCenter
                    verticalAlignment: Text.AlignVCenter
                    elide: Text.ElideRight
                }
                onClicked: () => {
                    page.connectionController.disconnect()
                    stack.pop()
                }
                Layout.preferredWidth: 3
                Layout.fillWidth: true
            }
            ToolButton {
                id: backButton
                text: qsTr("< Bootloader")
                visible: stack.depth == 2
                contentItem: Text {
                    text: backButton.text
                    font: backButton.font
                    opacity: enabled ? 1.0 : 0.3
                    color: backButton.down ? "#009688" : "#e0e0e0"
                    horizontalAlignment: Text.AlignHCenter
                    verticalAlignment: Text.AlignVCenter
                    elide: Text.ElideRight
                }
                onClicked: () => {
                    stack.pop()
                }
                Layout.preferredWidth: 3
                Layout.fillWidth: true
            }
            ToolButton {
                id: forwardButton
                text: qsTr("Connect >")
                visible: stack.depth == 1
                contentItem: Text {
                    text: forwardButton.text
                    font: forwardButton.font
                    opacity: enabled ? 1.0 : 0.3
                    color: forwardButton.down ? "#009688" : "#e0e0e0"
                    horizontalAlignment: Text.AlignHCenter
                    verticalAlignment: Text.AlignVCenter
                    elide: Text.ElideRight
                }
                onClicked: () => {
                    stack.push(selectionPage)
                }
                Layout.preferredWidth: 3
                Layout.fillWidth: true
            }
            Item {
                Layout.fillWidth: true
                Layout.preferredWidth: 6
            }

            Label {
                text: "Bootloader"
                visible: stack.depth == 1
                elide: Label.ElideRight
                horizontalAlignment: Qt.AlignHCenter
                verticalAlignment: Qt.AlignVCenter
                Layout.fillWidth: true
                Layout.preferredWidth: 4
                color: "#e0e0e0"
            }
            Label {
                text: "Connection"
                visible: stack.depth == 2
                elide: Label.ElideRight
                horizontalAlignment: Qt.AlignHCenter
                verticalAlignment: Qt.AlignVCenter
                Layout.fillWidth: true
                Layout.preferredWidth: 4
                color: "#e0e0e0"
            }
            Label {
                text: "Controls"
                visible: stack.depth == 3
                elide: Label.ElideRight
                horizontalAlignment: Qt.AlignHCenter
                verticalAlignment: Qt.AlignVCenter
                Layout.fillWidth: true
                Layout.preferredWidth: 4
                color: "#e0e0e0"
            }

            Item {
                Layout.fillWidth: true
                Layout.preferredWidth: 6
            }

            Components.Button {
                objectName: "emergencyStopBtn"
                text: "Stop (F12)"
                Layout.preferredWidth: 3
                Layout.fillWidth: true
                Material.background: '#b5341b'
                Material.foreground: '#ffffff'
                hoverColor: '#efa496'
                onClicked: () => page.connectionController.emergency_stop()
            }
        }
    }

    StackView {
        // Handles multiple pages layout.
        id: stack
        anchors.fill: parent
        focus: true
        Component.onCompleted: {
            stack.push(bootloaderPage)
            stack.push(selectionPage)
        }
    }

    BootloaderPage {
        // The first page is an interface to install firware files to the drives.
        id: bootloaderPage
        visible: false
        bootloaderController: page.bootloaderController
    }


    SelectionPage {
        // The main page is an interface to establish the connection with the drives.
        id: selectionPage
        visible: false
        connectionController: page.connectionController
    }

    ControlsPage {
        // The last page is an interface that allows manipulating the velocity of the connected motors.
        id: controlsPage
        visible: false
        connectionController: page.connectionController
    }
}
