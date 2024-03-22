from importlib import import_module

import logging
import os
import sys


def get_configuration():
    sys.path.append(os.getcwd())

    path = os.environ.get('APP_SETTINGS', 'application.configuration.configuration')
    if path is None:
        logging.error('APP_SETTINGS not defined. Please set APP_SETTINGS environment variable')
        raise Exception('APP_SETTINGS is not defined')

    module_name, class_name = path.rsplit('.', 1)
    module = import_module(module_name)
    return getattr(module, class_name)
