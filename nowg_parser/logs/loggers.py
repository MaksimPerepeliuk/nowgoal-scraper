import logging
import logging.config
from nowg_parser.logs.settings import logger_config


logging.config.dictConfig(logger_config)
app_logger = logging.getLogger('app_logger')