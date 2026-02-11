# Example and Self-Test for CRATE-X6-I on Linux
# This expects a standard CRATE-X6 with the following additional peripherals:
# - SerialGear USB-4COMi-SI-M 4 Port RS-485 Adapter connected to USB Managed 1
# - Alpha AWUS036AXML Wifi Adapter connected to USB Managed 2
# - Ezurio BL654 451-00004 Bluetooth LE Connectivity Adapter connected to USB Managed 3
# - Ezurio BL654 451-00004 Bluetooth LE Scanner Adapter connected to USB Managed 4
# (the BLE adapters are currently discovered via VID:PID and do not need to be plugged into specific ports.)

from crate_api import Environment

crate = Environment('crate-x6-i-v1.yaml').get_target()

# System power relay on
crate.get_driver("PowerProtocol", name="internal-system").on()

## Turn on all USB Power Drivers
usb_power_channels = ['internal-autoeth', 'internal-can', 'internal-relay',
                      'usb-managed-1', 'usb-managed-2', 'usb-managed-3',
                      'usb-managed-4', 'usb-managed-5']
for name in usb_power_channels:
    crate.get_driver('PowerProtocol', name=name).on()

## DUT Channel +12V Power Switching
dut_power = [crate.get_driver('PowerProtocol',
                              name='dut-'+str(n)) for n in range(1,7)]

dut_power[0].off()
dut_power[0].on()
dut_power[0].get()
dut_power[0].cycle()

## External RS-485 adapters on USB Managed 1:
try:
    rs485_1 = crate.get_driver('SerialDriver', name='rs485-1')
    rs485_2 = crate.get_driver('SerialDriver', name='rs485-2')
    rs485_3 = crate.get_driver('SerialDriver', name='rs485-3')
    rs485_4 = crate.get_driver('SerialDriver', name='rs485-4')
    print('rs485-1 serial port:', rs485_1.serial.port)
    rs485_1.serial.baudrate = 9600
    rs485_1.write(b'hello port 1 world')
    # uncomment below to test loopback on port 1:
    #print('rs485_1.read():', rs485_1.read(18, timeout=1))
except Exception as e:
    import traceback
    traceback.print_exc()
    print("RS-485 Adapter Failed")
    pass


## External WiFi Adapter on USB Managed 2:
try:
    wifi = crate.get_driver('EthernetLinuxDriver', name='wifi')
    print('WiFi Interface:', wifi.ifname)
    wifi.reset()
    wifi.address_add("10.22.22.22/24")
    wifi.address_flush()
    wifi.down()
    wifi.up()
    wifi.address_add("10.12.34.56/24")
except Exception as e:
    import traceback
    traceback.print_exc()
    print("WiFi Adapter Failed")
    pass

## Bluetooth LE Adapters
# Connectivity Device
try:
    ble_conn = crate.get_driver('nRF52Bluetooth', name='connect')
    print('Bluetooth Connectivity Device:', ble_conn.device())

    import blatann.examples.scanner as scanner
    scanner.main(ble_conn.device())
except Exception as e:
    import traceback
    traceback.print_exc()
    print("Bluetooth Connect Failed")
    pass
    
# Scanner Device
try:
   ble_sniff = crate.get_driver('nRF52Bluetooth', name='sniffer')
   print('Bluetooth Sniffer Device:', ble_sniff.device())
   from crate_api.util.BluetoothSnifferAPI import Sniffer
   import time

   sniffer = Sniffer.Sniffer(portnum=ble_sniff.device(), baudrate=1000000)
   print('BLE Sniffer Starting...')
   sniffer.start()
   print('BLE Sniffer Scanning...')
   sniffer.scan()
   time.sleep(5)
   print(sniffer.getDevices())
   print("inConnection", sniffer.inConnection)
   print("currentConnectRequest", sniffer.currentConnectRequest)
   print("packetsInLastConnection", sniffer.packetsInLastConnection)
except Exception as e:
    import traceback
    traceback.print_exc()
    print("Bluetooth Sniffer Failed")
    pass


## CAN
import can
dut_can = [crate.get_driver('CANDriver', name=str(n)) for n in range(1,7)]
# Reset all CAN channels
for n, dc in enumerate(dut_can):
    dc.reset()
    print(f"DUT {n+1} CAN: {dc.interface} {dc.ifname}")

# Configure interface for classic CAN
dut_can[0].down()
dut_can[0].timing = None
dut_can[0].fd_mode = False
dut_can[0].f_clock = 8_000_000
dut_can[0].bitrate = 33333
dut_can[0].up()

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
