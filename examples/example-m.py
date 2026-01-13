# Raspberry Pi Only

import time, os, platform
import logging
logger = logging.getLogger(__name__)

import can
from crate_api import Environment
import crate_api.resource.busio_i2cport
import crate_api.driver.ina260driver

crate = Environment('crate-m-v1.yaml').get_target()

## Enable USB Power for all devices:
usb_power_channels = ['internal-relay', 'ethernet', 'autoeth-bluetooth', 'bluetooth', 'wifi',
                      'usb-managed-1', 'usb-managed-2', 'usb-managed-3', 'usb-managed-4']
for name in usb_power_channels:
    crate.get_driver('PowerProtocol', name=name).on()

# Power Relays
dc1_power = crate.get_driver('PowerProtocol', name='switched-1')
dc2_power = crate.get_driver('PowerProtocol', name='switched-2')
ac1_power = crate.get_driver('PowerProtocol', name='switched-ac')

dc1_power.off()
dc1_power.on()
dc1_power.get()
dc1_power.cycle()

dc2_power.off()
dc2_power.on()

ac1_power.off()
ac1_power.on()

## Power Measurement Unit (on 12VDC Swtiched 1/2)

pmu_1 = crate.get_driver('INA260Driver', name='switched-1')
pmu_1.reset()
pmu_1.mode('continuous')
pmu_1.averaging_count(1)
pmu_1.current_conversion_time(4.156)
pmu_1.voltage_conversion_time(0.140)
print("mode:", pmu_1.mode())
print("averaging_count:", pmu_1.averaging_count())
print("voltage_conversion_time:", pmu_1.voltage_conversion_time())
print("current_conversion_time:", pmu_1.current_conversion_time())

dc1_power.on()
print('-- dc1_power.on()')
time.sleep(0.1)
for i in range(-1,3):
    print("pmu-1 current:", pmu_1.current(),
          "voltage:", pmu_1.voltage(),
          "power:", pmu_1.power())

dc1_power.off()
print('-- dc1_power.off()')
time.sleep(0.1)
for i in range(-1,3):
    print("pmu-1 current:", pmu_1.current(),
          "voltage:", pmu_1.voltage(),
          "power:", pmu_1.power())    
pmu_1.mode('shutdown')

pmu_2 = crate.get_driver('INA260Driver', name='switched-2')
pmu_2.reset()
pmu_2.mode('continuous')
pmu_2.averaging_count(1)
pmu_2.current_conversion_time(4.156)
pmu_2.voltage_conversion_time(0.140)

dc2_power.on()
print('-- dc2_power.on()')
time.sleep(0.1)
for i in range(-1,3):
    print("pmu-2 current:", pmu_2.current(),
          "voltage:", pmu_2.voltage(),
          "power:", pmu_2.power())

dc2_power.off()
print('-- dc2_power.off()')
time.sleep(0.1)
for i in range(-1,3):
    print("pmu-2 current:", pmu_2.current(),
          "voltage:", pmu_2.voltage(),
          "power:", pmu_2.power())    
pmu_2.mode('shutdown')

## CAN 
can1 = crate.get_driver('CANDriver', name='1')
print("CAN-FD1 interface", can1.ifname)
can2 = crate.get_driver('CANDriver', name='2')
print("CAN-FD2 interface", can2.ifname)

# configure interface parameters for CAN-FD.
can1.bitrate = 500_000
can1.sample_point = 80.0
can1.fd_mode = True
can1.dbitrate = 2_000_000
can1.data_sample_point = 80.0
can1.f_clock = 80_000_000
can1.reset()

# configure with explicit BitTiming or BitTimingFd to override bitrate etc.
can1.timing = can.BitTimingFd.from_sample_point(
                             f_clock=80_000_000,
                             nom_bitrate=500_000,
                             nom_sample_point=80.0,
                             data_bitrate=2_000_000,
                             data_sample_point=80.0) 
can1.reset()

# Configure interface for classic CAN
can1.timing = None
can1.fd_mode = False
can1.f_clock = 8_000_000
can1.bitrate = 33333
can1.reset()

# Send message with python-can Bus() object
canbus1 = can1.bus()
try:
    canbus1.send(can.Message(arbitration_id=0xC0FFEE,
                  data=[0,25,1,2,3,4,5],
                  is_extended_id=True))
    print(f"Message sent on {canbus1.channel_info}")
except can.CanError:
    print("Message Not sent")

# Shut down interfaces:
can1.down()
can2.down()

## Bluetooth LE
print('Bluetooth Connectivity Device:', crate.get_driver('nRF52Bluetooth', name='connect').device())
print('Bluetooth Sniffer Device:', crate.get_driver('nRF52Bluetooth', name='sniffer').device())





