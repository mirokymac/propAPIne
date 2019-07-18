# -*- coding: utf-8 -*-
"""
Created on Mon Jul  8 17:21:29 2019

@author: Zihao.MAI

Porting humid air from CoolProp
"""

__all__ = ["TYPES", "INTYPES", "humidAir"]

import logging
from CoolProp.CoolProp import HAPropsSI

logger = logging.getLogger(__name__)

TYPES = ('T', # Dry-Bulb temperature
         'B', # Wet-Bulb temperature
         'D', # Dew-Point temperature
         'V', # Mixture volume per kg dry air
         'Vha', # Mixture volume per kg wet air
         'R', # Relative humidity
         'W', # Humity ratio mass base
         'Y', # Humity ratio mole base
         'H', # Mixture enthalpy per kg dry air
         'Hha', # Mixture enthalpy per kg wet air
         'S', # Mixture entropy per kg dry air
         'Sha', # Mixture entropy per kg wet air
         'C', # Mixture specific heat per kg dry air
         'Cha', # Mixture specific heat per kg wet air
         'M', # Mixture viscosity
         'Z', # Compress factor
         'K', # Mixture thermal conductivity
         'A'  # All possible parameters
         )
TYPES = frozenset(TYPES)

INTYPES = ('T', 'R', 'D', 'W', 'P', 'B', 'H', 'Hha', 
           'Y', 'P_w', 'S', 'Sha', 'V', 'Vha')
INTYPES = frozenset(INTYPES)

def humidAir(outputType: list,
             inputType1: str,
             inputValue1: float,
             inputType2: str,
             inputValue2: float,
             inputType3: str,
             inputValue3: float) -> dict:
    # 初始化错误输出
    errtext = ""
    # 初始化输出字典
    result = dict()
    
    if type(outputType) != list:
        if type(outputType) == str:
            outputType = set([outputType])
        else:
            errtext += 'Input Error:\nOutput Type key word {%s} is not supported.' % outputType
            logger.error(errtext)
            result.update({'error': True,
                           'message': errtext})
            return {'result': result}
    else:
        outputType = set(outputType)
    # 处理输出数据不在范围内的问题。
    if "A" not in outputType:
        if not outputType.issubset(TYPES):
            errtext += 'Input Error:\nOutput Type {%s} is not in list.' % (outputType - TYPES)
                       
            logger.error(errtext)
            result.update({'error': True,
                           'message': errtext})
            outputType &= TYPES
            if len(outputType) == 0:
                return {'result': result}
    else:
        outputType = None
    
    # 要计算压力水汽数据，必须给出T和P参数，而剩余的一个参数则在输入列表中选取
    inputSet = frozenset((inputType1, inputType2, inputType3))
    if len(inputSet) == 3 and inputSet.issubset(INTYPES):
           
        result.update({inputType1: inputValue1, inputType2: inputValue2, inputType3: inputValue3})
        
        if not outputType:
            outputType = TYPES - inputSet - set(('A', ))
        else:
            outputType = outputType - inputSet
            if not len(outputType):
                return {"result": result}
        
        error_counter = 0
        for key in outputType:
            try:
                res = HAPropsSI(key,
                                inputType1,
                                inputValue1,
                                inputType2,
                                inputValue2,
                                inputType3,
                                inputValue3
                                )
                result.update({key: res})
            except Exception as e:
                logger.error("key *%s* failed to calculate: \n %s\n" % (key, str(e)))
                errtext += "[%s]key *%s* failed to cal.\n" % (e.__class__.__name__, key)
                error_counter += 1
                
        else:
            if error_counter > 0:
                result.update({'warning': True,
                               'message':errtext})

    else:
        logger.error('Input Error:\nAt lease one of the parameters must in \'BRWD\'')
        errtext += "input keys [%s, %s, %s] at least has \"T, P, H, S\" and one of \"BWRD\"" % (inputType1, inputType2, inputType3)
        result.update({'error': True,
                       'message':errtext})

    return {'result': result}