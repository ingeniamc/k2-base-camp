import os

import ingenialogger
from ingenialink import CAN_BAUDRATE
from PySide6.QtCore import QJsonArray, QObject, Signal, Slot
from PySide6.QtQml import QmlElement

from k2basecamp.models.bootloader_model import BootloaderModel
from k2basecamp.services.motion_controller_service import MotionControllerService
from k2basecamp.utils.enums import CanDevice, ConnectionProtocol, Drive
from k2basecamp.utils.types import thread_report

# To be used on the @QmlElement decorator
# (QML_IMPORT_MINOR_VERSION is optional)
QML_IMPORT_NAME = "qmltypes.controllers"
QML_IMPORT_MAJOR_VERSION = 1

logger = ingenialogger.get_logger(__name__)


@QmlElement
class BootloaderController(QObject):
    """A connection between the buisiness logic (BL) and the user interface (UI).
    Emits signals that the UI can respond to (BL -> UI).
    Defines slots that can then be accessed directly in the UI (UI -> BL).
    Creates and updates an instance of DriveModel to store application state.
    Uses an instance of MotionControllerService to connect to and communicate with the
    drives.
    Defines callback functions that are invoked after a task delegated to the
    MotionControllerService was completed.
    """

    firmware_changed = Signal(str, int, arguments=["firmware", "drive"])
    """Triggers when a firmware file was selected.

    Args:
        firmware (str): the path of the selected file.
        drive (int): the drive the file is for.
    """

    error_triggered = Signal(str, arguments=["error_message"])
    """Triggers when an error occurs while communicating with the drive.

    Args:
        error_message (str): the error message.
    """

    install_button_state_changed = Signal(int, arguments=["button_state"])
    """Triggers when the state of the install button changes.

    Args:
        buttons_state (int): the new button state.
    """

    servo_ids_changed = Signal(QJsonArray, arguments=["servo_ids"])
    """Triggers when the scan returned new values for the servo connections.

    Args:
        servo_ids (PySide6.QtCore.QJsonArray): the slave / node IDs identified by the
            scan.
    """

    firmware_installation_complete_triggered = Signal()
    """Triggers when the installation of firmware files was completed successfully."""

    firmware_installation_progress_changed = Signal(int, arguments=["progress"])
    """During installation, information about the progress of the operation is emitted.

    Args:
        progress (int): The progress as a percentage.
    """

    def __init__(self, mcs: MotionControllerService) -> None:
        super().__init__()
        self.mcs = mcs
        self.mcs.error_triggered.connect(self.error_message_callback)
        self.drive_model = BootloaderModel()

    @Slot(result=QJsonArray)
    def get_interface_name_list(self) -> QJsonArray:
        """Get a list of available interfaces from the MotionControllerService.

        Returns:
            QJsonArray: the available interfaces in JSON format.
        """
        return QJsonArray.fromStringList(self.mcs.get_interface_name_list())

    @Slot()
    def scan_servos(self) -> None:
        """Scan for servos in the network."""
        self.mcs.scan_servos(
            self.scan_servos_callback, self.drive_model, minimum_nodes=1
        )

    @Slot(str, int)
    def select_firmware(self, firmware: str, drive: int) -> None:
        """Update the DriveModel, setting the firmware property to the url of the
        file that was uploaded in the UI.

        Args:
            firmware: the url of the firmware file.
            drive: the drive the file belongs to.
        """
        firmware_path = firmware.removeprefix("file:///")
        if drive == Drive.Left.value:
            self.drive_model.left_firmware = firmware_path
        else:
            self.drive_model.right_firmware = firmware_path
        self.firmware_changed.emit(os.path.basename(firmware_path), drive)
        self.update_install_button_state()

    @Slot(int)
    def reset_firmware(self, drive: int) -> None:
        """Resets the firmware file in the DriveModel for a given drive.
        This will prevent the firmware installation button to install anything for this
        drive.

        Args:
            drive: the drive.
        """
        if drive == Drive.Left.value:
            self.drive_model.left_firmware = None
        else:
            self.drive_model.right_firmware = None
        self.firmware_changed.emit("", drive)
        self.update_install_button_state()

    @Slot()
    def install_firmware(self) -> None:
        """Install the firmwares that are saved in the DriveModel to the drives.
        If the user didn't provide a file for a drive, no changes will be made to that
        drive.
        If the installation process provides a progress report, it will be handled by
        the install_firmware_progress_callback - function.
        """
        self.mcs.install_firmware(
            self.install_firmware_callback,
            self.install_firmware_progress_callback,
            self.drive_model,
        )

    def install_firmware_progress_callback(self, progress: int) -> None:
        """During firmware installation information about the progress of the process is
        emitted. This function takes this information and passes it to a signal that can
        be consumed in the UI.

        Args:
            progress: the progress of the installation, as a percentage.
        """
        self.firmware_installation_progress_changed.emit(progress)

    @Slot(int)
    def select_connection(self, connection: int) -> None:
        """Update the DriveModel, setting the connection property to the value that was
        selected in the UI.

        Args:
            connection: the selected connection.
        """
        self.drive_model.connection = ConnectionProtocol(connection)
        self.update_install_button_state()

    @Slot(int)
    def select_interface(self, interface: int) -> None:
        """Update the DriveModel, setting the interface property to the value that was
        selected in the UI.

        Args:
            interface: the selected interface.
        """
        self.drive_model.interface_index = interface
        self.update_install_button_state()

    @Slot(int)
    def select_can_device(self, can_device: int) -> None:
        """Update the DriveModel, setting the can device property to the value that was
        selected in the UI.

        Args:
            can_device: the selected can device.
        """
        self.drive_model.can_device = CanDevice(can_device)
        self.update_install_button_state()

    @Slot(int)
    def select_can_baudrate(self, baudrate: int) -> None:
        """Update the DriveModel, setting the can baudrate property to the value that
        was selected in the UI.

        Args:
            can_baudrate: the selected can baudrate.
        """
        self.drive_model.can_baudrate = CAN_BAUDRATE(baudrate)
        self.update_install_button_state()

    @Slot(int, int)
    def select_node_id(self, node_id: int, drive: int) -> None:
        """Update the DriveModel, setting the can node / slave ID property to the value
        that was selected in the UI (which property is set depends on the drive).

        Args:
            node_id: the selected node / slave ID.
            drive: the drive the ID belongs to.
        """
        if drive == Drive.Left.value:
            self.drive_model.left_id = node_id
        else:
            self.drive_model.right_id = node_id
        self.update_install_button_state()

    def scan_servos_callback(self, thread_report: thread_report) -> None:
        """Callback after the scan operation was completed. If values where returned,
        updates the DriveModel state and emits a signal to the UI.

        Args:
            thread_report: the result of the operation that triggered
                the callback.
        """
        if thread_report.output is not None:
            servo_ids: list[int] = thread_report.output
            self.drive_model.left_id = servo_ids[0]
            if len(servo_ids) > 1:
                self.drive_model.right_id = servo_ids[1]
            self.servo_ids_changed.emit(QJsonArray.fromVariantList(servo_ids))
            self.update_install_button_state()

    def error_message_callback(self, error_message: str) -> None:
        """Callback when an error occured in a MotionControllerThread.
        Emits a signal to the UI that contains the error message.

        Args:
            error_message: the error message.
        """
        self.error_triggered.emit(error_message)

    def install_firmware_callback(self, thread_report: thread_report) -> None:
        """Callback when firmware was installed successfully to one or more drives.

        Args:
            thread_report: the result of the operation that triggered
                the callback.
        """
        self.firmware_installation_complete_triggered.emit()

    def update_install_button_state(self) -> None:
        """Helper function that calculates the state of the install button using the
        DriveModel and emits a signal to the UI with the resulting state.
        """
        self.install_button_state_changed.emit(
            self.drive_model.install_button_state().value
        )
