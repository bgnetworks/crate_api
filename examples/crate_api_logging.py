""" crate_api will by default setup basic logging and install a file output handler
    writing to './.crate_api_debug.log' in the root logger unless disabled by
    setting the environment variable 'CRATEAPI_NODEBUGLOG' *before* loading crate_api.
    Configure logging before loading crate_api to override basic setup.
    """
import os
# os.environ['CRATEAPI_NODEBUGLOG'] = 'true' # uncomment to disable file logging.

import logging

# Customize logging config *before* crate_api import
#logging.basicConfig(format='%(name)s: %(levelname)-8s %(message)s', level=logging.DEBUG)

logger = logging.getLogger(__name__)

import crate_api
print(logging.getLogger('').handlers)

logger.debug('test debug')
logger.info('test info')
logger.warning('test warn')
logger.error('test error')
logger.critical('test critical')

from crate_api import logger 
logger.debug('test debug')
logger.info('test info')
logger.warning('test warn')
logger.error('test error')
logger.critical('test critical')

