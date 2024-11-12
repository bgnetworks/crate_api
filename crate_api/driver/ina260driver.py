import attr, logging
logger = logging.getLogger(__name__)
from crate_api import (target_factory, step, Driver)

from adafruit_ina260 import INA260, Mode, AveragingCount, ConversionTime

modelist = {'triggered': Mode.TRIGGERED,
            'continuous': Mode.CONTINUOUS,
            'shutdown': Mode.SHUTDOWN}
listmode = {v:k for k,v in modelist.items()}

@target_factory.reg_driver
@attr.s(eq=False)
class INA260Driver(Driver):
    bindings = { "port": "BusIO_I2CPort" }

    address = attr.ib(default=0x40,
                   validator=attr.validators.and_(
                       attr.validators.ge(0x40),
                       attr.validators.le(0x4f)),
                   converter=int)

    def __attrs_post_init__(self):
        super().__attrs_post_init__()
        self.ina260 = INA260(self.port.i2c, self.address)

    def mode(self, setting=None):
        """ Set or retreive current sampling mode

        setting: (string) one of 'triggered', 'continuous' or 'shutdown'
        an invalid value  will not set a mode and return the current mode.
        Setting 'triggered' will trigger a sample collection until a
        new mode is set.
        """
        
        if setting in modelist.keys():
             self.ina260.mode = modelist[setting]
        return listmode[self.ina260.mode]

    @Driver.check_active
    @step()
    def current(self):
        return self.ina260.current

    @Driver.check_active
    @step()
    def voltage(self):
        return self.ina260.voltage

    @Driver.check_active
    @step()
    def power(self):
        return self.ina260.power


    @Driver.check_active
    @step()
    def reset(self):
        self.ina260.reset_bit = 1

    @Driver.check_active
    @step()
    def averaging_count(self, count=None):
        """ Set or retreive current averaging count
        
        count: (int) number of averages,
        must be in [1, 4, 16, 64, 128, 256, 512, 1024] otherwise
        the value will be coerced and a warning will be emitted. """
        d = {1: 0, 4: 1, 16: 2, 64: 3, 128: 4, 256: 5, 512: 6, 1024: 7}
        if count:
            if count not in d.keys():
                cc = count
                count = min(d.keys(), key=lambda x:abs(x-count))
                logger.warn("averaging_count(%d) not in allowed values (%s), cooercing to %s", cc, str(list(d.keys())), count)
            self.ina260.averaging_count = d[count]
        return AveragingCount.get_averaging_count(
            self.ina260.averaging_count)


    @Driver.check_active
    @step()
    def current_conversion_time(self, convtime=None):
        """ Set or retreive Current measurement conversion time
        in milliseconds.
        
        convtime: (float) optional conversion time in milliseconds,
        must be in [0.14, 0.204, 0.332, 0.588, 1.1, 2.116, 4.156, 8.244]
        otherwise the value will be coerced and a warning will be
        emitted. """
        d = {0.140: 0, 0.204: 1, 0.332: 2, 0.588: 3,
             1.100: 4, 2.116: 5, 4.156: 6, 8.244: 7}
        if convtime:
            if convtime not in d.keys():
                ct = convtime
                convtime = min(d.keys(), key=lambda x:abs(x-convtime))
                logger.warn(
                    "current_conversion_time(%.3f) not in (%s), "
                    "cooercing to %.3f", ct,
                    str(list(d.keys())), convtime)
            self.ina260.current_conversion_time = d[convtime]
        return ConversionTime.get_seconds(
            self.ina260.current_conversion_time)

    @Driver.check_active
    @step()
    def voltage_conversion_time(self, convtime=None):
        """ Set or retreive Voltage measurement conversion time
        in milliseconds.
        
        convtime: (float) optional conversion time in milliseconds,
        must be in [0.14, 0.204, 0.332, 0.588, 1.1, 2.116, 4.156, 8.244]
        otherwise the value will be coerced and a warning will be
        emitted. """
        d = {0.140: 0, 0.204: 1, 0.332: 2, 0.588: 3,
             1.100: 4, 2.116: 5, 4.156: 6, 8.244: 7}
        if convtime:
            if convtime not in d.keys():
                ct = convtime
                convtime = min(d.keys(), key=lambda x:abs(x-convtime))
                logger.warn(
                    "voltage_conversion_time(%.3f) not in (%s), "
                    "cooercing to %.3f", ct,
                    str(list(d.keys())), convtime)
            self.ina260.voltage_conversion_time = d[convtime]
        return ConversionTime.get_seconds(
            self.ina260.voltage_conversion_time)

