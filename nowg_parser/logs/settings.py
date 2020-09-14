logger_config = {
    'version': 1,
    'disable_existing_loggers': False,

    'formatters': {
        'std_format': {
            'format': ('%(levelname)-8s %(filename)s'
                       '[LINE:%(lineno)d %(asctime)s]'
                       '[%(processName)s]'
                       '[%(funcName)s] %(message)s'),
            'datefmt': '%Y-%m-%d %H:%M-%S'
        }
    },
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'level': 'DEBUG',
            'formatter': 'std_format'
        },
        'info_file_handler': {
            'class': 'logging.FileHandler',
            'level': 'INFO',
            'formatter': 'std_format',
            'filename': 'nowg_parser/logs/info.log',
            'encoding': 'utf8',
            'mode': 'a'
        },
        'debug_file_handler': {
            'class': 'logging.FileHandler',
            'level': 'DEBUG',
            'formatter': 'std_format',
            'filename': 'nowg_parser/logs/debug.log',
            'encoding': 'utf8',
            'mode': 'a'
        },
        'error_file_handler': {
            'class': 'logging.FileHandler',
            'level': 'ERROR',
            'formatter': 'std_format',
            'filename': 'nowg_parser/logs/error.log',
            'encoding': 'utf8',
            'mode': 'a'
        }
    },


    'loggers': {
        'app_logger': {
            'level': 'DEBUG',
            'propagate': 'no',
            'handlers': ['debug_file_handler',
                         'error_file_handler',
                         'info_file_handler'],
        },
        'app2_logger': {
            'level': 'DEBUG',
            'propagate': 'no',
            'handlers': ['debug_file_handler',
                         'error_file_handler',
                         'info_file_handler'],
        }
    },
}
