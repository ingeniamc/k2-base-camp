from typing import Union

from k2basecamp.models.base_model import BaseModel
from k2basecamp.utils.enums import ButtonState, ConnectionProtocol


class BootloaderModel(BaseModel):
    """Holds the state of the application.
    Is created and manipulated by the ConnectionController.
    """

    def __init__(
        self,
        left_firmware: Union[str, None] = None,
        right_firmware: Union[str, None] = None,
    ) -> None:
        super().__init__()
        self.left_firmware = left_firmware
        self.right_firmware = right_firmware

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
