src_addr = "10.13.37.1"
dut_addr = "10.13.37.42"

import time, os, subprocess
import logging
logger = logging.getLogger(__name__)

from crate_api import Environment
import pathlib
env = Environment(str(pathlib.Path(__file__).parent.resolve() / 'environments/crate-x6-v1.yaml'))

target_main = env.get_target('main')
target_ch1 = env.get_target('1')

# System power relay on
target_main.get_driver("PowerProtocol", name="power-system").on()

## USB Power Drivers
usb_power_relay = target_main.get_driver('PowerProtocol', name='power-relay')
usb_power_autoeth = target_main.get_driver('PowerProtocol', name='power-autoeth')

# ON
usb_power_relay.on()
usb_power_autoeth.on()

dut1_power = target_ch1.get_driver('PowerProtocol', name='power-dut')
dut1_power.on()


# Automotive Ethernet
# (on crate-x6-v1 DUT Ethernet ports are connected to single ethernet interface via switch)
autoeth = target_main.get_driver('EthernetLinuxDriver')
print("ethernet interface", autoeth.ifname)

autoeth.reset()
autoeth.address_add(src_addr+"/24")


ps = subprocess.run(['ping', '-I', autoeth.ifname, '-c', '3', dut_addr])
ps.check_returncode()
print('ping succeeded')
