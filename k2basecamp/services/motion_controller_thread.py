import time
from queue import Queue
from typing import Union

import ingenialogger
from ingenialink.exceptions import ILError, ILIOError
from ingeniamotion.exceptions import IMException
from PySide6.QtCore import QThread, Signal

from k2basecamp.utils.types import motion_controller_task, thread_report

logger = ingenialogger.get_logger(__name__)


class MotionControllerThread(QThread):
    """
    Thread to run ingeniamotion native functions or custom functions defined in the
    MotionControllerService.

    """

    thread_started: Signal = Signal()
    """Signal emitted when the thread starts"""

    task_errored: Signal = Signal(str, arguments=["error_message"])
    """Signal emitted when a task fails.
    The error message is returned by the thread"""

    task_completed: Signal = Signal(
        object,
        thread_report,
        arguments=["callback", "thread_report"],
    )
    """Signal emitted when a task is completed.
    A report [thread_report] is returned by the thread"""

    queue: Queue[Union[motion_controller_task, None]]
    """Task queue - the thread will work until the queue is empty and then
    wait for new tasks.
    """

    def __init__(self) -> None:
        """
        The constructor for MotionControllerThread class
        """
        self.__running = False
        self.queue = Queue()
        super().__init__()

    def run(self) -> None:
        """Run function.
        Emit a signal when it starts (started). Emits a report of
        :class:`~utils.types.thread_report` type using the task_completed
        signal. This report includes the method name, the output of the callback
        function, a timestamp, the duration and the exception raised during the
        callback, if any.
        If the task fails, a task_errored signal with the error message is emitted
        instead.

        """
        self.thread_started.emit()
        self.__running = True
        while self.__running:
            task = self.queue.get()
            if task is None:
                break
            timestamp = time.time()
            raised_exception = None
            output = None
            try:
                output = task.action(*task.args, **task.kwargs)
            except (
                IMException,
                ILError,
                ValueError,
                KeyError,
                FileNotFoundError,
                ConnectionError,
            ) as e:
                raised_exception = e
            duration = time.time() - timestamp
            report = thread_report(
                task.callback.__qualname__,
                output,
                timestamp,
                duration,
                raised_exception,
            )
            if raised_exception is None:
                self.task_completed.emit(task.callback, report)
            else:
                logger.error(report)
                # We only log ILIOErrors, because they are not important enough to
                # warrant displaying a error dialog.
                if not isinstance(raised_exception, ILIOError):
                    self.task_errored.emit(str(report.exceptions))
            self.queue.task_done()

    def stop(self) -> None:
        self.__running = False
        self.queue.put(item=None)
