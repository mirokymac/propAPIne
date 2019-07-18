# -*- coding: utf-8 -*-
"""
Created on Fri Apr 20 22:42:29 2018

@author: Zihao.MAI
"""

import logging
logger = logging.getLogger(__name__)

#==============================================================================
from .porting.humidAir import humidAir
from flask_restful import Resource, reqparse, fields, marshal_with

parser = reqparse.RequestParser()
parser.add_argument('output_type',
                    type=str,
                    required=True)
parser.add_argument('intype1',
                    type=str,
                    required=True)
parser.add_argument('invalue1',
                    type=float)
parser.add_argument('intype2',
                    type=str,
                    required=True)
parser.add_argument('invalue2',
                    type=float,
                    required=True)
parser.add_argument('intype3',
                    type=str,
                    required=True)
parser.add_argument('invalue3',
                    type=float,
                    required=True)
parser.add_argument('extra', nullable=True)
#==============================================================================
ret_fields = {
#        'CRC':fields.Raw,
        'result': fields.Raw
        }
#==============================================================================
class HAProp(Resource):
    @marshal_with(ret_fields)
    def get(self):
        args = parser.parse_args()
        result = humidAir(args.output_type,
                          args.intype1,
                          args.invalue1,
                          args.intype2,
                          args.invalue2,
                          args.intype3,
                          args.invalue3)
        return result