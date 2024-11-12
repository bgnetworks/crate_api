# TODO make this like labgrid/resource/udev.py:USBNetworkInterface()
import attr, logging, platform

from crate_api import target_factory
from crate_api import Resource, USBResource


@target_factory.reg_resource
@attr.s(eq=False)
class CANPort(Resource):
    """This resource describes a system built-in CAN interface port.

    Args:
        ifname (str): system interface name to use"""


    interface = 'socketcan'
    ifname = attr.ib(default='can0',
                    validator=attr.validators.instance_of(str),
                     converter=str)

@target_factory.reg_resource
@attr.s(eq=False)
class USBCANPort(USBResource):
    """This resource describes a USB-attached CAN interface port.

    Args:
        interface (str): interface type to pass to python-can
        channel (str): interface channel to pass to python-can (windows)
        index (int): port index on multiport adapters (socketcan/Linux)"""


    interface = attr.ib(default='socketcan',
                    validator=attr.validators.instance_of(str),
                    converter=str)
    # channel is used on windows to specify the channel as used by python-can
    channel = attr.ib(default='PCAN_USBBUS1',
                    validator=attr.validators.instance_of(str),
                    converter=str)
    # index is used on linux to index the interfaces of a usb can device
    index = attr.ib(default=0,
                    validator=attr.validators.instance_of(int),
                    converter=int)

    @property
    def ifname(self):
        "the Linux socket interface device name ('can0' etc.)"
        if platform.system() == "Linux":
            assert self.device is not None
            c = list(self.device.children)
            if len(c) > self.index:
                return c[self.index]['INTERFACE']
        elif platform.system() == "Windows":
            return self.channel


