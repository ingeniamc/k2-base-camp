pragma ComponentBehavior: Bound
import QtQuick.Layouts
import "components" as Components
import QtQuick.Controls.Material
import qmltypes.controllers 1.0
import QtQuick 2.15
import QtQuick.Controls 2.15
import QtQuick.Dialogs

// QEnum() does not seem to work properly with qmllint,
// which is why we disable this warning for this file.
// This only applies to the usage of Enums, if that is
// no longer used, the warning can be re-enabled.
// qmllint disable missing-property

ColumnLayout {
    id: bootloaderPage
    required property BootloaderController bootloaderController

    Connections {
        target: bootloaderPage.bootloaderController
        function onFirmware_changed(firmware, drive) {
            if (drive === Enums.Drive.Left) {
                firmwareFileLeft.text = firmware;
                resetFirmwareLeft.visible = true;
                firmwareButtonLeft.enabled = false;
            } else {
                firmwareFileRight.text = firmware;
                resetFirmwareRight.visible = true;
                firmwareButtonRight.enabled = false;
            }
        }
        function onInstall_button_state_changed(new_state) {
            installBtn.state = new_state;
        }
        function onServo_ids_changed(servo_ids) {
            const servo_ids_model = servo_ids.map((servo_id) => { return {
                value: servo_id,
                text: servo_id
            }});
            idLeftAutomatic.model = servo_ids_model;
            idLeftAutomatic.enabled = true;
            // Handle if the scan returned only one servo
            if (servo_ids_model.length > 1) {
                idRightAutomatic.model = servo_ids_model;
                idRightAutomatic.incrementCurrentIndex();
                idRightAutomatic.enabled = true;
            } else {
                idRightAutomatic.enabled = false;
            }
            idsAutomatic.visible = true;
        }
        function onFirmware_installation_progress_changed(progress) {
            progressDialogBar.value = progress;
            progressDialogBar.indeterminate = progress < 100 ? false : true;
        }
        function onFirmware_installation_complete_triggered() {
            progressDialogBar.indeterminate = true;
            progressDialogButtons.visible = true
            progressDialogBar.visible = false
            isInProgress.visible = false
            progressDialog.close();
        }
        function onError_triggered(error_message) {
            progressDialogBar.indeterminate = true;
            progressDialogButtons.visible = true
            progressDialogBar.visible = false
            isInProgress.visible = false
            progressDialog.close();
        }
    }

    Dialog {
        // Dialog to confirm the installation of firmware. 
        // Will block the application during installation and show a progress bar.
        // Closes and resets on error or completion.
        id: progressDialog
        modal: true
        closePolicy: Popup.NoAutoClose
        title: qsTr("Installing firmware..")
        x: (parent.width - width) / 2
        y: (parent.height - height) / 2
        
        ColumnLayout {
            anchors.fill: parent
            Label {
                text: "Installation can take several minutes."
                Layout.fillHeight: true
            }
            Label {
                text: "Please do not disconnect the drive while the process is in progress!"
                Layout.fillHeight: true
            }
            Label {
                id: isInProgress
                visible: false
                text: "Installation in progress.."
                Layout.fillHeight: true
            }
            Components.SpacerH {}
            ProgressBar {
                id: progressDialogBar
                visible: false
                from: 0
                to: 100
                value: 0
                indeterminate: true
                Layout.fillHeight: true
                Layout.fillWidth: true
            }
        }

        footer: DialogButtonBox {
            id: progressDialogButtons
            Button {
                text: qsTr("Cancel")
                DialogButtonBox.buttonRole: DialogButtonBox.RejectRole
            }
            Button {
                text: qsTr("Install")
                DialogButtonBox.buttonRole: DialogButtonBox.ApplyRole
            }
            
            onApplied: () => {
                bootloaderPage.bootloaderController.install_firmware();
                progressDialogButtons.visible = false
                progressDialogBar.visible = true
                isInProgress.visible = true
            }
        }
    }


    FileDialog {
        // Input for firmware file (left drive).
        id: firmwarefileLeftDialog
        title: "Please choose a file"
        defaultSuffix: "lfu"
        fileMode: FileDialog.OpenFile
        nameFilters: ["LFU Files (*.lfu)", "SFU Files (*.sfu)"]
        onAccepted: {
            bootloaderPage.bootloaderController.select_firmware(selectedFile, Enums.Drive.Left);
        }
    }

    FileDialog {
        // Input for firmware file (right drive).
        id: firmwarefileRightDialog
        title: "Please choose a file"
        defaultSuffix: "lfu"
        fileMode: FileDialog.OpenFile
        nameFilters: ["LFU Files (*.lfu)", "SFU Files (*.sfu)"]
        onAccepted: {
            bootloaderPage.bootloaderController.select_firmware(selectedFile, Enums.Drive.Right);
        }
    }

    Components.Selection {
        text: "Select connection mode:"
        model: [{
                value: Enums.ConnectionProtocol.CANopen,
                text: "CANopen"
            }, {
                value: Enums.ConnectionProtocol.EtherCAT,
                text: "EtherCAT"
            }]
        activatedHandler: currentValue => {
            bootloaderPage.bootloaderController.select_connection(currentValue);
            selectCANdevice.visible = currentValue == Enums.ConnectionProtocol.CANopen;
            selectBaudrate.visible = currentValue == Enums.ConnectionProtocol.CANopen;
            selectNetworkAdapter.visible = currentValue == Enums.ConnectionProtocol.EtherCAT;
            idLeftAutomatic.model = [];
            idRightAutomatic.model = [];
            idLeftAutomatic.enabled = false;
            idRightAutomatic.enabled = false;
            bootloaderPage.bootloaderController.reset_firmware(Enums.Drive.Left);
            resetFirmwareLeft.visible = false;
            firmwareButtonLeft.enabled = true;
            bootloaderPage.bootloaderController.reset_firmware(Enums.Drive.Right);
            resetFirmwareRight.visible = false;
            firmwareButtonRight.enabled = true;
        }
    }

    Components.Selection {
        id: selectNetworkAdapter
        text: "Select network adapter:"
        model: []
        visible: false
        Component.onCompleted: () => {
            const interface_name_list = bootloaderPage.bootloaderController.get_interface_name_list();
            selectNetworkAdapter.model = interface_name_list.map((interface_name, index) => {
                    return {
                        value: index,
                        text: interface_name
                    };
                });
        }
        activatedHandler: currentValue => bootloaderPage.bootloaderController.select_interface(currentValue)
    }

    Components.Selection {
        id: selectCANdevice
        text: "Select CAN device:"
        model: [{
                value: Enums.CanDevice.KVASER,
                text: "KVASER"
            }, {
                value: Enums.CanDevice.PCAN,
                text: "PCAN"
            }, {
                value: Enums.CanDevice.IXXAT,
                text: "IXXAT"
            }]
        activatedHandler: currentValue => bootloaderPage.bootloaderController.select_can_device(currentValue)
    }

    Components.Selection {
        id: selectBaudrate
        text: "Select baudrate:"
        model: [{
                value: Enums.CAN_BAUDRATE.Baudrate_1M,
                text: "1 Mbit/s"
            }, {
                value: Enums.CAN_BAUDRATE.Baudrate_500K,
                text: "500 Kbit/s"
            }, {
                value: Enums.CAN_BAUDRATE.Baudrate_250K,
                text: "250 Kbit/s"
            }, {
                value: Enums.CAN_BAUDRATE.Baudrate_125K,
                text: "125 Kbit/s"
            }, {
                value: Enums.CAN_BAUDRATE.Baudrate_100K,
                text: "100 Kbit/s"
            }, {
                value: Enums.CAN_BAUDRATE.Baudrate_50K,
                text: "50 Kbit/s"
            }]
        activatedHandler: currentValue => bootloaderPage.bootloaderController.select_can_baudrate(currentValue)
    }

    RowLayout {
        Components.SpacerW {
        }
        Text {
            text: "Connection mode:"
            font.pointSize: 12
            Layout.fillWidth: true
            Layout.preferredWidth: 2
            color: "#e0e0e0"
        }
        ComboBox {
            id: control
            textRole: "text"
            valueRole: "value"
            model: [{
                value: "Scan",
                text: "Scan"
            },
            {
                value: "Manual",
                text: "Manual"
            }]
            Layout.fillWidth: true
            Layout.preferredWidth: 2
            Material.foreground: Material.foreground
            onActivated: () => {
                scanButton.visible = (currentValue == "Scan");
                idsAutomatic.visible = (currentValue == "Scan" && idLeftAutomatic.model?.length > 0);
                idsManual.visible = (currentValue == "Manual");
            }
        }
        Components.SpacerW {
        }
        Components.Button {
            id: scanButton
            text: "Scan"
            Layout.fillWidth: true
            Layout.preferredWidth: 1
            Material.background: '#007acc'
            Material.foreground: '#FFFFFF'
            hoverColor: '#85ceff'
            onClicked: () => {
                bootloaderPage.bootloaderController.scan_servos();
            }
        }
        Components.SpacerW {
        }
    }

    RowLayout {
        // Manual input for slave / node IDs.
        id: idsManual
        visible: false
        Components.SpacerW {
        }
        Text {
            text: "ID Left:"
            font.pointSize: 12
            Layout.fillWidth: true
            Layout.preferredWidth: 4
            color: "#e0e0e0"
        }
        SpinBox {
            id: idLeft
            Layout.fillWidth: true
            Layout.preferredWidth: 4
            from: 0
            editable: true
            onValueModified: () => bootloaderPage.bootloaderController.select_node_id(value, Enums.Drive.Left)
        }
        Components.SpacerW {
        }
        Text {
            text: "ID Right:"
            font.pointSize: 12
            Layout.fillWidth: true
            Layout.preferredWidth: 4
            color: "#e0e0e0"
        }
        SpinBox {
            id: idRight
            Layout.fillWidth: true
            Layout.preferredWidth: 4
            from: 0
            editable: true
            onValueModified: () => bootloaderPage.bootloaderController.select_node_id(value, Enums.Drive.Right)
        }
        Components.SpacerW {
        }
    }

    RowLayout {
        // Slave / node IDs returned from a scan.
        id: idsAutomatic
        visible: false
        Components.SpacerW {
        }
        Text {
            text: "ID Left:"
            font.pointSize: 12
            Layout.fillWidth: true
            Layout.preferredWidth: 2
            color: "#e0e0e0"
        }
        ComboBox {
            id: idLeftAutomatic
            textRole: "text"
            valueRole: "value"
            enabled: false
            model: []
            Layout.fillWidth: true
            Layout.preferredWidth: 2
            Material.foreground: Material.foreground
            onActivated: () => bootloaderPage.bootloaderController.select_node_id(currentValue, Enums.Drive.Left)
        }
        Components.SpacerW {
        }
        Text {
            text: "ID Right:"
            font.pointSize: 12
            Layout.fillWidth: true
            Layout.preferredWidth: 2
            color: "#e0e0e0"
        }
        ComboBox {
            id: idRightAutomatic
            textRole: "text"
            valueRole: "value"
            enabled: false
            model: []
            Layout.fillWidth: true
            Layout.preferredWidth: 2
            Material.foreground: Material.foreground
            onActivated: () => bootloaderPage.bootloaderController.select_node_id(currentValue, Enums.Drive.Right)
        }
        Components.SpacerW {
        }
    }

    RowLayout {
        // Button for firmware file upload & display of currently selected file,
        // as well as a button to clear the firmware file.
        Components.SpacerW {
        }
        ColumnLayout {
            Layout.fillWidth: true
            Layout.preferredWidth: 2
            Components.Button {
                id: firmwareButtonLeft
                text: "Choose firmware left..."
                onClicked: firmwarefileLeftDialog.open()
            }
            RowLayout {
                Layout.alignment: Qt.AlignHCenter
                Text {
                    id: firmwareFileLeft
                    color: '#e0e0e0'
                }
                RoundButton {
                    id: resetFirmwareLeft
                    text: "X"
                    visible: false
                    onClicked: () => {
                        bootloaderPage.bootloaderController.reset_firmware(Enums.Drive.Left);
                        resetFirmwareLeft.visible = false;
                        firmwareButtonLeft.enabled = true;
                    }
                }
            }
        }
        Components.SpacerW {
        }
        ColumnLayout {
            Layout.fillWidth: true
            Layout.preferredWidth: 2
            Components.Button {
                id: firmwareButtonRight
                text: "Choose firmware right..."
                onClicked: firmwarefileRightDialog.open()
            }
            RowLayout {
                Layout.alignment: Qt.AlignHCenter
                Text {
                    id: firmwareFileRight
                    color: '#e0e0e0'
                }
                RoundButton {
                    id: resetFirmwareRight
                    text: "X"
                    visible: false
                    onClicked: () => {
                        bootloaderPage.bootloaderController.reset_firmware(Enums.Drive.Right);
                        resetFirmwareRight.visible = false;
                        firmwareButtonRight.enabled = true;
                    }
                }
            }
        }
        Components.SpacerW {
        }
    }


    RowLayout {
        // Button to open the installation dialog. 
        // Only active (clickable) when the pre-requisites for installation are met 
        // (at least a firmware file was uploaded, configuration for the ConnectionProtocol,
        // a node was selected for the drive we want to change).
        Components.SpacerW {
        }
        Components.Button {
            id: installBtn
            text: "Install firmware"
            Material.background: '#2ffcab'
            Material.foreground: '#1b1b1b'
            hoverColor: '#acfedd'
            Layout.fillWidth: true
            Layout.preferredWidth: 1
            state: Enums.ButtonState.Disabled
            states: [
                State {
                    name: Enums.ButtonState.Enabled
                    PropertyChanges {
                        target: installBtn
                        enabled: true
                    }
                },
                State {
                    name: Enums.ButtonState.Disabled
                    PropertyChanges {
                        target: installBtn
                        enabled: false
                    }
                }
            ]
            onClicked: () => {
                progressDialog.open()
            }
        }
        Components.SpacerW {
        }
    }
}
