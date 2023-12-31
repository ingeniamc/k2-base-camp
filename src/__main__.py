import os
import sys
from pathlib import Path

import ingenialogger

# Needed for styling.
# Created with pyside6-rcc using resources.qrc and qtquickcontrols.conf.
import resources  # noqa: F401
from controllers.bootloader_controller import BootloaderController
from controllers.drive_controller import DriveController
from PySide6.QtGui import QIcon
from PySide6.QtQml import QQmlApplicationEngine
from PySide6.QtQuick import QQuickView
from PySide6.QtWidgets import QApplication
from services.motion_controller_service import MotionControllerService

if __name__ == "__main__":
    # Init the logger util.
    ingenialogger.configure_logger(level=ingenialogger.LoggingLevel.INFO)

    # Create the application.
    app = QApplication(sys.argv)
    app.setWindowIcon(
        QIcon(
            os.fspath(
                Path(__file__).resolve().parent / "assets/novantaMotionFavicon.png"
            )
        )
    )

    # Insert QML Quick view into the application.
    view = QQuickView()
    qml_file = os.fspath(Path(__file__).resolve().parent / "views/main.qml")
    engine = QQmlApplicationEngine()

    # Init the controllers and make them availble to our .qml files.
    mcs = MotionControllerService()
    drive_controller = DriveController(mcs)
    bootloader_controller = BootloaderController(mcs)
    engine.setInitialProperties(
        {
            "bootloaderController": bootloader_controller,
            "driveController": drive_controller,
        }
    )

    engine.load(qml_file)
    if not engine.rootObjects():
        sys.exit(-1)

    # Start the application.
    ret = app.exec()
    drive_controller.mcs.stop_motion_controller_thread()
    sys.exit(ret)
