import attr

from crate_api import target_factory
from crate_api import Resource

@target_factory.reg_resource
@attr.s(eq=False)
class PowerPort(Resource):
    """This resource describes a generic power port.
    Drivers using this resource also need to
    bind the communication port seperately.

    Args:
        index (int): port index
        invert (bool): whether the logic level is inverted (active-low)"""
    index = attr.ib(default=0,
                    validator=attr.validators.instance_of(int),
                    converter=int)
    invert = attr.ib(default=False,
                     validator=attr.validators.instance_of(bool),
                     converter=bool)
