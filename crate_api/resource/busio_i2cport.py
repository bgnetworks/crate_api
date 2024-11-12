import attr, platform

from crate_api import (target_factory, Resource)

if platform.system() == "Linux":
    import board,busio

@target_factory.reg_resource
@attr.s(eq=False)
class BusIO_I2CPort(Resource):
    # TODO 'board' doesn't exist on non support platforms (laptops)
    #scl = attr.ib(default=board.SCL)
    #sda = attr.ib(default=board.SDA)

    @property
    def i2c(self):
        "The CircuitPython I2C() object"
        return busio.I2C(board.SCL, board.SDA)
