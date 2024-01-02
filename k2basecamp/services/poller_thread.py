import time
from typing import Union

import ingenialogger
from ingeniamotion import MotionController
from PySide6.QtCore import QThread, Signal

logger = ingenialogger.get_logger(__name__)


class PollerThread(QThread):
    """Thread to create a poller object."""

    new_data_available_triggered: Signal = Signal(list, list)
    """Signal emitted when new data is available."""

    def __init__(
        self,
        mc: MotionController,
        drive: str,
        registers: list[dict[str, Union[int, str]]],
        sampling_time: float = 0.125,
        refresh_time: float = 0.125,
        buffer_size: int = 100,
    ) -> None:
        """Constructor of the PollerThread.

        Args:
            mc: MotionController instance.
            drive: drive alias.
            registers: Register to be read.
            sampling_time: Sampling time. Defaults to 0.125.
            refresh_time: Refresh time. Defaults to 0.125.
            buffer_size: Buffer size. Defaults to 100.
        """
        super().__init__()
        self.__mc = mc
        self.__running = False
        self.__registers = registers
        self.__refresh_time = refresh_time
        self.__sampling_time = sampling_time
        self.__buffer_size = buffer_size
        self.__drive = drive

        self.__poller = self.__mc.capture.create_poller(
            self.__registers,
            self.__drive,
            sampling_time=self.__sampling_time,
            buffer_size=self.__buffer_size,
            start=False,
        )

    def run(self) -> None:
        """Start the thread. Periodically retrieve data from the drive."""
        self.__poller.start()
        self.__running = True
        while self.__running:
            time_vectors, data, lost_samples = self.__poller.data
            if lost_samples:
                logger.error("Some poller samples were lost.")
            if len(time_vectors) > 0 and self.__running:
                self.new_data_available_triggered.emit(time_vectors, data)
            time.sleep(self.__refresh_time)

    def stop(self) -> None:
        """Stop the thread"""
        self.__poller.stop()
        self.__running = False
