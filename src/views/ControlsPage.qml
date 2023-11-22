pragma ComponentBehavior: Bound
import QtQuick.Layouts
import QtQuick 2.15
import QtQuick.Controls 2.15
import QtQuick.Controls.Material
import "components"
import qmltypes.controllers 1.0
import QtCharts 2.6
import "js/plot.js" as PlotJS

// QEnum() does not seem to work properly with qmllint,
// which is why we disable this warning for this file.
// This only applies to the usage of Enums, if that is
// no longer used, the warning can be re-enabled.
// qmllint disable missing-property

RowLayout {
    id: grid
    signal cancelButtonPressed
    required property DriveController driveController

    Connections {
        target: grid.driveController
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
    Keys.onUpPressed: event => {
        if (event.isAutoRepeat)
            return;
        upButton.state = "ACTIVE";
        if (leftCheck.checked) {
            grid.driveController.set_velocity(velocitySliderL.value, Enums.Drive.Left);
        }
        if (rightCheck.checked) {
            grid.driveController.set_velocity(velocitySliderR.value, Enums.Drive.Right);
        }
    }

    Keys.onDownPressed: event => {
        if (event.isAutoRepeat)
            return;
        downButton.state = "ACTIVE";
        if (leftCheck.checked) {
            grid.driveController.set_velocity(velocitySliderL.value * -1, Enums.Drive.Left);
        }
        if (rightCheck.checked) {
            grid.driveController.set_velocity(velocitySliderR.value * -1, Enums.Drive.Right);
        }
    }

    Keys.onLeftPressed: event => {
        if (event.isAutoRepeat || !rightCheck.checked || !leftCheck.checked)
            return;
        leftButton.state = "ACTIVE";
        grid.driveController.set_velocity(velocitySliderL.value * -1, Enums.Drive.Left);
        grid.driveController.set_velocity(velocitySliderR.value, Enums.Drive.Right);
    }

    Keys.onRightPressed: event => {
        if (event.isAutoRepeat || !rightCheck.checked || !leftCheck.checked)
            return;
        rightButton.state = "ACTIVE";
        grid.driveController.set_velocity(velocitySliderL.value, Enums.Drive.Left);
        grid.driveController.set_velocity(velocitySliderR.value * -1, Enums.Drive.Right);
    }

    Keys.onReleased: event => {
        if (event.isAutoRepeat)
            return;
        switch (event.key) {
        case Qt.Key_Up:
            upButton.state = "NORMAL";
            break;
        case Qt.Key_Down:
            downButton.state = "NORMAL";
            break;
        case Qt.Key_Left:
            leftButton.state = "NORMAL";
            break;
        case Qt.Key_Right:
            rightButton.state = "NORMAL";
            break;
        }
        if (leftCheck.checked) {
            grid.driveController.set_velocity(0, Enums.Drive.Left);
        }
        if (rightCheck.checked) {
            grid.driveController.set_velocity(0, Enums.Drive.Right);
        }
    }

    ColumnLayout {
        RowLayout {
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
                        grid.driveController.enable_motor(Enums.Drive.Left);
                    } else {
                        grid.driveController.disable_motor(Enums.Drive.Left);
                    }
                }
            }
            CheckBox {
                id: rightCheck
                text: qsTr("Right")
                onToggled: () => {
                    PlotJS.resetPlot(chartR);
                    PlotJS.initSeries(chartR, xAxisR, yAxisR, "Right");
                    if (rightCheck.checked) {
                        grid.driveController.enable_motor(Enums.Drive.Right);
                    } else {
                        grid.driveController.disable_motor(Enums.Drive.Right);
                    }
                }
            }
            SpacerW {
            }
        }
        RowLayout {
            Layout.fillHeight: true

            Rectangle {
                Layout.fillWidth: true
                Layout.fillHeight: true
                Layout.preferredHeight: 2
                ChartView {
                    id: chartL
                    anchors.fill: parent
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
                ChartView {
                    id: chartR
                    anchors.fill: parent
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
            Layout.fillHeight: true
            Layout.preferredHeight: 1
            rows: 2
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
            }
            SpacerW {
            }
            ColumnLayout {
                RowLayout {
                    Text {
                        color: "black"
                        text: "Max Velocity L -"
                    }
                    Text {
                        id: velocitySliderLValue
                        text: "5.00"
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
            SpacerW {
            }

            StateButton {
                id: leftButton
                text: "←"
                Layout.alignment: Qt.AlignRight | Qt.AlignTop
            }
            StateButton {
                id: downButton
                text: "↓"
                Layout.alignment: Qt.AlignTop
            }
            StateButton {
                id: rightButton
                text: "→"
                Layout.alignment: Qt.AlignLeft | Qt.AlignTop
            }
            ColumnLayout {
                RowLayout {
                    Text {
                        color: "black"
                        text: "Max Velocity R -"
                    }
                    Text {
                        id: velocitySliderRValue
                        text: "5.00"
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
            SpacerW {
            }

            Item {
                Layout.fillHeight: true
                Layout.columnSpan: 5
            }
        }
    }
}