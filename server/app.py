# -*- coding: utf-8 -*-
"""
Created on Fri Apr 20 14:17:11 2018

@author: zihao.mai
"""

from flask import Flask
from flask_restful import Api
from resources.PropSI import PropSI
from resources.HAProp import HAProp
from resources.Flash import Flash

import logging
logger = logging.getLogger(__name__)

logger.info('Initializing flask app...')
app = Flask(__name__)
logger.info('Done.')
logger.info('Initializing rest API...')
api = Api(app)

logger.info('Initializing rest API...')
api.add_resource(PropSI, '/propsi')
api.add_resource(HAProp, '/haprop')
api.add_resource(Flash, '/flash')

logger.info('Done.')

if __name__ == '__main__':
    app.run('0.0.0.0', port=22001)