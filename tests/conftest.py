from typing import Generator

import pytest

from k2basecamp.controllers.drive_controller import DriveController
from k2basecamp.services.motion_controller_service import MotionControllerService


@pytest.fixture
def drive_controller() -> Generator[DriveController, None, None]:
    """Fixture to create an instance of DriveController

    Returns:
        DriveController: the DriveController
    """
    mcs = MotionControllerService()
    drive_controller = DriveController(mcs)
    yield drive_controller
    drive_controller.mcs.stop_motion_controller_thread()
