import ingenialogger
from ingeniamotion import MotionController
from PySide6.QtCore import QThread, Signal

from k2basecamp.models.bootloader_model import BootloaderModel
from k2basecamp.utils.enums import Drive
from k2basecamp.utils.functions import install_firmware

logger = ingenialogger.get_logger(__name__)


class BootloaderThread(QThread):
    """Thread to install firmware."""

    firmware_installation_complete_triggered = Signal()
    """Triggers when the installation of firmware files was completed successfully."""

    firmware_installation_progress_changed = Signal(int, arguments=["progress"])
    """During installation, information about the progress of the operation is emitted.

    Args:
        progress (int): The progress as a percentage.
    """

    error_triggered = Signal(str, arguments=["error_message"])
    """Triggers when an error occurs while communicating with the drive.

    Args:
        error_message (str): the error message.
    """

    def __init__(
        self,
        drive: Drive,
        bootloader_model: BootloaderModel,
        firmware: str,
        id: int,
    ) -> None:
        super().__init__()
        if not bootloader_model.install_prerequisites_met():
            self.error_triggered.emit(
                "Incorrect or insufficient configuration. Make sure to provide the "
                + "right parameters for the selected connection protocol."
            )
        self.__drive = drive
        self.__bootloader_model = bootloader_model
        self.__firmware = firmware
        self.__id = id

    def run(self) -> None:
        """Start the thread."""

        try:
            install_firmware(
                bootloader_model=self.__bootloader_model,
                mc=MotionController(),
                drive=self.__drive,
                firmware=self.__firmware,
                id=self.__id,
                progress_callback=self.progress_callback,
            )
            self.firmware_installation_complete_triggered.emit()
        except Exception as e:
            logger.error(e)
            # We only log ILIOErrors, because they are not important enough to
            # warrant displaying a error dialog.
            self.error_triggered.emit(str(e))

    def progress_callback(self, progress: int) -> None:
        self.firmware_installation_progress_changed.emit(progress)
