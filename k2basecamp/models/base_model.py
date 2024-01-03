from typing import Union

from ingenialink import CAN_BAUDRATE
from PySide6.QtCore import QObject

from k2basecamp.utils.enums import CanDevice, ConnectionProtocol


class BaseModel(QObject):
    """Holds the state of the application.
    Is created and manipulated by the ConnectionController.
    """

    def __init__(
        self,
        connection: ConnectionProtocol = ConnectionProtocol.CANopen,
        can_device: CanDevice = CanDevice.KVASER,
        can_baudrate: CAN_BAUDRATE = CAN_BAUDRATE.Baudrate_1M,
        interface_index: int = 0,
        left_id: Union[int, None] = None,
        right_id: Union[int, None] = None,
    ) -> None:
        super().__init__()
        self.connection = connection
        self.can_device = can_device
        self.can_baudrate = can_baudrate
        self.interface_index = interface_index
        self.left_id = left_id
        self.right_id = right_id
