import time, os, platform
import logging
logger = logging.getLogger(__name__)

from crate_api import Environment

crate = Environment('crate-m-v1.yaml').get_target('main')

try:
    print('## nRF52 Connectivity Firmware:')
    bt = crate.get_driver('nRF52Bluetooth', name='connect')
    import blatann.examples.scanner as scanner

    print(bt.device())

    scanner.main(bt.device())
except Exception as e:
    print('Connectivity Firmware not found?')
    print(e)


try:
    print('## nRF52 Sniffer Firmware:')
    bt = crate.get_driver('nRF52Bluetooth', name='sniffer')
    from crate_api.util.BluetoothSnifferAPI import Sniffer

    print(bt.device())

    sniffer = Sniffer.Sniffer(portnum=bt.device(), baudrate=1000000)
    print('Starting...')
    sniffer.start()
    print('Scanning...')
    sniffer.scan()
    time.sleep(5)

    print(sniffer.getDevices())

    print("inConnection", sniffer.inConnection)
    print("currentConnectRequest", sniffer.currentConnectRequest)
    print("packetsInLastConnection", sniffer.packetsInLastConnection)
    
except Exception as e:
    print('nRF52 with Sniffer Firmware not found?')
    raise e



