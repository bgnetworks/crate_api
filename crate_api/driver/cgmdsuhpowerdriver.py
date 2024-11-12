import attr, time, serial.tools.list_ports
from pexpect.exceptions import TIMEOUT

from crate_api import (target_factory,
                       step, 
                       Driver, 
                       PowerResetMixin, 
                       SerialDriver, 
                       PowerProtocol, 
                       ExecutionError)


# the order of teh bytes is weird for unknown reasons
# byte order: 10X2XXXX
def decode_usb_state(v):
    v = v[3:4] + v[0:1] + v[1:2]
    vi = int(v, 16)
    return [(vi >> i) & 1 != 0 for i in range(10)]

def encode_usb_state(bl):
    vi = 0xFFF
    for i in range(len(bl)):
        vi = vi & ~(1 << i) if not bl[i] else vi
    v = bytes(hex(vi).upper(), encoding='utf8')[2:]
    return v[1:2] + v[2:3] + b'F' + v[0:1]

@target_factory.reg_driver
@attr.s(eq=False)
class CGMDSUHPowerDriver(SerialDriver, PowerResetMixin, PowerProtocol):
    bindings = { "port": {"USBSerialPort", "RawSerialPort"},
                 "channel": "PowerPort" }
    delay = attr.ib(default=2.0, validator=attr.validators.instance_of(float))
    
    def __attrs_post_init__(self):
        super().__attrs_post_init__()
        self.port.speed = 9600
        if self.port.port == "auto":
            for port in serial.tools.list_ports.comports():
                if port.vid == 0x0403 and port.pid == 0x6001:
                    self.port.port = port.device
                    try: 
                        self.on_activate()
                        self.get_usb()
                        break
                    except (ExecutionError, TIMEOUT) as e:
                        self.logger.info(
                            "Tried port %s but got exception %s",
                              port, e)
                        continue
            if self.port.port == "auto":
                raise Exception("Unsuccessful 'auto' search for Serial Port (is the CRATE hardware connected?)")
            
    def open(self):
        r = 5
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
    
    # SerialDriver doesn't have it??
    def _flush(self):
        try:
            self._read(timeout=0.1)
        except TIMEOUT:
            pass

    # Another hack: close port after activation so other targets can open it.
    def on_activate(self):
        super().on_activate()
        self.close()

    def get_usb(self, retries=4):
        for i in range(retries):
            self.open()
            self._flush()
            self._write(b'GP\x0d')
            v = self._read(10, timeout=1.0)
            #self.logger.debug('got: '+v.hex())
            self.close()
            if v[8:10] == b'\x0d\x0a':
                bl = decode_usb_state(v)
                self.logger.debug("get_usb %s", repr(bl))
                return bl
            else:
                m = "get_usb Failed to read correct response! Got %s" % v.hex()
                if i >= retries-1:         
                    raise ExecutionError(m)
                else:
                    self.logger.warning(m)

    def set_usb(self, bl, password=b'pass    ', retries=4):
        for i in range(retries):
            v = encode_usb_state(bl) + b'FFFF'
            self.open()
            self._flush()
            self._write(b'SP' + password + v + b'\x0d')
            vr = self._read(11, timeout=1.0)
            self.close()
            if vr == b'G' + v + b'\x0d\x0a':
                self.logger.debug("set_usb state=%s", bl)
                return True
            else:
                m = "set_usb %s Failed to read correct response! Got %s" % (bl, v)
                if i >= retries-1:
                    raise ExecutionError(m)
                else:
                    self.logger.warning(m)

    @Driver.check_active
    @step()
    def on(self):
        v = self.get_usb()
        v[self.channel.index] = ~self.channel.invert
        self.set_usb(v)

    @Driver.check_active
    @step()
    def off(self):
        v = self.get_usb()
        v[self.channel.index] = self.channel.invert
        self.set_usb(v)

    @Driver.check_active
    @step()
    def cycle(self):
        self.off()
        time.sleep(self.delay)
        self.on()

    @Driver.check_active
    def get(self):
        return self.get_usb()[self.channel.index] ^ self.channel.invert
