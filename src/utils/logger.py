import copy
import os
import socket
from logging.config import dictConfig

# config attributes example:
# "logger": {
#     "email_notifications": false,
#     "to_address_list": ["123@mail.ch", "456@mail.ch"]
# }


class Logger:
    LOGGER_CONFIG_DEFAULT = {
        'version': 1,
        'loggers': {
            '': {  # root logger
                'level': 'NOTSET',
                'handlers': ['debug_console_handler', 'info_rotating_file_handler', 'error_file_handler', 'mail_handler'],
            },
            'my.package': {
                'level': 'WARNING',
                'propagate': False,
                'handlers': ['info_rotating_file_handler', 'error_file_handler'],
            },
        },
        'handlers': {
            'debug_console_handler': {
                'level': 'INFO',
                'formatter': 'info',
                'class': 'logging.StreamHandler',
                'stream': 'ext://sys.stdout',
            },
            'info_rotating_file_handler': {
                'level': 'DEBUG',
                'formatter': 'info',
                'class': 'logging.handlers.RotatingFileHandler',
                'filename': 'info.log',
                'mode': 'a',
                'maxBytes': 102400000,
                'backupCount': 10
            },
            'error_file_handler': {
                'level': 'WARNING',
                'formatter': 'error',
                'class': 'logging.FileHandler',
                'filename': 'error.log',
                'mode': 'a',
            },
            'mail_handler': {
                'level': 'ERROR',
                'formatter': 'error',
                'class': 'logging.handlers.SMTPHandler',
                'mailhost': ('to_be_replaced: "xxx.ch"', 587),
                'credentials': ('<env_variable:MAIL_USERNAME>', '<env_variable:MAIL_PASSWORD>'),
                'fromaddr': 'from.address@xxx.ch',
                'toaddrs': ['<conf_file:to_address_list>'],
                'subject': 'EV-INSIGHTS Notification - Error',
                'secure': ""
            }
        },
        'formatters': {
            'info': {
                # 'format': '%(asctime)s::%(levelname)s::%(name)s::%(module)s|%(lineno)s:: %(message)s'
                'format': '%(asctime)s::%(levelname)s:: %(message)s'
            },
            'error': {
                # 'format': '%(asctime)s::%(levelname)s::%(name)s::%(process)d::%(module)s|%(lineno)s:: %(message)s'
                'format': '%(asctime)s::%(levelname)s:: %(message)s'
            },
        },
    }

    def __init__(self, config, filename=None):
        log_dir = config['output_dir']
        if not os.path.isdir(log_dir):
            os.makedirs(log_dir)
        logger_config_tmp = copy.deepcopy(self.LOGGER_CONFIG_DEFAULT)
        if filename:
            logger_config_tmp['handlers']['info_rotating_file_handler']['filename'] = \
                os.path.join(log_dir, filename + "_" + logger_config_tmp['handlers']['info_rotating_file_handler']['filename'])
            logger_config_tmp['handlers']['error_file_handler']['filename'] = \
                os.path.join(log_dir, filename + "_" + logger_config_tmp['handlers']['error_file_handler']['filename'])
        else:
            logger_config_tmp['handlers']['info_rotating_file_handler']['filename'] = \
                os.path.join(log_dir, logger_config_tmp['handlers']['info_rotating_file_handler']['filename'])
            logger_config_tmp['handlers']['error_file_handler']['filename'] = \
                os.path.join(log_dir, logger_config_tmp['handlers']['error_file_handler']['filename'])

        if config['email_notifications']:
            logger_config_tmp['handlers']['mail_handler']['credentials'] = \
                (os.environ['MAIL_USERNAME'], os.environ['MAIL_PASSWORD'])
            logger_config_tmp['handlers']['mail_handler']['toaddrs'] = list(config['to_address_list'])
            logger_config_tmp['handlers']['mail_handler']['subject'] = \
                "*** " + logger_config_tmp['handlers']['mail_handler']['subject'] + \
                " - " + socket.gethostname() + \
                " - " + output_dir + " ***"
        else:
            logger_config_tmp['loggers']['']['handlers'].remove('mail_handler')
            logger_config_tmp['handlers'].pop('mail_handler')
        
        self.logger_config_final = copy.deepcopy(logger_config_tmp)
        dictConfig(self.logger_config_final)
        return
