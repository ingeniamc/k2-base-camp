import os
import sys
from pathlib import Path

import ingenialogger
from PySide6.QtCore import QPointF, Qt
from PySide6.QtQml import QQmlApplicationEngine
from PySide6.QtQuick import QQuickItem
from pytest_mock import MockerFixture
from pytestqt.qtbot import QtBot

from k2basecamp.controllers.bootloader_controller import BootloaderController
from k2basecamp.controllers.drive_controller import DriveController
from k2basecamp.services.motion_controller_service import MotionControllerService


def test_emergency_button(qtbot: QtBot, mocker: MockerFixture) -> None:
    """Start the UI and press the emergency button. Confirm that the expected signal is
    emitted.

    Args:
        qtbot: see https://pytest-qt.readthedocs.io/en/latest/reference.html
        mocker: Used to spy on a signal
    """
    ingenialogger.configure_logger(level=ingenialogger.LoggingLevel.DEBUG)

    engine = QQmlApplicationEngine()
    qml_file = os.fspath(
        Path(__file__).resolve().parent.parent.parent / "k2basecamp/views/main.qml"
    )

    mcs = MotionControllerService()
    drive_controller = DriveController(mcs)
    bootloaderController = BootloaderController(mcs)

    spy = mocker.spy(DriveController, "emergency_stop")

    engine.setInitialProperties(
        {
            "driveController": drive_controller,
            "bootloaderController": bootloaderController,
        }
    )
    engine.load(qml_file)
    if not engine.rootObjects():
        sys.exit(-1)

    root_object = engine.rootObjects()[0]
    root_item = root_object.contentItem()  # type: ignore

    mybtn: QQuickItem = root_object.findChild(QQuickItem, "emergencyStopBtn")  # type: ignore
    assert mybtn is not None
    center = QPointF(mybtn.width(), mybtn.height()) / 2  # type: ignore
    qtbot.mouseClick(
        mybtn.window(),
        Qt.MouseButton.LeftButton,
        pos=root_item.mapFromItem(mybtn, center).toPoint(),
    )
    qtbot.wait(10)
    assert spy.call_count == 1

    drive_controller.mcs.stop_motion_controller_thread()
