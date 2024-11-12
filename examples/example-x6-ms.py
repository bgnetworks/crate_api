import time
import logging
logger = logging.getLogger(__name__)

import can
from crate_api import Environment

crate = Environment('crate-x6-ms-v1.yaml').get_target()

## Turn on all USB Power Drivers
for name in ['unmanaged', 'relay', 'can-a', 'can-b', 'can-c',
             'managed-1', 'managed-2', 'managed-3', 'managed-4', 'managed-5']:
    crate.get_driver('PowerProtocol', name=name).on()

## Relay control

# all on
for ch in ['dut-1', 'dut-2', 'dut-3', 'dut-4', 'dut-5', 'dut-6',
           'switched-1', 'switched-2']:
    crate.get_driver('PowerProtocol', name=ch).on()

## CAN
dut_can = [crate.get_driver('CANDriver', name=str(ch)) for ch in range(1,7)]

print("dut_can", [x.ifname for x in dut_can])

# configure interface parameters for CAN-FD.
for dc in dut_can:
    dc.timing = can.BitTimingFd.from_sample_point(
        f_clock=80_000_000,
        nom_bitrate=500_000,
        nom_sample_point=80.0,
        data_bitrate=2_000_000,
        data_sample_point=80.0)
    dc.reset()

