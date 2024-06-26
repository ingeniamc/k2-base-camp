from typing import Union

from k2basecamp.models.base_model import BaseModel
from k2basecamp.utils.enums import ButtonState, ConnectionProtocol


class ConnectionModel(BaseModel):
    """Holds the state of the application.
    Is created and manipulated by the ConnectionController.
    """

    def __init__(
        self,
        left_dictionary: Union[str, None] = None,
        left_dictionary_type: Union[ConnectionProtocol, None] = None,
        right_dictionary: Union[str, None] = None,
        right_dictionary_type: Union[ConnectionProtocol, None] = None,
        left_config: Union[str, None] = None,
        right_config: Union[str, None] = None,
    ) -> None:
        super().__init__()
        self.left_dictionary = left_dictionary
        self.left_dictionary_type = left_dictionary_type
        self.right_dictionary = right_dictionary
        self.right_dictionary_type = right_dictionary_type
        self.left_config = left_config
        self.right_config = right_config

    def connect_button_state(self) -> ButtonState:
        """Calculate the state the "Connect"-button should be in based on the
        application state.

        Returns:
            utils.enums.ButtonState: the button state.
        """
        if (
            self.left_dictionary is None
            or self.left_dictionary_type is None
            or self.connection != self.left_dictionary_type
            or self.right_dictionary is None
            or self.right_dictionary_type is None
            or self.connection != self.right_dictionary_type
            or self.left_id is None
            or self.right_id is None
            or self.left_id == self.right_id
            or (
                self.connection == ConnectionProtocol.CANopen
                and (self.can_device is None or self.can_baudrate is None)
            )
            or (
                self.connection == ConnectionProtocol.EtherCAT
                and (self.interface is None)
            )
        ):
            return ButtonState.Disabled
        return ButtonState.Enabled
