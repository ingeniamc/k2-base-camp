from typing import Union

from ingenialink import CAN_BAUDRATE
from PySide6.QtCore import QObject

from k2basecamp.utils.enums import ButtonState, CanDevice, ConnectionProtocol


class DriveModel(QObject):
    """Holds the state of the application.
    Is created and manipulated by the DriveController.
    """

    def __init__(
        self,
        connection: ConnectionProtocol = ConnectionProtocol.CANopen,
        can_device: CanDevice = CanDevice.KVASER,
        can_baudrate: CAN_BAUDRATE = CAN_BAUDRATE.Baudrate_1M,
        interface_index: int = 0,
        left_id: Union[int, None] = None,
        right_id: Union[int, None] = None,
        dictionary: Union[str, None] = None,
        dictionary_type: Union[ConnectionProtocol, None] = None,
        left_firmware: Union[str, None] = None,
        right_firmware: Union[str, None] = None,
        left_config: Union[str, None] = None,
        right_config: Union[str, None] = None,
    ) -> None:
        super().__init__()
        self.connection = connection
        self.can_device = can_device
        self.can_baudrate = can_baudrate
        self.interface_index = interface_index
        self.left_id = left_id
        self.right_id = right_id
        self.dictionary = dictionary
        self.dictionary_type = dictionary_type
        self.left_firmware = left_firmware
        self.right_firmware = right_firmware
        self.left_config = left_config
        self.right_config = right_config

    def connect_button_state(self) -> ButtonState:
        """Calculate the state the "Connect"-button should be in based on the
        application state.

        Returns:
            utils.enums.ButtonState: the button state.
        """
        if (
            self.dictionary is None
            or self.dictionary_type is None
            or self.connection != self.dictionary_type
            or self.left_id is None
            or self.right_id is None
            or self.left_id == self.right_id
            or (
                self.connection == ConnectionProtocol.CANopen
                and (self.can_device is None or self.can_baudrate is None)
            )
            or (
                self.connection == ConnectionProtocol.EtherCAT
                and (self.interface_index is None)
            )
        ):
            return ButtonState.Disabled
        return ButtonState.Enabled

    def install_prerequisites_met(self) -> bool:
        """Calculate if the application is in the right state to perform the
        "install firmware" - operation.

        Returns:
            bool: true if it is, false if not.
        """
        return (
            (
                (self.left_id is not None and self.left_firmware is not None)
                or (self.right_id is not None and self.right_firmware is not None)
            )
            and self.left_id != self.right_id
            and (
                (
                    self.connection == ConnectionProtocol.CANopen
                    and self.can_baudrate is not None
                    and self.can_device is not None
                )
                or (
                    self.connection == ConnectionProtocol.EtherCAT
                    and self.interface_index is not None
                )
            )
        )

    def install_button_state(self) -> ButtonState:
        """The "install" - button should only be active if the application is in the
        right state to perform the operation.

        Returns:
            utils.enums.ButtonState: the button state.
        """
        if self.install_prerequisites_met():
            return ButtonState.Enabled
        return ButtonState.Disabled
