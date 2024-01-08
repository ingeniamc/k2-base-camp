from typing import Any, Callable

from ingeniamotion import MotionController

from k2basecamp.models.bootloader_model import BootloaderModel
from k2basecamp.utils.enums import ConnectionProtocol, Drive, stringify_can_device_enum

DEFAULT_DICTIONARY_PATH = "k2basecamp/assets/eve-net-c_can_2.4.1.xdf"


def install_firmware(
    firmware: str,
    id: int,
    bootloader_model: BootloaderModel,
    mc: MotionController,
    drive: Drive,
    progress_callback: Callable[[int], Any],
) -> None:
    """Install firmware to a drive using the MotionController.

    Args:
        firmware: the file containing the firmware.
        id: the node id of the drive.
        bootloader_model: the model with the application state.
        mc: the MotionController to communicate with the drive.
        drive: the drive to install the firmware to.
        progress_callback: callback for when the installation progress updates.
    """
    if not firmware or not id:
        return

    if bootloader_model.connection == ConnectionProtocol.CANopen:
        mc.communication.connect_servo_canopen(
            baudrate=bootloader_model.can_baudrate,
            can_device=stringify_can_device_enum(bootloader_model.can_device),
            dict_path=DEFAULT_DICTIONARY_PATH,
            node_id=id,
            alias=drive.name,
        )
        mc.communication.load_firmware_canopen(
            servo=drive.name,
            fw_file=firmware,
            progress_callback=progress_callback,
        )
        mc.communication.disconnect(servo=drive.name)
    elif bootloader_model.connection == ConnectionProtocol.EtherCAT:
        mc.communication.load_firmware_ecat_interface_index(
            fw_file=firmware,
            if_index=bootloader_model.interface_index,
            slave=id,
        )
