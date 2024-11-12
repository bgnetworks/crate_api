import attr, subprocess, logging, platform
logger = logging.getLogger(__name__)
from crate_api import (target_factory, step, Driver)

import can as pycan

@target_factory.reg_driver
@attr.s(eq=False)
class CANDriver(Driver):
    bindings = { "port": {"USBCANPort","CANPort"} }

    bitrate = attr.ib(default=500_000,
                      validator=attr.validators.instance_of(int),
                      converter=int)
    fd_mode = attr.ib(default=False,
                      validator=attr.validators.instance_of(bool),
                      converter=bool)
    data_bitrate = attr.ib(default=1_000_000,
                       validator=attr.validators.instance_of(int),
                       converter=int)
    sample_point = attr.ib(default=85.0,
                           validator=attr.validators.instance_of(float),
                           converter=float)
    data_sample_point = attr.ib(default=75.0,
                           validator=attr.validators.instance_of(float),
                           converter=float)
    f_clock = attr.ib(default=8_000_000,
                           validator=attr.validators.instance_of(int),
                           converter=int)

    timing = None
    _bus = None

    def __attrs_post_init__(self):
        super().__attrs_post_init__()
        
    @property
    def ifname(self):
        assert self.port.ifname != None
        return self.port.ifname
    
    @property
    def interface(self):
        return self.port.interface
    
    @property
    def bus_kwargs(self):
        return {
            'interface': self.port.interface,
            'channel' : self.ifname,
            'bitrate': self.bitrate,
            'fd': self.fd_mode,
            'timing': (self.timing)}

    def _run_cmd(self, cmd):
        logger.info("CANDriver: %s", cmd)
        ps = subprocess.run(cmd)
        ps.check_returncode()
            
    def _cmd_up(self):
        cmd = [
            "sudo",
            "ip",
            "link",
            "set",
            self.ifname,
            "up",
            "type", "can",
            "bitrate", str(self.bitrate),
            "fd", ('on' if self.fd_mode else 'off')]
        if self.fd_mode:
            cmd.extend(['dbitrate', str(self.dbitrate)])
        return cmd           

    def _cmd_down(self):
        return ["sudo", "ip", "link", "set",
                self.ifname, "down"]

    def up(self):
        if platform.system() == "Linux":
            self._run_cmd(self._cmd_up())

    def bus(self, state=pycan.BusState.ACTIVE, **kwargs):
        try:
            self.up()
        except Exception as e:
            logger.info("Failed to set interface %s up: %s", self.ifname, str(e))
        if self._bus is None:
            k = self.bus_kwargs | {'state': state} | kwargs
            logger.info("CANDriver.bus(%s)", repr(k))
            self._bus = pycan.interface.Bus(**k)
        return self._bus

    def down(self):
        if self._bus is not None:
            # set it to passive so it at least doesn't respond
            # which is probably all socketcan does anyway
            try:
                self._bus.reset()
            except:
                pass
            try:
                self._bus.shutdown()
            except:
                logger.warn("exception in self._bus.shutdown()")
                pass
            self._bus = None
        if platform.system() == "Linux":
            self._run_cmd(self._cmd_down())

    @Driver.check_active
    @step()
    def reset(self):
        self.down()
        self.up()
    
    @step()
    def on_deactivate(self):
        self.down()
