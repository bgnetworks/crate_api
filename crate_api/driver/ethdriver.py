import attr, time, struct, subprocess, logging

from crate_api import (target_factory, step,  Driver)

@target_factory.reg_driver
@attr.s(eq=False)
class EthernetLinuxDriver(Driver):
    bindings = { "port": "USBNetworkInterface" }

    address = attr.ib(default=None,
                      validator=attr.validators.instance_of(str),
                      converter=str)

    def __attrs_post_init__(self):
        super().__attrs_post_init__()

    @property
    def ifname(self):
        return self.port.ifname
        
    def _run_cmd(self, cmd):
        logging.debug("EthernetLinuxDriver: %s", cmd)
        ps = subprocess.run(cmd)
        ps.check_returncode()
            
    def _cmd_up(self):
        return ["sudo",
                "ip",
                "link",
                "set",
                self.ifname,
                "up"]

    def _cmd_address_add(self, address):
        return ["sudo",
                "ip",
                "address",
                "add",
                str(address),
                "dev",
                self.ifname]

    def _cmd_address_flush(self):
        return ["sudo",
                "ip",
                "address",
                "flush",
                "dev",
                self.ifname,
                "scope",
                "global"]
    
    def _cmd_down(self):
        return ["sudo", "ip", "link", "set",
                self.ifname, "down"]

    @Driver.check_active
    @step()
    def address_add(self, address=None):
        if (address is not None) or (self.address is not None and self.address != 'None' ):
            self._run_cmd(self._cmd_address_add(address if address else self.address))

    @Driver.check_active
    @step()
    def address_flush(self):
        self._run_cmd(self._cmd_address_flush())

    @Driver.check_active
    @step()
    def down(self):
        self._run_cmd(self._cmd_down())

    @Driver.check_active
    @step()
    def up(self):
        self._run_cmd(self._cmd_up())
        self.address_add()

    @Driver.check_active
    @step()
    def reset(self):
        self.down()
        self.address_flush()
        self.up()

