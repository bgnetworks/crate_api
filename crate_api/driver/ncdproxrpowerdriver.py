import attr, time, struct, serial.tools.list_ports
from pexpect.exceptions import TIMEOUT

from crate_api import target_factory
from crate_api import step
from crate_api import Driver
from crate_api import (PowerResetMixin,
                       SerialDriver,
                       PowerProtocol, 
                       ExecutionError)


@target_factory.reg_driver
@attr.s(eq=False)
class NCDProXRPowerDriver(SerialDriver, PowerResetMixin, PowerProtocol):
    bindings = { "port": "USBSerialPort",
                 "channel": "PowerPort" }

    delay = attr.ib(default=2.0, validator=attr.validators.instance_of(float))
    def __attrs_post_init__(self):
        super().__attrs_post_init__()
        self.port.speed = 115200
        if self.port.port == "auto":
            for port in serial.tools.list_ports.comports():
                if port.vid == 0x0403 and port.pid == 0x6001:
                    self.port.port = port.device
                    try: 
                        self.on_activate()
                        self.get_relays()
                        break
                    except (ExecutionError, TIMEOUT) as e:
                        self.logger.info(
                            "Tried port %s but got exception %s",
                              port, e)
                        continue
            if self.port.port == "auto":
                raise Exception("Unsuccessful 'auto' search for Serial Port")

    def open(self):
        r = 10
        for i in range(r):
            try:
                return super().open()
            except serial.serialutil.SerialException as e:
                if i < r-1:
                    self.logger.debug("RETRY %i SerialException: %s", i, e)
                else:
                    raise e
                time.sleep(0.5)
                continue

    # SerialDriver doesn't have it...
    def _flush(self):
        try:
            self._read()
        except :
            pass

    # Close port after activation so other targets can open it.
    def on_activate(self):
        super().on_activate()
        self.close()

    def set_relay(self, channel, state):
        """ state: relay-coil active high """
        if channel > 8 or channel < 0:
            raise ValueError
        ch = (channel + 8) if state else channel
        m = b'\xAA\x03\xFE' + struct.pack('<B', 0x64+ch) + \
            b'\x01' + struct.pack('<B', 0x10+ch)
        self.open()
        self._flush()
        time.sleep(0.1)
        self._write(m)
        time.sleep(0.1)
        v = self._read(4)
        self.close()
        if v == b'\xAA\x01\x55\x00':
            self.logger.debug("set_relay channel=%d state=%r", channel, state)
            return True
        else:
            raise ExecutionError(
                "set_relay %d %d Failed to read correct response! Got %s" %
                (channel, state, v.hex()))

    def get_relays(self):
        m = b'\xAA\x03\xFE\x7C\x01\x28'
        self.logger.debug(m.hex())
        self.open()
        self._flush()
        time.sleep(0.1)
        self._write(m)
        time.sleep(0.1)
        v = self._read(4)
        self.close()
        if v[0:2] == b'\xAA\x01':
            bl = [(v[2] >> i) & 1 > 0 for i in range(8)]
            self.logger.debug("get_relays %s", repr(bl))
            return bl
        else:
            raise ExecutionError(
                "get_relays Failed to read correct response! Got %s" %
                v.hex())

    @Driver.check_active
    @step()
    def on(self):
        self.set_relay(self.channel.index, not self.channel.invert)

    @Driver.check_active
    @step()
    def off(self):
        self.set_relay(self.channel.index, self.channel.invert)

    @Driver.check_active
    @step()
    def cycle(self):
        self.off()
        time.sleep(self.delay)
        self.on()

    @Driver.check_active
    def get(self):
        return (self.get_relays()[self.channel.index]) ^ self.channel.invert
