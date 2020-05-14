# -*- coding: utf-8 -*-
from src.core.utils import pyutils

CONFIG = pyutils.load_config('config.yaml')

ADMIN_USERNAME                  = CONFIG['admin username']
API_TOKEN                       = CONFIG['api token']
SUPPORT_MAIL                    = CONFIG['mail']
DATABASE                        = CONFIG['database']
ENABLE_TOR                      = CONFIG['enable tor']
DEBUG                           = CONFIG['debug']

AVAILABLE_COUNTRIES_LIST        = CONFIG['countries']
PROMOCODES                      = CONFIG['promocodes']
