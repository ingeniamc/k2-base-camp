from ingenialink import CAN_BAUDRATE
from PySide6.QtTest import QSignalSpy

from src.controllers.drive_controller import DriveController
from src.enums import ButtonState, CanDevice, Connection, Drive


def test_select(drive_controller: DriveController) -> None:
    connect_button_spy = QSignalSpy(drive_controller.connect_button_state_changed)
    connection = Connection.CANopen
    drive_controller.select_connection(connection.value)
    assert drive_controller.connection == connection

    assert (
        connect_button_spy.at(connect_button_spy.size() - 1)[0]
        == ButtonState.Disabled.value
    )

    interface = 2
    drive_controller.select_interface(interface)
    assert drive_controller.interface_index == interface

    can_device = CanDevice.KVASER
    drive_controller.select_can_device(can_device.value)
    assert drive_controller.can_device == can_device

    can_baudrate = CAN_BAUDRATE.Baudrate_1M
    drive_controller.select_can_baudrate(can_baudrate.value)
    assert drive_controller.baudrate == can_baudrate

    left_id = 31
    drive_controller.select_node_id(left_id, Drive.Left.value)
    assert drive_controller.left_id == left_id

    right_id = 32
    drive_controller.select_node_id(right_id, Drive.Right.value)
    assert drive_controller.right_id == right_id

    dict_signal_spy = QSignalSpy(drive_controller.dictionary_changed)

    ethercat_dict = "tests/assets/cap-net-e_eoe_2.4.1.xdf"
    drive_controller.select_dictionary(ethercat_dict)
    assert drive_controller.dictionary == ethercat_dict
    assert drive_controller.dictionary_type == Connection.EtherCAT
    assert dict_signal_spy.at(dict_signal_spy.size() - 1)[
        0
    ] == ethercat_dict.removeprefix("tests/assets/")

    canopen_dict = "tests/assets/eve-xcr-c_can_2.4.1.xdf"
    drive_controller.select_dictionary(canopen_dict)
    assert drive_controller.dictionary == canopen_dict
    assert drive_controller.dictionary_type == Connection.CANopen  # type: ignore
    assert dict_signal_spy.at(dict_signal_spy.size() - 1)[
        0
    ] == canopen_dict.removeprefix("tests/assets/")
    assert (
        connect_button_spy.at(connect_button_spy.size() - 1)[0]
        == ButtonState.Enabled.value
    )

    assert connect_button_spy.count() == 8