from typing import Generator

import pytest

from k2basecamp.controllers.connection_controller import ConnectionController
from k2basecamp.services.motion_controller_service import MotionControllerService


@pytest.fixture
def connection_controller() -> Generator[ConnectionController, None, None]:
    """Fixture to create an instance of ConnectionController

    Returns:
        ConnectionController: the ConnectionController
    """
    mcs = MotionControllerService()
    connection_controller = ConnectionController(mcs)
    yield connection_controller
    connection_controller.mcs.stop_motion_controller_thread()
