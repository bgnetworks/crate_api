# CAN interposer example that bridges multiple can interfaces.
# Messages received on one interface is sent on all other interfaces.
# Runs on Linux and Windows CRATE hosts.
# scapy package must be installed from pip in the local virtualenv: 'pip install scapy'

# CRATE-X6 channels to use:
can_channels = [1, 2]

# Setup CRATE and get interface names for scapy
import platform
import logging
logger = logging.getLogger(__name__)

from crate_api import Environment
if platform.system() == "Windows":
    crate = Environment('crate-x6-v1_windows.yaml').get_target()
else:
    crate = Environment('crate-x6-v1.yaml').get_target()

# System power relay on (CRATE-X6)
crate.get_driver('PowerProtocol', name='internal-relay').on()
crate.get_driver('PowerProtocol', name='internal-can').on()
crate.get_driver("PowerProtocol", name='internal-system').on()

can_drivers = {chan: crate.get_driver('CANDriver', name=str(chan)) for chan in can_channels}
for chan, driver in can_drivers.items():
    print(chan, driver.ifname)
    driver.up()

# Setup scapy CANSockets
import time
from scapy.all import conf, load_layer, load_contrib, AsyncSniffer
if platform.system() == "Linux":
    conf.contribs["CANSocket"] = {"use-python-can": False}
    conf.contribs["ISOTP"] = {"use-can-isotp-kernel-module": True}
    bustype = 'socketcan'
else:
    conf.contribs["CANSocket"] = {"use-python-can": True}
    conf.contribs["ISOTP"] = {"use-can-isotp-kernel-module": False}
    bustype = 'pcan'
load_layer("can")
load_contrib("cansocket")

sockets = {CANSocket(interface=bustype, channel=driver.ifname, bitrate=500000, fd=False): chan
           for chan, driver in can_drivers.items()}

# This function is called by the sniffer for each received packet on each sniffed socket.
# print() calls are commented out because they slow down sending packets
def prn_send(x):
    if x.flags == "error":
        print("WARNING: Received Error Frame on", x.sniffed_on)
        return None
    #print("====")
    #print("sniffed_on", x.sniffed_on)
    
    # Implement packet filtering / manipulation here:

    # Filtering: drop packets on channel 1 with id 0x666:
    if x.sniffed_on == 1 and x.identifier == 0x666:
        print('dropped packet')
        x.show()
        return None
    
    # Modification: change packets on channel 2 with data 0xDEAD to data 0xBEEF:
    if x.sniffed_on == 2 and x.data == b'\xDE\xAD':
        x.data = b'\xBE\xEF'

    # Injection (conditional): If a message is received with id 0x777 on channel 1, 
    # send an additional message on all channels with id 0x888 and data 0xCAFE
    if x.sniffed_on == 1 and x.identifier == 0x777:
        for outsock in sockets.keys():
            outsock.send(CAN(flags='extended', identifier=0x888, data=b'\xca\xfe'))

    # Send packet on all sockets except the one we recevied this packet on
    for outsock, iface in sockets.items():
        if x.sniffed_on != iface:
            #print("sending on", iface) 
            outsock.send(x)
    #x.show()  # print packet contents to stdout

t = AsyncSniffer(opened_socket=sockets, prn=prn_send)
t.start()

# do stuff here while sniffing

# Injection: send 999#FFFF message once per second while sniffing.
while True:
    for outsock in sockets.keys():
        outsock.send(CAN(identifier=0x999, data=b'\xFF\xFF'))
    time.sleep(1)

t.join() # if not doing anything else, join asyncsniffer thread and wait on it

# Testing on Windows with PCAN-View connected to bridged channels via loopbacks
# indicates this setup can handle full bus load at 500kbaud.
# Testing performed with four 8-byte messages sent at a period of 1ms.