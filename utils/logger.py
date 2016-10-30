#!/usr/bin/python3
# -*- coding: utf-8 -*-


import logging

logger = logging.getLogger(__name__)
formatter = logging.Formatter('%(asctime)s - %(module)s(%(levelname)s) - %(message)s', datefmt='%Y-%m-%d %H:%M:%S')
fh = logging.FileHandler('./logs/app_log.txt')
fh.setLevel(logging.WARNING)
fh.setFormatter(formatter)

logger.addHandler(fh)

ch = logging.StreamHandler()
ch.setLevel(logging.DEBUG)
ch.setFormatter(formatter)
logger.addHandler(ch)
logger.setLevel(logging.DEBUG)

logger.debug('Logger imported')