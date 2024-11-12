# Linux or Windows

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
crate.get_driver("PowerProtocol", name="internal-system").on()

## Turn on all USB Power Drivers
usb_power_channels = ['internal-autoeth', 'internal-can', 'internal-relay',
             'usb-managed-1', 'usb-managed-2', 'usb-managed-3', 'usb-managed-4', 'usb-managed-5']
for name in usb_power_channels:
    crate.get_driver('PowerProtocol', name=name).on()

# DUT Power Relay
dut_power = [crate.get_driver('PowerProtocol', name='dut-'+str(n)) for n in range(1,7)]

dut_power[0].off()
dut_power[0].on()
dut_power[0].get()
dut_power[0].cycle()

for d in dut_power:
    d.off()
    d.on()

## CAN 
dut_can = [crate.get_driver('CANDriver', name=str(n)) for n in range(1,7)]
for n, dc in enumerate(dut_can):
    dc.reset()
    print(f"DUT {n+1} CAN: {dc.interface} {dc.ifname}")

# configure interface parameters for CAN-FD.
dut_can[0].bitrate = 500_000
dut_can[0].sample_point = 80.0
dut_can[0].fd_mode = True
dut_can[0].dbitrate = 2_000_000
dut_can[0].data_sample_point = 80.0
dut_can[0].f_clock = 80_000_000
dut_can[0].reset()

# configure with explicit BitTiming or BitTimingFd to override bitrate etc.
dut_can[0].down()
dut_can[0].timing = can.BitTimingFd.from_sample_point(
                             f_clock=80_000_000,
                             nom_bitrate=500_000,
                             nom_sample_point=80.0,
                             data_bitrate=2_000_000,
                             data_sample_point=80.0) 
dut_can[0].up()

# Configure interface for classic CAN
dut_can[0].down()
dut_can[0].timing = None
dut_can[0].fd_mode = False
dut_can[0].f_clock = 8_000_000
dut_can[0].bitrate = 33333

# Send message with python-can Bus() object
canbus1 = dut_can[0].bus()
try:
    canbus1.send(can.Message(arbitration_id=0xC0FFEE,
                  data=[0,25,1,2,3,4,5],
                  is_extended_id=True))
    print(f"Message sent on {canbus1.channel_info}")
except can.CanError:
    print("Message Not sent")

# Shut down interfaces:
map(lambda x: x.down(), dut_can)

if platform.system() == "Linux":
    # Automotive Ethernet
    # (on crate-x6-v1 DUT Ethernet ports are connected to single ethernet interface via switch)
    autoeth = crate.get_driver('EthernetLinuxDriver')
    print("ethernet interface", autoeth.ifname)

    autoeth.reset()
    autoeth.address_add("10.22.22.22/24")

    autoeth.address_flush()
    autoeth.down()
    autoeth.up()
    autoeth.address_add("10.12.34.56/24")

