import logging
import logging.config

from time import time
from functools import wraps

conf = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'standard': {
            'format': ('[%(asctime)s.%(msecs).03d] [%(levelname)s] '
                       '[pid|%(process)d] [%(name)s:%(lineno)d] %(message)s'),
            'datefmt': '%m-%d %H:%M:%S'
        },
    },
    'handlers': {
        'console': {
            'level': 'DEBUG',
            'class': 'logging.StreamHandler',
            'formatter': 'standard',
        },
    },
    'loggers': {
        'app': {
            'handlers': ['console'],
            'level': 'DEBUG',
            'propagate': True
        },
    }
}
logging.config.dictConfig(conf)
levelnames = logging._levelToName

# create logger
project_logger = logging.getLogger('app')
