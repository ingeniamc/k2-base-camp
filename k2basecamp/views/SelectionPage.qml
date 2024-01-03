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
    id: selectionPage
    required property ConnectionController connectionController

    Connections {
        target: selectionPage.connectionController
        function onDictionary_changed(dictionary) {
            dictionaryFile.text = dictionary;
            resetDictionary.visible = true;
            dictionaryButton.enabled = false;
        }
        function onConnect_button_state_changed(new_state) {
            connectBtn.state = new_state;
        }
        function onServo_ids_changed(servo_ids) {
            const servo_ids_model = servo_ids.map((servo_id) => { return {
                value: servo_id,
                text: servo_id
            }});
            idLeftAutomatic.model = servo_ids_model;
            idRightAutomatic.model = servo_ids_model;
            idRightAutomatic.incrementCurrentIndex();
            idLeftAutomatic.enabled = true;
            idRightAutomatic.enabled = true;
            idsAutomatic.visible = true;
        }
        function onConfig_changed(config, drive) {
            if (drive === Enums.Drive.Left) {
                configFileLeft.text = config;
                resetConfigLeft.visible = true;
                configButtonLeft.enabled = false;
            } else {
                configFileRight.text = config;
                resetConfigRight.visible = true;
                configButtonRight.enabled = false;
            }
        }
    }

    FileDialog {
        // Input for dictionary file.
        id: fileDialog
        title: "Please choose a file"
        defaultSuffix: "xdf"
        fileMode: FileDialog.OpenFile
        nameFilters: ["Dictionary files (*.xdf)"]
        onAccepted: {
            selectionPage.connectionController.select_dictionary(selectedFile);
        }
    }

    FileDialog {
        // Input for config file (left drive).
        id: configfileLeftDialog
        title: "Please choose a file"
        defaultSuffix: "lfu"
        fileMode: FileDialog.OpenFile
        nameFilters: ["XCF Files (*.xcf)"]
        onAccepted: {
            selectionPage.connectionController.select_config(selectedFile, Enums.Drive.Left);
        }
    }

    FileDialog {
        // Input for config file (right drive).
        id: configfileRightDialog
        title: "Please choose a file"
        defaultSuffix: "lfu"
        fileMode: FileDialog.OpenFile
        nameFilters: ["XCF Files (*.xcf)"]
        onAccepted: {
            selectionPage.connectionController.select_config(selectedFile, Enums.Drive.Right);
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
            selectionPage.connectionController.select_connection(currentValue);
            selectCANdevice.visible = currentValue == Enums.ConnectionProtocol.CANopen;
            selectBaudrate.visible = currentValue == Enums.ConnectionProtocol.CANopen;
            selectNetworkAdapter.visible = currentValue == Enums.ConnectionProtocol.EtherCAT;
            idLeftAutomatic.model = [];
            idRightAutomatic.model = [];
            idLeftAutomatic.enabled = false;
            idRightAutomatic.enabled = false;
            selectionPage.connectionController.reset_dictionary();
            resetDictionary.visible = false;
            dictionaryButton.enabled = true;
        }
    }

    Components.Selection {
        id: selectNetworkAdapter
        text: "Select network adapter:"
        model: []
        visible: false
        Component.onCompleted: () => {
            const interface_name_list = selectionPage.connectionController.get_interface_name_list();
            selectNetworkAdapter.model = interface_name_list.map((interface_name, index) => {
                    return {
                        value: index,
                        text: interface_name
                    };
                });
        }
        activatedHandler: currentValue => selectionPage.connectionController.select_interface(currentValue)
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
        activatedHandler: currentValue => selectionPage.connectionController.select_can_device(currentValue)
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
        activatedHandler: currentValue => selectionPage.connectionController.select_can_baudrate(currentValue)
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
                selectionPage.connectionController.scan_servos();
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
            onValueModified: () => selectionPage.connectionController.select_node_id(value, Enums.Drive.Left)
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
            onValueModified: () => selectionPage.connectionController.select_node_id(value, Enums.Drive.Right)
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
            onActivated: () => selectionPage.connectionController.select_node_id(currentValue, Enums.Drive.Left)
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
            onActivated: () => selectionPage.connectionController.select_node_id(currentValue, Enums.Drive.Right)
        }
        Components.SpacerW {
        }
    }

    RowLayout {
        // Button for config file upload & display of currently selected file,
        // as well as a button to clear the config file.
        Components.SpacerW {
        }
        ColumnLayout {
            Layout.fillWidth: true
            Layout.preferredWidth: 2
            
            Components.Button {
                id: configButtonLeft
                text: "(Optional) Choose config left..."
                onClicked: configfileLeftDialog.open()
            }
            RowLayout {
                Layout.alignment: Qt.AlignHCenter
                Text {
                    id: configFileLeft
                    color: '#e0e0e0'
                }
                RoundButton {
                    id: resetConfigLeft
                    text: "X"
                    visible: false
                    onClicked: () => {
                        selectionPage.connectionController.reset_config(Enums.Drive.Left);
                        resetConfigLeft.visible = false;
                        configButtonLeft.enabled = true;
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
                id: configButtonRight
                text: "(Optional) Choose config right..."
                onClicked: configfileRightDialog.open()
            }
            RowLayout {
                Layout.alignment: Qt.AlignHCenter
                Text {
                    id: configFileRight
                    color: '#e0e0e0'
                }
                RoundButton {
                    id: resetConfigRight
                    text: "X"
                    visible: false
                    onClicked: () => {
                        selectionPage.connectionController.reset_config(Enums.Drive.Right);
                        resetConfigRight.visible = false;
                        configButtonRight.enabled = true;
                    }
                }
            }
        }
        Components.SpacerW {
        }
    }

    RowLayout {
        // Button for dictionary file upload & display of currently selected file.
        Components.SpacerW {
        }
        ColumnLayout {
            Layout.fillWidth: true
            Layout.preferredWidth: 2
            Components.Button {
                id: dictionaryButton
                text: "Choose dictionary file..."
                onClicked: fileDialog.open()
            }
            RowLayout {
                Layout.alignment: Qt.AlignHCenter
                Text {
                    id: dictionaryFile
                    color: '#e0e0e0'
                    Layout.alignment: Qt.AlignHCenter
                }
                RoundButton {
                    id: resetDictionary
                    text: "X"
                    visible: false
                    onClicked: () => {
                        selectionPage.connectionController.reset_dictionary();
                        resetDictionary.visible = false;
                        dictionaryButton.enabled = true;
                    }
                }
            }
        }
        Components.SpacerW {
        }
    }


    RowLayout {
        Components.SpacerW {
        }
        Components.Button {
            id: connectBtn
            text: "Connect"
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
                        target: connectBtn
                        enabled: true
                    }
                },
                State {
                    name: Enums.ButtonState.Disabled
                    PropertyChanges {
                        target: connectBtn
                        enabled: false
                    }
                }
            ]
            onClicked: () => {
                connectBtn.state = Enums.ButtonState.Disabled;
                selectionPage.connectionController.connect();
            }
        }
        Components.SpacerW {
        }
    }
}
