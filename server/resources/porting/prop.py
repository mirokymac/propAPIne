# -*- coding: utf-8 -*-
"""
Created on Tue Jul  9 11:17:03 2019

@author: Zihao.MAI

porting of cool prop gas properties
"""

__all__ = ["mProp", "flasher"]

REFPROP_READY = False

from difflib import SequenceMatcher
from functools import reduce
from json import load as load_json
import logging
#from os.path import isfile, getsize
#import pickle
import re
import CoolProp.CoolProp as cp

from ..util.load_csv import Load_csv, Key

# 初始化环境
logger = logging.getLogger(__name__)
# 输入输出变量列表
# 不建议H和S作为intype，因为使用的reference不一样
loader = Load_csv(r'./common/CoolProp.AbstractState.IO.csv')

tmp_SIcal_types = loader(Key(0))
tmp_io_flags = loader(Key(2))
tmp_qc_flags = loader(Key(3))
tmp_ABcal_types = loader(Key(4))

OTYPE = dict(zip(tmp_SIcal_types, tmp_ABcal_types))
ITYPE = frozenset([i for i, j in zip(tmp_SIcal_types, tmp_io_flags) if "I" in j])
QCTYPE = frozenset([i for i, j in zip(tmp_SIcal_types, tmp_qc_flags) if j])
OTYPE_MIX = {
        "VAPFRAC": "mole_fractions_vapor",
        "LIQFRAC": "mole_fractions_liquid"
            }
OTYPE_COMBO =  {
        "CRIT": frozenset(("TCRIT", "PCRIT", "ACENTRIC", "M")),
        "FLOW": frozenset(("D", "V", "M", "Z")),
        "HEAT": frozenset(("S", "H", "U", "CP"))
                }

# 构建ITYPE_AB
def input_construct(type1:str, type2:str, value1:float, value2:float):
    type1 = type1[0] + type1[1:].lower()
    type2 = type2[0] + type2[1:].lower()
    if type1 in "DHSU":
        type1 += "mass"
    if type2 in "DHSU":
        type2 += "mass"
    res = None
    if type1[0] < type2[0]:
        res = {
            "ipair": getattr(cp, type1 + type2 + "_INPUTS"),
            "Value1": value1,
            "Value2": value2
                }
    else:
        res = {
            "ipair": getattr(cp, type2 + type1 + "_INPUTS"),
            "Value1": value2,
            "Value2": value1
                }
    return res

TYPE_PATTERN = r"[A-Za-z0-9]+"
MIXTURE_PATTERN = r"[A-Z0-9]+\s?\:\s?\d+\.?\d*"

del loader, tmp_ABcal_types, tmp_io_flags, tmp_qc_flags, tmp_SIcal_types
# 物料字典
loader = './common/fluidlist.json'
    
with open(loader, "r") as loader:
    SUBS_P = load_json(loader)
#SUBS_M_CP = dict()
#SUBS_M_REFPROP = dict()

# 尝试载入REFPROP
PATH_TO_REFPROP = "./refprop/"

cp.set_config_string(5, PATH_TO_REFPROP)
try:
    cp.PropsSI('H', 'P', 101325, 'Q', 1, 'REFPROP::Water')
    REFPROP_READY = True
    logger.critical("Refprop loaded.")
except:
    REFPROP_READY = False
    logger.critical("Refprop unable to load.")

#def prop(sub:str,
#         outType:list,
#         inputType1:str,
#         inputValue1:float,
#         inputType2:str,
#         inputValue2:float,
#         backend:str="CP")-> dict:
#    
#    pass
#
## 废弃代码： mProp/AbstractState可以完全覆盖这部分的内容。
#def pProp(sub:str,
#          outType:list,
#          inputType1:str,
#          inputValue1:float,
#          inputType2:str,
#          inputValue2:float,
#          backend:str="CP")-> dict:
#    
#    res = dict()
#    errtext = ""
#    mode_refprop = False
#    extend_backend_req = False
#    # 检查REFPROP可用性
#    if backend == "REFPROP":
#        if REFPROP_READY:
#            mode_refprop = True
#        else:
#            errtext += "Warning: No REFPROP support on server!\n"
#            res.update({"warning": True,
#                        "message": errtext})
#            mode_refprop = False
#    # 转换输出关键字为list
#    if type(outType) != list:
#        if type(outType) == str:
#            outType = [outType]
#        else:
#            errtext += "Input Error: Invalid output type: " + str(outType)
#            logger.error(errtext)
#            res.update({"error": True,
#                        "message": errtext})
#            return {"result": res}
#    # 将所有文本输入转化为大写
#    sub = sub.upper()
#    backend = backend.upper()
#    inputType1 = inputType1.upper()
#    inputType2 = inputType2.upper()
#    outType = set(list(map(str.upper, outType)))
#    
#    # 检查纯物质名字是否受到支持
#    if sub in SUBS_P:
#        if mode_refprop:
#            if SUBS_P[sub][1] != "N/A":
#                errtext += "Input Error: Not a REFPROP supported substance" + str(sub)
#                logger.error(errtext)
#                res.update({"error": True,
#                            "message": errtext})
#                return {"result": res}
#            else:
#                sub = "REFPROP::" + SUBS_P[sub][1]
#        else:
#            # 检查使用的backend类型
#            if backend in ("CP", "COOLPROP"):
#                sub = SUBS_P[sub][0]
#            elif backend in ("PENGROBINSON", "PENG-ROBINSON", "PR"):
#                sub = "PR::" + SUBS_P[sub][0]
#            else:
#                errtext += "Input Error: Not supported backend [%s] requested." % backend
#                logger.error(errtext)
#                res.update({"error": True,
#                            "message": errtext})
#                return {"result": res}
#    else:
#        extend_backend_req = True
#    
#    if inputType1 == inputType2 and not set(outType).issubset(QCTYPE):
#        errtext += "Input Error. Only one input Type [%s] is given." % inputType1
#        logger.error(errtext)
#        res.update({"error": True,
#                    "message": errtext})
#        return {"result": res}
#    
#    if SequenceMatcher(None, inputType1, inputType2).find_longest_match(0, len(inputType1), 0, len(inputType2)).size and not set(outType).issubset(QCTYPE):
#        errtext += "Input Error. Input Type [%s&%s] is the same." % (inputType1, inputType2)
#        logger.error(errtext)
#        res.update({"error": True,
#                    "message": errtext})
#        return {"result": res}
#        
#    if {inputType1, inputType2}.issubset(ITYPE) and not set(outType).issubset(QCTYPE):
#        errtext += "Input Error. Invalid input type combo [%s&%s]." % (inputType1, inputType2)
#        logger.error(errtext)
#        res.update({"error": True,
#                    "message": errtext})
#        return {"result": res}
#    
#    for item in ("H", "S"):
#        if item in inputType1 + inputType2:
#            errtext += "Warning: Unexpected result due to [%s] using difference Reference point on different backend.\n" % item
#            logger.warning(errtext)
#            res.update({"warning": True,
#                        "message": errtext})
#    
#    if type(inputValue1) == float and type(inputValue2) == float:
#        errtext += "Input Error. Invalid values are not numbers."
#        logger.error(errtext)
#        res.update({"error": True,
#                    "message": errtext})
#        return {"result": res}
#    
#    # 处理输出项
#    for item in set(OTYPE_COMBO.keys()).intersection(outType):
#        outType.remove(item)
#        outType.union(OTYPE_COMBO[item])
#        
#    if outType - set(OTYPE.keys()):
#        errtext += "Warning: Unsupported Output Type keywords: %s \n" % list(outType - OTYPE)
#        logger.warning(errtext)
#        res.update({"warning": True,
#                    "message": errtext})
#    
#    outType = outType.intersection(OTYPE.keys())
#    
#    for item in outType:
#        try:
#            if extend_backend_req:
#                # todo: impletementing of pProp_extend()
#                res.update(pProp_extend())
#            else:
#                res.update({item: cp.PropsSI(item, inputType1, inputValue1, inputType2, inputValue2, sub)})
#        except Exception as e:
#            errtext += "Calculation Error: Fail to cal [%s]:\n" % item
#            errtext += str(e)
#            res.update({"warning": True,
#                        "message": errtext})
#    
#    if {"message", "warning"} == set(res.keys()):
#        errtext += "Fatal Calculation Error: No result calculated!"
#        res.update({"warning": True,
#                    "message": errtext})
#    
#    return {"result": res}
    
            
def mProp(sub:str,
          outType:list,
          inputType1:str,
          inputValue1:float,
          inputType2:str,
          inputValue2:float,
          backend:str="CP")-> dict:
    res = dict()
    errtext = ""
    mode_refprop = False
    extend_backend_req = False
    mixture = None
    flash = []
    # 检查REFPROP可用性
    if backend == "REFPROP":
        if REFPROP_READY:
            mode_refprop = True
        else:
            errtext += "Warning: No REFPROP support on server!\n"
            res.update({"warning": True,
                        "message": errtext})
            mode_refprop = False
    # 转换输出关键字为list
    if type(outType) != list:
        if type(outType) == str:
            outType = re.findall(TYPE_PATTERN, outType)
        else:
            errtext += "Input Error: Invalid output type: " + str(outType)
            logger.error(errtext)
            res.update({"error": True,
                        "message": errtext})
            return {"result": res}
    # 将所有文本输入转化为大写
    sub = sub.upper()
    backend = backend.upper()
    inputType1 = inputType1.upper()
    inputType2 = inputType2.upper()
    outType = set(list(map(str.upper, outType)))
    
    # 检查纯物质名字是否受到支持
    # 1-检查REFPROPbackend可用性
    if sub in SUBS_P:
        if mode_refprop:
            if SUBS_P[sub][1] == "N/A":
                errtext += "Input Error: Not a REFPROP supported substance " + str(sub)
                logger.error(errtext)
                res.update({"error": True,
                            "message": errtext})
                return {"result": res}
            else:
                sub =  SUBS_P[sub][1]
        else:
            # 检查使用的backend类型
            if backend in ("CP", "COOLPROP") or (not mode_refprop and backend == "REFPROP"):
                sub_ = SUBS_P[sub][0]
            elif backend in ("PENGROBINSON", "PENG-ROBINSON", "PR"):
                sub_ = SUBS_P[sub][0]
            else:
                errtext += "Input Error: Not supported backend [%s] requested." % backend
                logger.error(errtext)
                res.update({"error": True,
                            "message": errtext})
                return {"result": res}

# todo: make extend pure backend avaible

            if sub_ == "N/A":
                # extend_backend_req = True
                errtext += "Input Error: Not a CoolProp supported substance " + str(sub)
                logger.error(errtext)
                res.update({"error": True,
                            "message": errtext})
                return {"result": res}
            sub = sub_
            del sub_
    else:
        # 2-检查混合物可用性
        # 2.1-检查是否输入了混合物组分
        # 2.2-检查是否在组成自定义混合物的物质名中包含了混合物名称
        # 2.3-检查组成自定义混合物的物质是否都是物性数据库支持的物质
        # 2.4-检查各物质份额是否均为正数
        # 2.5-归一化混合物组成
        mixture = re.findall(MIXTURE_PATTERN, sub)
        if mixture:
            # get substance name
            sub = list(map(lambda x: x.split(":")[0], mixture))
            # get substance fraction
            mixture = list(map(lambda x: float(x.split(":")[1]), mixture))
            
            if set(sub) - set(SUBS_P.keys()):
                errtext += "Input Error: Not supported substance for mixture: " + ", ".join(sub)
                logger.error(errtext)
                res.update({"error": True,
                            "message": errtext})
                return {"result": res}
            else:
                if reduce(lambda acc, x: SUBS_P[x][2] or acc, sub, False):
                    errtext += "Input Error: Building a mixture with a mixture..."
                    logger.error(errtext)
                    res.update({"error": True,
                            "message": errtext})
                    return {"result": res}
                else:
                    if backend in ("CP", "COOLPROP"):
                        sub = "&".join([SUBS_P[i][0] for i in sub])
                    elif mode_refprop:
                        sub = "&".join([SUBS_P[i][1] for i in sub])
                        if "N/A" in sub:
                            errtext += "Input Error: Not REFPROP supported substance is detected."
                            logger.error(errtext)
                            res.update({"error": True,
                                        "message": errtext})
                            return {"result": res}

             # 检查混合组分输入是否均为正数
            if not reduce(lambda acc, x: acc and (x > 0), mixture, True):
                errtext += "Input Error: Building a mixture with a mixture..."
                logger.error(errtext)
                res.update({"error": True,
                        "message": errtext})
                return {"result": res}
            mixture = [i/sum(mixture) for i in mixture]
        else:
            extend_backend_req = True

    if  not outType.issubset(QCTYPE):
        if inputType1 == inputType2:
            errtext += "Input Error. Only one input Type [%s] is given." % inputType1
            logger.error(errtext)
            res.update({"error": True,
                        "message": errtext})
            return {"result": res}
        
        if SequenceMatcher(None, inputType1, inputType2).find_longest_match(0, len(inputType1), 0, len(inputType2)).size:
            errtext += "Input Error. Input Type [%s&%s] is the same." % (inputType1, inputType2)
            logger.error(errtext)
            res.update({"error": True,
                        "message": errtext})
            return {"result": res}
            
        if not {inputType1, inputType2}.issubset(ITYPE):
            errtext += "Input Error. Invalid input type combo [%s&%s]." % (inputType1, inputType2)
            logger.error(errtext)
            res.update({"error": True,
                        "message": errtext})
            return {"result": res}
    
    for item in ("H", "S"):
        if item in inputType1 + inputType2:
            errtext += "Warning: Unexpected result due to [%s] using difference Reference point on different backend.\n" % item
            logger.warning(errtext)
            res.update({"warning": True,
                        "message": errtext})
    
    try:
        inputValue1 = float(inputValue1)
        inputValue2 = float(inputValue2)
    except:
        errtext += "Input Error. Invalid values are not numbers."
        logger.error(errtext)
        res.update({"error": True,
                    "message": errtext})
        return {"result": res}
    
    if backend in ("PENGROBINSON", "PENG-ROBINSON", "PR"):
        backend = "PR"
    elif backend in ("CP", "COOLPROP") or not mode_refprop:
        backend = "HEOS"
    elif backend == "REFPROP" and mode_refprop:
        backend = "REFPROP"
    
    # 处理输出项
    # 构建闪蒸计算输出
    flash = set(OTYPE_MIX.keys())
    flash &= outType
    outType -= flash
    # 如果将进行闪蒸计算而目标组成不是混合物
    if not mixture and flash:
        flash = []
        errtext += "Input Error. Not support flash calculation for predefine mixture or pure component."
        logger.error(errtext)
        res.update({"error": True,
                    "message": errtext})
    
    # 构建组合输出
    for item in set(OTYPE_COMBO.keys()).intersection(outType):
        outType.remove(item)
        outType = outType.union(OTYPE_COMBO[item])
    
    # 构建普通输出
    if outType - set(OTYPE.keys()):
        errtext += "Warning: Unsupported Output Type keywords: %s \n" % list(outType - set(OTYPE.keys()))
        logger.warning(errtext)
        res.update({"warning": True,
                    "message": errtext})
    
    outType = outType.intersection(OTYPE.keys())
    
    if extend_backend_req:
        # todo: impletementing of mProp_extend()
        res.update(mProp_extend())
    else:
        sub = cp.AbstractState(backend, sub)
        if mixture:
            sub.set_mole_fractions(mixture)
        sub.update(
                **input_construct(
                          inputType1,
                          inputType2,
                          inputValue1,
                          inputValue2
                          )
                )
        
        for item in outType:
            try:
                res.update({
                        item: sub.keyed_output(getattr(cp, OTYPE[item]))
                        })
            except Exception as e:
                errtext += "Calculation Error: Fail to cal [%s]:\n" % item
                errtext += str(e)
                res.update({"warning": True,
                            "message": errtext})

        for item in flash:
            try:
                res.update({
                        item: getattr(sub, OTYPE_MIX[item])()
                        })
            except Exception as e:
                errtext += "Calculation Error: Fail to cal [%s]:\n" % item
                errtext += str(e)
                res.update({"warning": True,
                            "message": errtext})

    if {"message", "warning"} == set(res.keys()):
        errtext += "Fatal Calculation Error: No result calculated!"
        res.update({"warning": True,
                    "message": errtext})
    
    return {"result": res}

#
#def pProp_extend():
#    pass

def mProp_extend():
    errtext = ""
    errtext += "Extended component database not impletemented."
    logger.warning(errtext)
    return {"error": True, "message": errtext}
    
def flasher(sub:str,
            inputType1:str,
            inputValue1:float,
            inputType2:str,
            inputValue2:float,
            backend:str="CP")-> dict:
    res = dict()
    errtext = ""
    extend_backend_req = False
    mode_refprop = False
    mixture = None
    outType = ("D", "H", "M", "S", "U", "V", "Z")
    # 检查REFPROP可用性
    if backend == "REFPROP":
        if REFPROP_READY:
            mode_refprop = True
        else:
            errtext += "Warning: No REFPROP support on server!\n"
            res.update({"warning": True,
                        "message": errtext})
            mode_refprop = False
    # 将所有文本输入转化为大写
    sub = sub.upper()
    backend = backend.upper()
    inputType1 = inputType1.upper()
    inputType2 = inputType2.upper()
    
    # 检查纯物质名字是否受到支持

    # 2-检查混合物可用性
    mixture = re.findall(MIXTURE_PATTERN, sub)
    if mixture:
        # get substance name
        sub = list(map(lambda x: x.split(":")[0], mixture))
        # get substance fraction
        mixture = list(map(lambda x: float(x.split(":")[1]), mixture))
        
        if set(sub) - set(SUBS_P.keys()):
            errtext += "Input Error: Not supported substance for mixture: " + ", ".join(sub)
            logger.error(errtext)
            res.update({"error": True,
                        "message": errtext})
            return {"result": res}
        else:
            if reduce(lambda acc, x: SUBS_P[x][2] or acc, sub, False):
                errtext += "Input Error: Building a mixture with a mixture..."
                logger.error(errtext)
                res.update({"error": True,
                        "message": errtext})
                return {"result": res}
            else:
                if backend in ("CP", "COOLPROP"):
                    sub = "&".join([SUBS_P[i][0] for i in sub])
                elif mode_refprop:
                    sub = "&".join([SUBS_P[i][1] for i in sub])
                    if "N/A" in sub:
                        errtext += "Input Error: Not supported substance for REFPROP is detected."
                        logger.error(errtext)
                        res.update({"error": True,
                                    "message": errtext})
                        return {"result": res}
                else:
                    extend_backend_req = True

        # 检查混合组分输入是否均为正数
        if not reduce(lambda acc, x: acc and (x > 0), mixture, True):
            errtext += "Input Error: Building a mixture with a mixture..."
            logger.error(errtext)
            res.update({"error": True,
                    "message": errtext})
            return {"result": res}
        mixture = [i/sum(mixture) for i in mixture]
    else:
        extend_backend_req = True
    
    if not mixture:
        errtext += "Input Error: Can not calculate flashing for pure component."
        logger.error(errtext)
        res.update({"error": True,
                    "message": errtext})
        return {"result": res}

    if type(sub) == str:
        res.update({"components": sub.split("&")})

    if inputType1 == inputType2:
        errtext += "Input Error. Only one input Type [%s] is given." % inputType1
        logger.error(errtext)
        res.update({"error": True,
                    "message": errtext})
        return {"result": res}
    
    if SequenceMatcher(None, inputType1, inputType2).find_longest_match(0, len(inputType1), 0, len(inputType2)).size:
        errtext += "Input Error. Input Type [%s&%s] is the same." % (inputType1, inputType2)
        logger.error(errtext)
        res.update({"error": True,
                    "message": errtext})
        return {"result": res}
        
    if not {inputType1, inputType2}.issubset(ITYPE):
        errtext += "Input Error. Invalid input type combo [%s&%s]." % (inputType1, inputType2)
        logger.error(errtext)
        res.update({"error": True,
                    "message": errtext})
        return {"result": res}
    
    for item in ("H", "S"):
        if item in inputType1 + inputType2:
            errtext += "Warning: Unexpected result due to [%s] using difference Reference point on different backend.\n" % item
            logger.warning(errtext)
            res.update({"warning": True,
                        "message": errtext})
    
    try:
        inputValue1 = float(inputValue1)
        inputValue2 = float(inputValue2)
    except:
        errtext += "Input Error. Invalid values are not numbers."
        logger.error(errtext)
        res.update({"error": True,
                    "message": errtext})
        return {"result": res}
    
    if backend in ("PENGROBINSON", "PENG-ROBINSON", "PR"):
        backend = "PR"
    elif backend in ("CP", "COOLPROP") or not mode_refprop:
        backend = "HEOS"
    elif backend == "REFPROP" and mode_refprop:
        backend = "REFPROP"
    
    
    if extend_backend_req:
        # todo: impletementing of mProp_extend()
        res.update(mProp_extend())
    else:
        sub = cp.AbstractState(backend, sub)
        sub.set_mole_fractions(mixture)
        sub.update(
                **input_construct(
                          inputType1,
                          inputType2,
                          inputValue1,
                          inputValue2
                          )
                )
#       
        Q = sub.keyed_output(getattr(cp, "iQ"))
        T = sub.T()
        P = sub.p()
        rtn = dict()
        for item in outType:
            try:
                rtn.update({
                        item: sub.keyed_output(getattr(cp, OTYPE[item]))
                        })
            except Exception as e:
                errtext += "Calculation Error: Fail to cal [%s] for INFLOW:\n" % item
                errtext += str(e)
                res.update({"warning": True,
                            "message": errtext})
        rtn.update({"Fraction": mixture})
        res.update({
            "IN": rtn,
            "T": T,
            "P": P,
            "Q": Q
            })
        
        if not (0 < Q < 1):
            errtext += "Input Error: INFLOW is single phase"
            res.update({"warning": True,
                        "message": errtext})
            return {"result": res}
        
        for mix in OTYPE_MIX:
            _mixture = None
            sub.set_mole_fractions(mixture)
            try:
                _mixture = getattr(sub, OTYPE_MIX[mix])()
            except Exception as e:
                errtext += "Calculation Error: Fail to cal [%s]:\n" % mix
                errtext += str(e)
                res.update({"warning": True,
                            "message": errtext})
                continue

            sub.set_mole_fractions(_mixture)
            sub.specify_phase(cp.iphase_gas if mix == "VAPFRAC" else cp.iphase_liquid)
            sub.update(cp.PT_INPUTS, P, T)
            
            rtn = dict()
            for item in outType:
                try:
                    rtn.update({
                            item: sub.keyed_output(getattr(cp, OTYPE[item]))
                            })
                except Exception as e:
                    errtext += "Calculation Error: Fail to cal [%s] for INFLOW:\n" % item
                    errtext += str(e)
                    res.update({"warning": True,
                                "message": errtext})
            rtn.update({"Fraction": _mixture})
            res.update({mix: rtn})
                
    if {"message", "warning"} == set(res.keys()):
        errtext += "Fatal Calculation Error: No result calculated!"
        res.update({"warning": True,
                    "message": errtext})
    
    return {"result": res}
    
    