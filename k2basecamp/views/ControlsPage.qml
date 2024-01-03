pragma ComponentBehavior: Bound
import QtQuick.Layouts
import QtQuick 2.15
import QtQuick.Controls 2.15
import QtQuick.Controls.Material
import "components"
import qmltypes.controllers 1.0
import QtCharts 2.6
import "js/plot.js" as PlotJS
import "js/controls.js" as ControlsJS

// QEnum() does not seem to work properly with qmllint,
// which is why we disable this warning for this file.
// This only applies to the usage of Enums, if that is
// no longer used, the warning can be re-enabled.
// qmllint disable missing-property

RowLayout {
    id: grid
    signal cancelButtonPressed
    required property ConnectionController connectionController

    Connections {
        target: grid.connectionController
        function onVelocity_left_changed(timestamp, velocity) {
            PlotJS.updatePlot(chartL, timestamp, velocity);
        }
        function onVelocity_right_changed(timestamp, velocity) {
            PlotJS.updatePlot(chartR, timestamp, velocity);
        }
        function onDrive_connected_triggered() {
            PlotJS.initSeries(chartL, xAxisL, yAxisL, "Left");
            PlotJS.initSeries(chartR, xAxisR, yAxisR, "Right");
        }
        function onDrive_disconnected_triggered() {
            leftCheck.checked = false;
            rightCheck.checked = false;
            PlotJS.resetPlot(chartL);
            PlotJS.resetPlot(chartR);
        }
    }

    // Bind velocity controls to the arrow keys on the keyboard.

    Keys.onUpPressed: event => ControlsJS.handleButtonPressed(upButton, -1, 1, event)

    Keys.onDownPressed: event => ControlsJS.handleButtonPressed(downButton, 1, -1, event)

    Keys.onLeftPressed: event => ControlsJS.handleButtonPressed(leftButton, 1, 1, event)

    Keys.onRightPressed: event => ControlsJS.handleButtonPressed(rightButton, -1, -1, event)

    Keys.onReleased: event => {
        if (event.isAutoRepeat)
            return;
        switch (event.key) {
        case Qt.Key_Up:
            ControlsJS.handleButtonReleased(upButton);
            break;
        case Qt.Key_Down:
            ControlsJS.handleButtonReleased(downButton);
            break;
        case Qt.Key_Left:
            ControlsJS.handleButtonReleased(leftButton);
            break;
        case Qt.Key_Right:
            ControlsJS.handleButtonReleased(rightButton);
            break;
        }
    }

    ColumnLayout {
        RowLayout {
            // Checkboxes to enable / disable motors.
            Layout.fillHeight: true

            SpacerW {
            }
            CheckBox {
                id: leftCheck
                text: qsTr("Left")
                onToggled: () => {
                    PlotJS.resetPlot(chartL);
                    PlotJS.initSeries(chartL, xAxisL, yAxisL, "Left");
                    if (leftCheck.checked) {
                        grid.connectionController.enable_motor(Enums.Drive.Left);
                    } else {
                        grid.connectionController.disable_motor(Enums.Drive.Left);
                    }
                    ControlsJS.updateKeyState();
                }
            }
            CheckBox {
                id: rightCheck
                text: qsTr("Right")
                onToggled: () => {
                    PlotJS.resetPlot(chartR);
                    PlotJS.initSeries(chartR, xAxisR, yAxisR, "Right");
                    if (rightCheck.checked) {
                        grid.connectionController.enable_motor(Enums.Drive.Right);
                    } else {
                        grid.connectionController.disable_motor(Enums.Drive.Right);
                    }
                    ControlsJS.updateKeyState();
                }
            }
            SpacerW {
            }
        }
        RowLayout {
            // Graphs to display motor velocities over time. 
            Layout.fillHeight: true

            Rectangle {
                Layout.fillWidth: true
                Layout.fillHeight: true
                Layout.preferredHeight: 2
                color: "transparent"
                ChartView {
                    id: chartL
                    anchors.fill: parent
                    backgroundColor: "#000000"
                    axes: [
                        ValueAxis {
                            id: xAxisL
                            min: 1.0
                            max: 20.0
                        },
                        ValueAxis {
                            id: yAxisL
                            min: -7.5
                            max: 7.5
                        }
                    ]
                }
            }
            Rectangle {
                Layout.fillWidth: true
                Layout.fillHeight: true
                Layout.preferredHeight: 2
                color: "transparent"
                ChartView {
                    id: chartR
                    anchors.fill: parent
                    backgroundColor: "#000000"
                    axes: [
                        ValueAxis {
                            id: xAxisR
                            min: 1.0
                            max: 20.0
                        },
                        ValueAxis {
                            id: yAxisR
                            min: -7.5
                            max: 7.5
                        }
                    ]
                }
            }
        }

        GridLayout {
            /** Buttons to control velocities. 
             * The arrow key buttons are bound to click events.
             * Sliders to control the target velocities.
             * Inputs to control the maximum velocities.
             */
            Layout.fillHeight: true
            Layout.preferredHeight: 1
            rows: 4
            columns: 5
            rowSpacing: 0
            Item {
                Layout.fillHeight: true
                Layout.columnSpan: 5
            }
            SpacerW {
            }
            StateButton {
                id: upButton
                text: "↑"
                Layout.alignment: Qt.AlignBottom
                leftFactor: -1
                rightFactor: 1
            }
            SpacerW {
            }
            ColumnLayout {
                RowLayout {
                    Text {
                        color: "#e0e0e0"
                        text: "Maximum Velocity L"
                    }
                }
                SpinBox {
                    from: 0
                    value: 10
                    editable: true
                    onValueModified: () => {
                        grid.connectionController.set_register_max_velocity(value, Enums.Drive.Left);
                    }
                }
            }
            ColumnLayout {
                RowLayout {
                    Text {
                        color: "#e0e0e0"
                        text: "Target Velocity L -"
                    }
                    Text {
                        id: velocitySliderLValue
                        text: "5.00"
                        color: "#e0e0e0"
                    }
                }
                Slider {
                    id: velocitySliderL
                    from: 1
                    to: 10
                    value: 5
                    onMoved: () => {
                        PlotJS.setMaxVelocity(chartL, velocitySliderL.value);
                        velocitySliderLValue.text = velocitySliderL.value.toFixed(2);
                    }
                }
            }

            StateButton {
                id: leftButton
                text: "←"
                Layout.alignment: Qt.AlignRight | Qt.AlignTop
                leftFactor: 1
                rightFactor: 1
            }
            StateButton {
                id: downButton
                text: "↓"
                Layout.alignment: Qt.AlignTop
                leftFactor: 1
                rightFactor: -1
            }
            StateButton {
                id: rightButton
                text: "→"
                Layout.alignment: Qt.AlignLeft | Qt.AlignTop
                leftFactor: -1
                rightFactor: -1
            }
            ColumnLayout {
                RowLayout {
                    Text {
                        color: "#e0e0e0"
                        text: "Maximum Velocity R"
                    }
                }
                SpinBox {
                    from: 0
                    value: 10
                    editable: true
                    onValueModified: () => {
                        grid.connectionController.set_register_max_velocity(value, Enums.Drive.Right);
                    }
                }
            }

            ColumnLayout {
                RowLayout {
                    Text {
                        color: "#e0e0e0"
                        text: "Target Velocity R -"
                    }
                    Text {
                        id: velocitySliderRValue
                        text: "5.00"
                        color: "#e0e0e0"
                    }
                }
                Slider {
                    id: velocitySliderR
                    from: 1
                    to: 10
                    value: 5
                    onMoved: () => {
                        PlotJS.setMaxVelocity(chartR, velocitySliderR.value);
                        velocitySliderRValue.text = velocitySliderR.value.toFixed(2);
                    }
                }
            }

            Item {
                Layout.fillHeight: true
                Layout.columnSpan: 5
            }
        }
    }
}
