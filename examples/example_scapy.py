# Linux or Windows
# scapy package must be installed from pip in the local virtualenv: 'pip install scapy'
can_channel = 1

import platform
import logging
logger = logging.getLogger(__name__)

import can
from crate_api import Environment

if platform.system() == "Windows":
    crate = Environment('crate-x6-v1_windows.yaml').get_target()
else:
    crate = Environment('crate-x6-v1.yaml').get_target()

# System power relay on
crate.get_driver('PowerProtocol', name='internal-relay').on()
crate.get_driver('PowerProtocol', name='internal-can').on()
crate.get_driver("PowerProtocol", name='internal-system').on()
    
# Use a scapy CANSocket
import scapy.all as s
if platform.system() == "Linux":
    s.conf.contribs["CANSocket"] = {"use-python-can": False}
    s.conf.contribs["ISOTP"] = {"use-can-isotp-kernel-module": True}
    bustype = 'socketcan'
else:
    s.conf.contribs["CANSocket"] = {"use-python-can": True}
    s.conf.contribs["ISOTP"] = {"use-can-isotp-kernel-module": False}
    bustype = 'pcan'
s.load_layer("can")
s.load_contrib("cansocket")
s.load_contrib("isotp")

can_driver = crate.get_driver('CANDriver', name='1')
can_driver.up()

with CANSocket(interface=bustype, channel=can_driver.ifname, bitrate=33333, fd=False) as sock:
    sock.send(CAN(identifier=0x123, data=b'hello'))

    # Use a scapy ISOTPSocket()
    with ISOTPSocket(sock,
                     tx_id=0x259, rx_id=0x659) as sock:
        sock.send(ISOTP((b"ISO-TP Message")))


