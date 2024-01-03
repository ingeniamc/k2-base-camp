from ingenialink import CAN_BAUDRATE
from PySide6.QtTest import QSignalSpy

from k2basecamp.controllers.connection_controller import ConnectionController
from k2basecamp.utils.enums import ButtonState, CanDevice, ConnectionProtocol, Drive

"""Use the various slots (functions) in the ConnectionController to change the
application state and confirm that it has been changed as expected.
Also confirm that the connect button state has the right state before and after
making all the selections.
"""


def test_select_connection(connection_controller: ConnectionController) -> None:
    connection = ConnectionProtocol.CANopen
    connection_controller.select_connection(connection.value)
    assert connection_controller.connection_model.connection == connection


def test_select_interface(connection_controller: ConnectionController) -> None:
    interface = 2
    connection_controller.select_interface(interface)
    assert connection_controller.connection_model.interface_index == interface


def test_select_can_device(connection_controller: ConnectionController) -> None:
    can_device = CanDevice.KVASER
    connection_controller.select_can_device(can_device.value)
    assert connection_controller.connection_model.can_device == can_device


def test_select_can_baudrate(connection_controller: ConnectionController) -> None:
    can_baudrate = CAN_BAUDRATE.Baudrate_1M
    connection_controller.select_can_baudrate(can_baudrate.value)
    assert connection_controller.connection_model.can_baudrate == can_baudrate


def test_select_ids(connection_controller: ConnectionController) -> None:
    left_id = 31
    connection_controller.select_node_id(left_id, Drive.Left.value)
    assert connection_controller.connection_model.left_id == left_id

    right_id = 32
    connection_controller.select_node_id(right_id, Drive.Right.value)
    assert connection_controller.connection_model.right_id == right_id


def test_select_dictionary(connection_controller: ConnectionController) -> None:
    dict_signal_spy = QSignalSpy(connection_controller.dictionary_changed)

    ethercat_dict = "tests/assets/cap-net-e_eoe_2.4.1.xdf"
    connection_controller.select_dictionary(ethercat_dict)
    assert connection_controller.connection_model.dictionary == ethercat_dict
    assert (
        connection_controller.connection_model.dictionary_type
        == ConnectionProtocol.EtherCAT
    )
    assert dict_signal_spy.at(dict_signal_spy.size() - 1)[
        0
    ] == ethercat_dict.removeprefix("tests/assets/")

    canopen_dict = "tests/assets/eve-xcr-c_can_2.4.1.xdf"
    connection_controller.select_dictionary(canopen_dict)
    assert connection_controller.connection_model.dictionary == canopen_dict
    assert (
        connection_controller.connection_model.dictionary_type
        == ConnectionProtocol.CANopen  # type: ignore
    )
    assert dict_signal_spy.at(dict_signal_spy.size() - 1)[
        0
    ] == canopen_dict.removeprefix("tests/assets/")


def test_connect_button(connection_controller: ConnectionController) -> None:
    connect_button_spy = QSignalSpy(connection_controller.connect_button_state_changed)
    connection_controller.select_connection(ConnectionProtocol.CANopen.value)
    connection_controller.select_interface(2)
    connection_controller.select_can_device(CanDevice.KVASER.value)
    connection_controller.select_can_baudrate(CAN_BAUDRATE.Baudrate_1M.value)
    connection_controller.select_node_id(31, Drive.Left.value)
    connection_controller.select_node_id(32, Drive.Right.value)
    # The button should be disabled until everything is seleced.
    assert (
        connect_button_spy.at(connect_button_spy.size() - 1)[0]
        == ButtonState.Disabled.value
    )
    canopen_dict = "tests/assets/eve-xcr-c_can_2.4.1.xdf"
    connection_controller.select_dictionary(canopen_dict)
    # Now that everything is selected, the button should be enabled.
    assert (
        connect_button_spy.at(connect_button_spy.size() - 1)[0]
        == ButtonState.Enabled.value
    )
    # The button state was checked every time something was selected in the controller.
    assert connect_button_spy.count() == 7
