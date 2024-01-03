from typing import Union

from k2basecamp.models.base_model import BaseModel
from k2basecamp.utils.enums import ButtonState, ConnectionProtocol


class ConnectionModel(BaseModel):
    """Holds the state of the application.
    Is created and manipulated by the ConnectionController.
    """

    def __init__(
        self,
        dictionary: Union[str, None] = None,
        dictionary_type: Union[ConnectionProtocol, None] = None,
        left_config: Union[str, None] = None,
        right_config: Union[str, None] = None,
    ) -> None:
        super().__init__()
        self.dictionary = dictionary
        self.dictionary_type = dictionary_type
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
