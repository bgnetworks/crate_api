import attr, time

from crate_api import (target_factory,
                       step, 
                       Driver, 
                       SerialDriver, 
                       ExecutionError)

@target_factory.reg_driver
@attr.s(eq=False)
class nRF52Bluetooth(Driver):
    """Serial port mapper, used for nRF52 dongles with
    'nRF52 Connectivity' and 'nRF Sniffer for Bluetooth LE'
    firmare installed"""

    bindings = { "port": "USBSerialPort" }

    @Driver.check_active
    @step()
    def device(self):
        return self.port.port
    
    

