import os

import ingenialogger
from ingenialink import CAN_BAUDRATE
from PySide6.QtCore import QJsonArray, QObject, Signal, Slot
from PySide6.QtQml import QmlElement

from k2basecamp.models.drive_model import DriveModel
from k2basecamp.services.motion_controller_service import MotionControllerService
from k2basecamp.utils.enums import CanDevice, ConnectionProtocol, Drive
from k2basecamp.utils.types import thread_report

# To be used on the @QmlElement decorator
# (QML_IMPORT_MINOR_VERSION is optional)
QML_IMPORT_NAME = "qmltypes.controllers"
QML_IMPORT_MAJOR_VERSION = 1

logger = ingenialogger.get_logger(__name__)


@QmlElement
class DriveController(QObject):
    """A connection between the buisiness logic (BL) and the user interface (UI).
    Emits signals that the UI can respond to (BL -> UI).
    Defines slots that can then be accessed directly in the UI (UI -> BL).
    Creates and updates an instance of DriveModel to store application state.
    Uses an instance of MotionControllerService to connect to and communicate with the
    drives.
    Defines callback functions that are invoked after a task delegated to the
    MotionControllerService was completed.
    """

    drive_connected_triggered: Signal = Signal()
    """Triggers when a drive is connected."""

    drive_disconnected_triggered: Signal = Signal()
    """Triggers when a drive is disconnected."""

    velocity_left_changed = Signal(float, float, arguments=["timestamp", "velocity"])
    """Triggers when the poller returns a new value.

    Args:
        timestamp (float): timestamp of the new data point.
        velocity (float): velocity of the new data point.
    """

    velocity_right_changed = Signal(float, float, arguments=["timestamp", "velocity"])
    """Triggers when the poller returns a new value.

    Args:
        timestamp (float): timestamp of the new data point.
        velocity (float): velocity of the new data point.
    """

    dictionary_changed = Signal(str, arguments=["dictionary"])
    """Triggers when the dictionary file was selected.

    Args:
        dictionary (str): the path of the selected file.
    """

    config_changed = Signal(str, int, arguments=["config", "drive"])
    """Triggers when a config file was selected.

    Args:
        config (str): the path of the selected file.
        drive (int): the drive the file is for.
    """

    error_triggered = Signal(str, arguments=["error_message"])
    """Triggers when an error occurs while communicating with the drive.

    Args:
        error_message (str): the error message.
    """

    connect_button_state_changed = Signal(int, arguments=["button_state"])
    """Triggers when the state of the connect button changes.

    Args:
        buttons_state (int): the new button state.
    """

    servo_ids_changed = Signal(QJsonArray, arguments=["servo_ids"])
    """Triggers when the scan returned new values for the servo connections.

    Args:
        servo_ids (PySide6.QtCore.QJsonArray): the slave / node IDs identified by the
            scan.
    """

    def __init__(self, mcs: MotionControllerService) -> None:
        super().__init__()
        self.mcs = mcs
        self.mcs.error_triggered.connect(self.error_message_callback)
        self.drive_model = DriveModel()

    @Slot()
    def connect(self) -> None:
        """Connect to the drives using the MotionControllerService and the currently
        selected configuration stored in the DriveModel.
        """
        self.mcs.connect_drives(
            self.connect_callback,
            self.drive_model,
        )

    @Slot()
    def disconnect(self) -> None:
        """Disconnect the drives using the MotionControllerService."""
        self.mcs.disconnect_drives(self.disconnect_callback)

    @Slot(int)
    def enable_motor(self, drive: int) -> None:
        """Enable the motor of a given drive using the MotionControllerService.

        Args:
            drive: the drive to enable
        """
        target = Drive(drive)
        if target == Drive.Left:
            self.mcs.enable_motor(self.enable_motor_l_callback, target)
        else:
            self.mcs.enable_motor(self.enable_motor_r_callback, target)

    @Slot(int)
    def disable_motor(self, drive: int) -> None:
        """Enable the motor of a given drive using the MotionControllerService.

        Args:
            drive: the drive to disable
        """
        if drive == Drive.Left.value:
            self.mcs.run(
                self.disable_motor_l_callback,
                "motion.motor_disable",
                Drive.Left.name,
            )
        else:
            self.mcs.run(
                self.disable_motor_r_callback,
                "motion.motor_disable",
                Drive.Right.name,
            )

    @Slot()
    def handle_new_velocity_data_r(
        self, timestamps: list[float], data: list[list[float]]
    ) -> None:
        """Handles new velocity data coming from a PollerThread. Emits a signal with the
        data prepared in a format that the UI can handle.

        Args:
            timestamps: contains the timestamp of the new data point.
            data: contains the value of the new data point.
        """
        self.velocity_right_changed.emit(timestamps[0], data[0][0])

    @Slot()
    def handle_new_velocity_data_l(
        self, timestamps: list[float], data: list[list[float]]
    ) -> None:
        """Handles new velocity data coming from a PollerThread. Emits a signal with the
        data prepared in a format that the UI can handle.

        Args:
            timestamps: contains the timestamp of the new data point.
            data: contains the value of the new data point.
        """
        self.velocity_left_changed.emit(timestamps[0], data[0][0])

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
            self.scan_servos_callback,
            self.drive_model,
        )

    @Slot(float, int)
    def set_velocity(self, velocity: float, drive: int) -> None:
        """Set the target velocity of a given drive using the MotionControllerService.

        Args:
            velocity: the velocity
            drive: the drive
        """
        self.mcs.run(
            self.log_report,
            "motion.set_velocity",
            velocity,
            servo=Drive(drive).name,
        )

    @Slot(float, int)
    def set_register_max_velocity(self, max_velocity: float, drive: int) -> None:
        """Set a specific register - in this case the one that controls the maximum
        velocity - of a given drive using the MotionControllerService.

        Args:
            max_velocity: the value to set the register to
            drive: the drive
        """
        self.mcs.run(
            self.log_report,
            "communication.set_register",
            "CL_VEL_REF_MAX",
            max_velocity,
            Drive(drive).name,
        )

    @Slot(str)
    def select_dictionary(self, dictionary: str) -> None:
        """Update the DriveModel, setting the dictionary property to the url of the
        file that was uploaded in the UI.
        Also identifies which connection protocol the dictionary belongs to and sets the
        corresponding property in the DriveModel.

        Args:
            dictionary: the url of the dictionary file
        """
        self.drive_model.dictionary = dictionary.removeprefix("file:///")
        self.drive_model.dictionary_type = self.mcs.check_dictionary_format(
            self.drive_model.dictionary
        )
        self.dictionary_changed.emit(os.path.basename(self.drive_model.dictionary))
        self.update_connect_button_state()

    @Slot()
    def reset_dictionary(self) -> None:
        """Resets the dictionary file in the DriveModel."""
        self.drive_model.dictionary = None
        self.drive_model.dictionary_type = None
        self.dictionary_changed.emit("")
        self.update_connect_button_state()

    @Slot(str, int)
    def select_config(self, config: str, drive: int) -> None:
        """Update the DriveModel, setting the config property for a drive to the url of
        the file that was uploaded in the UI.

        Args:
            config: the url of the config file.
            drive: the drive
        """
        config = config.removeprefix("file:///")
        if drive == Drive.Left.value:
            self.drive_model.left_config = config
        else:
            self.drive_model.right_config = config
        self.config_changed.emit(os.path.basename(config), drive)

    @Slot(int)
    def reset_config(self, drive: int) -> None:
        """Resets the config file in the DriveModel for a given drive.

        Args:
            drive: the drive.
        """
        if drive == Drive.Left.value:
            self.drive_model.left_config = None
        else:
            self.drive_model.right_config = None
        self.config_changed.emit("", drive)

    @Slot(int)
    def select_connection(self, connection: int) -> None:
        """Update the DriveModel, setting the connection property to the value that was
        selected in the UI.

        Args:
            connection: the selected connection
        """
        self.drive_model.connection = ConnectionProtocol(connection)
        self.update_connect_button_state()

    @Slot(int)
    def select_interface(self, interface: int) -> None:
        """Update the DriveModel, setting the interface property to the value that was
        selected in the UI.

        Args:
            interface: the selected interface
        """
        self.drive_model.interface_index = interface
        self.update_connect_button_state()

    @Slot(int)
    def select_can_device(self, can_device: int) -> None:
        """Update the DriveModel, setting the can device property to the value that was
        selected in the UI.

        Args:
            can_device: the selected can device
        """
        self.drive_model.can_device = CanDevice(can_device)
        self.update_connect_button_state()

    @Slot(int)
    def select_can_baudrate(self, baudrate: int) -> None:
        """Update the DriveModel, setting the can baudrate property to the value that
        was selected in the UI.

        Args:
            can_baudrate: the selected can baudrate
        """
        self.drive_model.can_baudrate = CAN_BAUDRATE(baudrate)
        self.update_connect_button_state()

    @Slot(int, int)
    def select_node_id(self, node_id: int, drive: int) -> None:
        """Update the DriveModel, setting the can node / slave ID property to the value
        that was selected in the UI (which property is set depends on the drive).

        Args:
            node_id: the selected node / slave ID
            drive: the drive the ID belongs to
        """
        if drive == Drive.Left.value:
            self.drive_model.left_id = node_id
        else:
            self.drive_model.right_id = node_id
        self.update_connect_button_state()

    @Slot()
    def emergency_stop(self) -> None:
        """Immediately disables the motors of all connected drives."""
        self.mcs.emergency_stop(self.log_report)

    def connect_callback(self, thread_report: thread_report) -> None:
        """Callback after the drives where connected. Emits a signal to the UI.

        Args:
            thread_report: the result of the operation that triggered
                the callback
        """
        self.drive_connected_triggered.emit()

    def disconnect_callback(self, thread_report: thread_report) -> None:
        """Callback after the drives where disconnected. Emits a signal to the UI.

        Args:
            thread_report: the result of the operation that triggered
                the callback
        """

        self.drive_disconnected_triggered.emit()
        self.update_connect_button_state()

    def enable_motor_l_callback(self, thread_report: thread_report) -> None:
        """Callback after the motor of a drive was enabled.
        Starts an instance of PollerThread to continuously monitor the velocity of the
        motor.
        Binds the new_data_available_triggered signal of the new PollerThread to a
        function that handles the communication with the UI.

        Args:
            thread_report: the result of the operation that triggered
                the callback
        """
        poller_thread = self.mcs.create_poller_thread(
            Drive.Left.name, [{"name": "CL_VEL_FBK_VALUE", "axis": 1}]
        )
        poller_thread.new_data_available_triggered.connect(
            self.handle_new_velocity_data_l
        )
        poller_thread.start()

    def enable_motor_r_callback(self, thread_report: thread_report) -> None:
        """Callback after the motor of a drive was enabled.
        Starts an instance of PollerThread to continuously monitor the velocity of the
        motor.
        Emits a signal to the UI.

        Args:
            thread_report: the result of the operation that triggered
                the callback
        """
        poller_thread = self.mcs.create_poller_thread(
            Drive.Right.name, [{"name": "CL_VEL_FBK_VALUE", "axis": 1}]
        )
        poller_thread.new_data_available_triggered.connect(
            self.handle_new_velocity_data_r
        )
        poller_thread.start()

    def disable_motor_l_callback(self, thread_report: thread_report) -> None:
        """Callback after the motor of a drive was disabled.
        Stops the corresponding poller thread.

        Args:
            thread_report: the result of the operation that triggered
                the callback
        """
        self.mcs.stop_poller_thread(Drive.Left.name)

    def disable_motor_r_callback(self, thread_report: thread_report) -> None:
        """Callback after the motor of a drive was disabled.
        Stops the corresponding poller thread.

        Args:
            thread_report: the result of the operation that triggered
                the callback
        """
        self.mcs.stop_poller_thread(Drive.Right.name)

    def scan_servos_callback(self, thread_report: thread_report) -> None:
        """Callback after the scan operation was completed. If values where returned,
        updates the DriveModel state and emits a signal to the UI.

        Args:
            thread_report: the result of the operation that triggered
                the callback
        """
        if thread_report.output is not None:
            servo_ids: list[int] = thread_report.output
            self.drive_model.left_id = servo_ids[0]
            self.drive_model.right_id = servo_ids[1]
            self.servo_ids_changed.emit(QJsonArray.fromVariantList(servo_ids))
            self.update_connect_button_state()

    def error_message_callback(self, error_message: str) -> None:
        """Callback when an error occured in a MotionControllerThread.
        Emits a signal to the UI that contains the error message.

        Args:
            error_message: the error message.
        """
        self.error_triggered.emit(error_message)
        self.update_connect_button_state()

    def log_report(self, report: thread_report) -> None:
        """Generic callback that simply logs the result of the operation.

        Args:
            report: the result of the operation that triggered
                the callback
        """
        logger.debug(report)

    def update_connect_button_state(self) -> None:
        """Helper function that calculates the state of the connect button using the
        DriveModel and emits a signal to the UI with the resulting state.
        """
        self.connect_button_state_changed.emit(
            self.drive_model.connect_button_state().value
        )
