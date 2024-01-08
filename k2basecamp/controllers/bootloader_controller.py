import os
from typing import Union

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

    firmware_left_installation_progress_changed = Signal(int, arguments=["progress"])
    """During installation, information about the progress of the operation is emitted.

    Args:
        progress (int): The progress as a percentage.
    """

    firmware_right_installation_progress_changed = Signal(int, arguments=["progress"])
    """During installation, information about the progress of the operation is emitted.

    Args:
        progress (int): The progress as a percentage.
    """

    firmware_installation_started = Signal(QJsonArray, arguments=["drives"])
    """Triggers when the installation of firmware begins.

    Args:
        drives (PySide6.QtCore.QJsonArray): The drives to be updated.
    """

    def __init__(self, mcs: MotionControllerService) -> None:
        super().__init__()
        self.mcs = mcs
        self.mcs.error_triggered.connect(self.error_message_callback)
        self.bootloader_model = BootloaderModel()
        self.drives_in_progress: list[int] = []
        self.errors: list[str] = []

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
            self.scan_servos_callback, self.bootloader_model, minimum_nodes=1
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
            self.bootloader_model.left_firmware = firmware_path
        else:
            self.bootloader_model.right_firmware = firmware_path
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
            self.bootloader_model.left_firmware = None
        else:
            self.bootloader_model.right_firmware = None
        self.firmware_changed.emit("", drive)
        self.update_install_button_state()

    @Slot()
    def install_firmware(self) -> None:
        """Install the firmwares that are saved in the DriveModel to the drives.
        If the user didn't provide a file for a drive, no changes will be made to that
        drive.
        If the installation process provides a progress report, it will be handled by
        the install_firmware_progress_callback - function.
        Depending on the connection protocol, the installation has to be done
        sequentially (one drive after the other) or can be done in parallel.
        """
        if self.bootloader_model.connection == ConnectionProtocol.EtherCAT:
            self.install_firmware_sequential()
        elif self.bootloader_model.connection == ConnectionProtocol.CANopen:
            self.install_firmware_parallel()
        else:
            return
        self.firmware_installation_started.emit(
            QJsonArray.fromVariantList(self.drives_in_progress)
        )

    def install_firmware_sequential(self) -> None:
        """Install firmware to the drives, one after the other."""
        if self.bootloader_model.left_firmware and self.bootloader_model.left_id:
            self.drives_in_progress.append(Drive.Left.value)
            self.mcs.install_firmware_sequential(
                self.install_firmware_callback,
                self.firmware_left_installation_progress_changed,
                Drive.Left,
                self.bootloader_model,
                self.bootloader_model.left_firmware,
                self.bootloader_model.left_id,
            )
        if self.bootloader_model.right_firmware and self.bootloader_model.right_id:
            self.drives_in_progress.append(Drive.Right.value)
            self.mcs.install_firmware_sequential(
                self.install_firmware_callback,
                self.firmware_right_installation_progress_changed,
                Drive.Right,
                self.bootloader_model,
                self.bootloader_model.right_firmware,
                self.bootloader_model.right_id,
            )

    def install_firmware_parallel(self) -> None:
        """Install firmware to the drives in parallel.
        Spawns a thread for each drive."""
        if self.bootloader_model.left_firmware and self.bootloader_model.left_id:
            self.drives_in_progress.append(Drive.Left.value)
            self.bootloader_thread_left = self.mcs.create_bootloader_thread(
                bootloader_model=self.bootloader_model,
                drive=Drive.Left,
                firmware=self.bootloader_model.left_firmware,
                id=self.bootloader_model.left_id,
            )
            self.bootloader_thread_left.firmware_installation_progress_changed.connect(
                self.firmware_left_installation_progress_changed
            )
            self.bootloader_thread_left.firmware_installation_complete_triggered.connect(
                self.install_firmware_callback
            )
            self.bootloader_thread_left.error_triggered.connect(
                self.error_message_callback
            )
            self.bootloader_thread_left.start()
        if self.bootloader_model.right_firmware and self.bootloader_model.right_id:
            self.drives_in_progress.append(Drive.Right.value)
            self.bootloader_thread_right = self.mcs.create_bootloader_thread(
                bootloader_model=self.bootloader_model,
                drive=Drive.Right,
                firmware=self.bootloader_model.right_firmware,
                id=self.bootloader_model.right_id,
            )
            self.bootloader_thread_right.firmware_installation_progress_changed.connect(
                self.firmware_right_installation_progress_changed
            )
            self.bootloader_thread_right.firmware_installation_complete_triggered.connect(
                self.install_firmware_callback
            )
            self.bootloader_thread_right.error_triggered.connect(
                self.error_message_callback
            )
            self.bootloader_thread_right.start()

    @Slot(int)
    def select_connection(self, connection: int) -> None:
        """Update the DriveModel, setting the connection property to the value that was
        selected in the UI.

        Args:
            connection: the selected connection.
        """
        self.bootloader_model.connection = ConnectionProtocol(connection)
        self.update_install_button_state()

    @Slot(int)
    def select_interface(self, interface: int) -> None:
        """Update the DriveModel, setting the interface property to the value that was
        selected in the UI.

        Args:
            interface: the selected interface.
        """
        self.bootloader_model.interface_index = interface
        self.update_install_button_state()

    @Slot(int)
    def select_can_device(self, can_device: int) -> None:
        """Update the DriveModel, setting the can device property to the value that was
        selected in the UI.

        Args:
            can_device: the selected can device.
        """
        self.bootloader_model.can_device = CanDevice(can_device)
        self.update_install_button_state()

    @Slot(int)
    def select_can_baudrate(self, baudrate: int) -> None:
        """Update the DriveModel, setting the can baudrate property to the value that
        was selected in the UI.

        Args:
            can_baudrate: the selected can baudrate.
        """
        self.bootloader_model.can_baudrate = CAN_BAUDRATE(baudrate)
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
            self.bootloader_model.left_id = node_id
        else:
            self.bootloader_model.right_id = node_id
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
            self.bootloader_model.left_id = servo_ids[0]
            if len(servo_ids) > 1:
                self.bootloader_model.right_id = servo_ids[1]
            self.servo_ids_changed.emit(QJsonArray.fromVariantList(servo_ids))
            self.update_install_button_state()

    def error_message_callback(self, error_message: str) -> None:
        """Callback when an error occured in a MotionControllerThread.
        Emits a signal to the UI that contains the error message.
        If the installation is still in progress (e.g. when two drives are being updated
        in parallel), the error will be emmitted in the install_firmware_callback
        function instead.

        Args:
            error_message: the error message.
        """
        self.errors.append(error_message)
        if len(self.drives_in_progress) > 0:
            self.drives_in_progress.pop()
        if len(self.drives_in_progress) == 0:
            self.error_triggered.emit("\n".join(self.errors))
            self.errors = []

    @Slot()
    def install_firmware_callback(
        self, thread_report: Union[thread_report, None] = None
    ) -> None:
        """Checks if the installation has completed for both drives. If that's the case,
        emits a signal to notify the GUI that the installation has concluded and - if
        any error ocurred - another signal with all the errors that occurred in the
        process.

        Args:
            thread_report: the result of the operation that triggered
                the callback. Defaults to None.
        """
        self.drives_in_progress.pop()
        if len(self.drives_in_progress) == 0:
            self.firmware_installation_complete_triggered.emit()
            if len(self.errors) > 0:
                self.error_triggered.emit("\n".join(self.errors))
                self.errors = []

    def update_install_button_state(self) -> None:
        """Helper function that calculates the state of the install button using the
        DriveModel and emits a signal to the UI with the resulting state.
        """
        self.install_button_state_changed.emit(
            self.bootloader_model.install_button_state().value
        )
