
import os, sys, platform, logging
from datetime import datetime

logger = logging.getLogger(__name__)
# Setup debug logging to a file if enabled
if not bool(os.environ.get('CRATEAPI_NODEBUGLOG', default=False)): # enabled by default
    # to make things nice if the caller hasn't setup logging yet
    logging.basicConfig(format='%(name)s: %(levelname)-8s %(message)s', level=logging.WARNING)

    fh = logging.FileHandler(f".crate_api_debug.log", mode='w')
    fh.setLevel(logging.DEBUG)
    fh.setFormatter(logging.Formatter('%(asctime)s %(name)s %(levelname)-8s %(message)s'))

    root_logger = logging.getLogger()
    # set all the root handlers to have the same level as the root logger
    for h in root_logger.handlers:
        h.setLevel(root_logger.getEffectiveLevel())
    root_logger.setLevel(logging.DEBUG)
    root_logger.addHandler(fh)

    logger.debug(
        f"crate_api debug logging to '.crate_api_debug.log' at {datetime.now():%y%m%d%H%M%S}")

# crate_api module exposure
if platform.system() == 'Linux':
    from labgrid import Environment
    from labgrid.factory import target_factory
    from labgrid.resource.common import Resource
    from labgrid.resource.udev import USBResource
    from labgrid.step import step
    from labgrid.driver.common import Driver
    from labgrid.driver.powerdriver import PowerResetMixin
    from labgrid.driver import SerialDriver
    from labgrid.protocol import PowerProtocol
    from labgrid.driver.exception import ExecutionError
    from labgrid.exceptions import NoResourceFoundError

    def get_lg_crate_id_path():
        # To find the udev ID_PATH prefix for the connected crate hardware, we check both ttyUSB0 and ttyUSB1.
        # Assume one is the relay control while the other is the USB Hub power control.
        # Match against a hard coded suffix to identify which is the hub.
        usb_hub_suffix = ".4.4:1.0"
        usb_hub_id_path = ""
        devs = []
        import pyudev
        context = pyudev.Context()

        for device in context.list_devices(subsystem='tty', ID_VENDOR_ID='0403'):
            if device['ID_MODEL_ID'] != '6001':
                continue
            id_path_substring = device['ID_PATH']
            if id_path_substring.endswith(usb_hub_suffix):
                usb_hub_id_path = id_path_substring
            devs.append(str(device))

        if usb_hub_id_path == "":
            raise NoResourceFoundError(
                'Could not find CRATE usb control serial port. (Is the CRATE Hardware connected?)',
                found=devs)

        # trim off the usb_hub_suffix
        usb_hub_id_root = usb_hub_id_path[0:usb_hub_id_path.index(usb_hub_suffix)]
        print("Using USB Hub Base Path: ", usb_hub_id_root)
        return usb_hub_id_root
    
    os.environ.setdefault("LG_CRATE_ID_PATH", get_lg_crate_id_path())
    
elif platform.system() == 'Windows':
    from wabgrid import Environment
    from wabgrid.factory import target_factory
    from wabgrid.resource.common import Resource
    from wabgrid.resource.udev import USBResource
    from wabgrid.step import step
    from wabgrid.driver.common import Driver
    from wabgrid.driver.powerdriver import PowerResetMixin
    from wabgrid.driver import SerialDriver
    from wabgrid.protocol import PowerProtocol
    from wabgrid.driver.exception import ExecutionError
        
    # dummy on windows
    def get_lg_crate_id_path():
        pass

else:
    logger.critical("Unsupported Platform")


from crate_api.resource.powerport import PowerPort
from crate_api.resource.canport import USBCANPort

from crate_api.driver.ncdproxrpowerdriver import NCDProXRPowerDriver
from crate_api.driver.cgmdsuhpowerdriver import CGMDSUHPowerDriver
from crate_api.driver.candriver import CANDriver
from crate_api.driver.ethdriver import EthernetLinuxDriver
from crate_api.driver.bluetooth import nRF52Bluetooth

# Environment loading
from importlib_resources import files, as_file
# using importlib_resources backport until we are supporting only 3.10+
# https://setuptools.pypa.io/en/latest/userguide/datafiles.html#accessing-data-files-at-runtime

class Environment(Environment):

    def __init__(self, name):
        path = None

        if os.path.isfile(name):
            path = name
        
        p = os.path.join(os.getcwd(), name)
        if os.path.isfile(p):
            path = p
        
        p = os.path.join(os.getcwd(), 'environments', name)
        if os.path.isfile(p):
            path = p

        if path:
            logger.debug(f'Using path-local Environment YAML at {path}')
            super().__init__(path)            
        else:
            with as_file(files('crate_api.environments').joinpath(name)) as path:
                if os.path.isfile(path):
                    logger.debug(f'Using crate_api Environment YAML at {path}')
                    super().__init__(str(path))
                else:
                    logger.warn(f'No Environment YAML file matching "{name}" found. Trying anyway')
                    super().__init__(name)
                    
                    
                    
                    

               
