from ingenialink import CAN_BAUDRATE
from PySide6.QtTest import QSignalSpy

from k2basecamp.controllers.drive_controller import DriveController
from k2basecamp.utils.enums import ButtonState, CanDevice, ConnectionProtocol, Drive

"""Use the various slots (functions) in the DriveController to change the
application state and confirm that it has been changed as expected.
Also confirm that the connect button state has the right state before and after
making all the selections.
"""


def test_select_connection(drive_controller: DriveController) -> None:
    connection = ConnectionProtocol.CANopen
    drive_controller.select_connection(connection.value)
    assert drive_controller.drive_model.connection == connection


def test_select_interface(drive_controller: DriveController) -> None:
    interface = 2
    drive_controller.select_interface(interface)
    assert drive_controller.drive_model.interface_index == interface


def test_select_can_device(drive_controller: DriveController) -> None:
    can_device = CanDevice.KVASER
    drive_controller.select_can_device(can_device.value)
    assert drive_controller.drive_model.can_device == can_device


def test_select_can_baudrate(drive_controller: DriveController) -> None:
    can_baudrate = CAN_BAUDRATE.Baudrate_1M
    drive_controller.select_can_baudrate(can_baudrate.value)
    assert drive_controller.drive_model.can_baudrate == can_baudrate


def test_select_ids(drive_controller: DriveController) -> None:
    left_id = 31
    drive_controller.select_node_id(left_id, Drive.Left.value)
    assert drive_controller.drive_model.left_id == left_id

    right_id = 32
    drive_controller.select_node_id(right_id, Drive.Right.value)
    assert drive_controller.drive_model.right_id == right_id


def test_select_dictionary(drive_controller: DriveController) -> None:
    dict_signal_spy = QSignalSpy(drive_controller.dictionary_changed)

    ethercat_dict = "tests/assets/cap-net-e_eoe_2.4.1.xdf"
    drive_controller.select_dictionary(ethercat_dict)
    assert drive_controller.drive_model.dictionary == ethercat_dict
    assert drive_controller.drive_model.dictionary_type == ConnectionProtocol.EtherCAT
    assert dict_signal_spy.at(dict_signal_spy.size() - 1)[
        0
    ] == ethercat_dict.removeprefix("tests/assets/")

    canopen_dict = "tests/assets/eve-xcr-c_can_2.4.1.xdf"
    drive_controller.select_dictionary(canopen_dict)
    assert drive_controller.drive_model.dictionary == canopen_dict
    assert drive_controller.drive_model.dictionary_type == ConnectionProtocol.CANopen  # type: ignore
    assert dict_signal_spy.at(dict_signal_spy.size() - 1)[
        0
    ] == canopen_dict.removeprefix("tests/assets/")


def test_connect_button(drive_controller: DriveController) -> None:
    connect_button_spy = QSignalSpy(drive_controller.connect_button_state_changed)
    drive_controller.select_connection(ConnectionProtocol.CANopen.value)
    drive_controller.select_interface(2)
    drive_controller.select_can_device(CanDevice.KVASER.value)
    drive_controller.select_can_baudrate(CAN_BAUDRATE.Baudrate_1M.value)
    drive_controller.select_node_id(31, Drive.Left.value)
    drive_controller.select_node_id(32, Drive.Right.value)
    # The button should be disabled until everything is seleced.
    assert (
        connect_button_spy.at(connect_button_spy.size() - 1)[0]
        == ButtonState.Disabled.value
    )
    canopen_dict = "tests/assets/eve-xcr-c_can_2.4.1.xdf"
    drive_controller.select_dictionary(canopen_dict)
    # Now that everything is selected, the button should be enabled.
    assert (
        connect_button_spy.at(connect_button_spy.size() - 1)[0]
        == ButtonState.Enabled.value
    )
    # The button state was checked every time something was selected in the controller.
    assert connect_button_spy.count() == 7
