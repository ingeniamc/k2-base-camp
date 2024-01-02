from enum import Enum, auto

from ingenialink import CAN_BAUDRATE, CAN_DEVICE
from PySide6.QtCore import QEnum, QObject
from PySide6.QtQml import QmlElement


class ButtonState(Enum):
    Enabled = auto()
    Disabled = auto()
    Active = auto()


class Drive(Enum):
    Left = auto()
    Right = auto()


class ConnectionProtocol(Enum):
    EtherCAT = auto()
    CANopen = auto()


class CanDevice(Enum):
    """CAN Device. Proxy for CAN_DEVICE - necessary because QEnum does not accept string
    enums."""

    KVASER = auto()
    PCAN = auto()
    IXXAT = auto()


def stringify_can_device_enum(device: CanDevice) -> CAN_DEVICE:
    """QEnum does not support string enums, but our connection function from ingenialink
    expects the can device as a string. This helper converts the integer enum
    "CanDevice" that can be used both in python and QML to the string enum the function
    needs.

    Args:
        device: the int enum to convert

    Returns:
        CAN_DEVICE: the converted string enum
    """
    if device == CanDevice.KVASER:
        return CAN_DEVICE.KVASER
    elif device == CanDevice.PCAN:
        return CAN_DEVICE.PCAN
    elif device == CanDevice.IXXAT:
        return CAN_DEVICE.IXXAT


# To be used on the @QmlElement decorator
# (QML_IMPORT_MINOR_VERSION is optional)
QML_IMPORT_NAME = "qmltypes.controllers"
QML_IMPORT_MAJOR_VERSION = 1


@QmlElement
class Enums(QObject):
    """Register enums for use in QML."""

    QEnum(Drive)
    QEnum(ConnectionProtocol)
    QEnum(CanDevice)
    QEnum(CAN_BAUDRATE)
    QEnum(ButtonState)
