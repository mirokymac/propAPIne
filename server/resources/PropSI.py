# -*- coding: utf-8 -*-
"""
Created on Fri Apr 20 22:18:40 2018

@author: Zihao.MAI
"""

import logging
from .util.stringlib import string_to_dict
logger = logging.getLogger(__name__)

#==============================================================================
from .porting.prop import mProp
from flask_restful import Resource, reqparse, fields, marshal_with
#====================================================================
parser = reqparse.RequestParser()
parser.add_argument('substance',
                    type=str,
                    required=True)
parser.add_argument('output_type',
                    type=str,
                    required=True)
# maybe better to put all the params in the EXTRA string?
parser.add_argument('intype1',
                    type=str,
                    nullable=True)
parser.add_argument('invalue1',
                    type=float,
                    nullable=True)
parser.add_argument('intype2',
                    type=str,
                    nullable=True)
parser.add_argument('invalue2',
                    type=float,
                    nullable=True)
#parser.add_argument('step',
#                    type=float,
#                    nullable=True)
#parser.add_argument('end',
#                    type=float,
#                    nullable=True)
parser.add_argument('extra', type=str, nullable=True)
#==============================================================================
ret_fields = {
#        'CRC':fields.Raw,
        'result': fields.Raw
        }
#==============================================================================
class PropSI(Resource):
    @marshal_with(ret_fields)
    def get(self):
        args = parser.parse_args()
        
        extra = None
        if args.extra:
            extra = string_to_dict(args.extra)
        
        if extra and "backend" in extra:
            result = mProp(args.substance,
                           args.output_type,
                           args.intype1,
                           args.invalue1,
                           args.intype2,
                           args.invalue2,
                           extra["backend"])
        else:
            result = mProp(args.substance,
                           args.output_type,
                           args.intype1,
                           args.invalue1,
                           args.intype2,
                           args.invalue2)
        return result