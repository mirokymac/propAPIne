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
from json import dumps as dumps_json
import logging
#from os.path import isfile, getsize
#import pickle
import re
import CoolProp.CoolProp as cp
from . import dippr_functions

from ..util.load_csv import Load_csv, Key

# 初始化环境
logger = logging.getLogger(__name__)
# 输入输出变量列表
# ps1: 不建议H和S作为intype，因为不同的backend使用的reference不一样
loader = Load_csv(r'./common/CoolProp.AbstractState.IO.csv')

tmp_SIcal_types = loader(Key(0))
tmp_io_flags = loader(Key(2))
tmp_qc_flags = loader(Key(3))
tmp_ABcal_types = loader(Key(4))

OTYPE = dict(zip(tmp_SIcal_types, tmp_ABcal_types))
ITYPE = frozenset([i for i, j in zip(tmp_SIcal_types, tmp_io_flags) if "I" in j])
QCTYPE = frozenset([i for i, j in zip(tmp_SIcal_types, tmp_qc_flags) if j])
# 2024-03-05 增加fugacity，fugacity_coeff和K
OTYPE_MIX = {
        "VAPFRAC": "mole_fractions_vapor",
        "LIQFRAC": "mole_fractions_liquid"
        }
OTYPE_PHASE = {
        "FUGACITY": "fugacity",
        "FUGACITYCOEFF": "fugacity_coeff",
        "K": "K"
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

TYPE_PATTERN = r"[A-Za-z0-9\_]+"
MIXTURE_PATTERN = r"[A-Z0-9]+\s?\:\s?\-?\d+\.?\d*"

del loader, tmp_ABcal_types, tmp_io_flags, tmp_qc_flags, tmp_SIcal_types
# 物料字典
# CoolProp 与 Refprop部分
loader = './common/fluidlist.json'
with open(loader, "r") as loader:
    SUBS_P = load_json(loader)

# EOS 扩展部分
loader = './common/EOS_substance_list.csv'
with open(loader, "r") as loader:
    SUBS_EOS = loader.readlines()
SUBS_EOS = SUBS_EOS[0].split(",")
SUBS_EOS = set(SUBS_EOS)
#SUBS_M_CP = dict()
#SUBS_M_REFPROP = dict()

# DIPPR 扩展温度相关参数字典
loader = './common/DIPPR.json'
with open(loader, "r") as loader:
    DIPP_PARAM = load_json(loader)
DIPP_CONV = {"CONDUCTIVITY":"TC", "V":"V"}

# 相态列表
PHASE = ("gas", "liquid", "not_imposed", "supercritical", "supercritical_gas", "supercritical_liquid", "twophase")

# 尝试载入REFPROP
PATH_TO_REFPROP = "./refprop/"

cp.set_config_string(5, PATH_TO_REFPROP)
try:
    cp.PropsSI('H', 'P', 101325, 'Q', 1, 'REFPROP::Water')
    REFPROP_READY = True
    logger.critical("Refprop loaded.")
except:
    REFPROP_READY = False
    logger.critical("Refprop failed to load. Refprop is disableed.")

# 尝试载入扩展EOS物料
loader = "./common/addition_substance_EOS.json"
with open(loader, "r") as loader:
    loader = load_json(loader)
DIPPR_NAME_CONV = dict([i["name"], i["aliases"][0]] for i in loader)

loader = dumps_json(loader)
cp.set_debug_level(100)
cp.add_fluids_as_JSON("PR", loader)
try:
    cp.PropsSI('H', 'P', 101325, 'Q', 1, 'SRK::SIH4')
    EXEOS_READY = True
    logger.critical("Extend EOS loaded.")
except:
    EXEOS_READY = False
    logger.critical("Extend EOS failed to load.")
cp.set_debug_level(0)

del loader


def mProp(sub:str,
          outType:list,
          inputType1:str,
          inputValue1:float,
          inputType2:str,
          inputValue2:float,
          backend:str="CP",
          preferedPhase:str="")-> dict:
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
            
    # 2020-6-5 增加额外EOS组分处理
    # 2024-03-05 调整位置，减少不必要计算
    sub, mixture, backend, _res = subsHandler(sub, backend, mode_refprop)
    if "error" in _res:
        return {"result": _res}
    errtext += _res.get("message", "")
    res.update(_res)
    del _res
    
    
    # 转换输出关键字为list
    if type(outType) != list:
        if type(outType) == str:
            outType = re.findall(TYPE_PATTERN, outType)
        else:
            errtext += f"Input Error: Invalid output type: {outType}\n" 
            logger.error(errtext)
            res.update({"error": True,
                        "message": errtext})
            return {"result": res}

    # 将所有文本输入转化为大写
    inputType1 = inputType1.upper()
    inputType2 = inputType2.upper()
    outType = set(list(map(str.upper, outType)))
    
    # inType checks
    if not outType.issubset(QCTYPE):
        # check if the same input
        if inputType1 == inputType2:
            errtext += "Input Error. Only one input Type [%s] is given.\n" % inputType1
            logger.error(errtext)
            res.update({"error": True,
                        "message": errtext})
            return {"result": res}

        # check alias, if the input is the same or not
        if SequenceMatcher(None, inputType1, inputType2).find_longest_match(0, len(inputType1), 0, len(inputType2)).size:
            errtext += "Input Error. Input Type [%s&%s] is the same.\n" % (inputType1, inputType2)
            logger.error(errtext)
            res.update({"error": True,
                        "message": errtext})
            return {"result": res}

        if not {inputType1, inputType2}.issubset(ITYPE):
            errtext += "Input Error. Invalid input type combo [%s&%s].\n" % (inputType1, inputType2)
            logger.error(errtext)
            res.update({"error": True,
                        "message": errtext})
            return {"result": res}

    for item in ("H", "S"):
        if item in inputType1 + inputType2:
            errtext += "Warning: Unexpected result may occur, due to [%s] using difference Reference point on different backend.\n" % item
            logger.warning(errtext)
            res.update({"warning": True,
                        "message": errtext})

    try:
        inputValue1 = float(inputValue1)
        inputValue2 = float(inputValue2)
    except:
        errtext += "Input Error. Invalid value. Values are not numbers\n."
        logger.error(errtext)
        res.update({"error": True,
                    "message": errtext})
        return {"result": res}

    # 处理输出项
    # 构建闪蒸计算输出
    flash = set(OTYPE_MIX.keys()).union(set(OTYPE_PHASE.keys()))
    flash &= outType
    outType -= flash
    # 如果将进行闪蒸计算而目标组成不是混合物
    if not mixture and flash:
        flash = []
        errtext += "Input Error. Not support flash calculation for predefine mixture or pure component.\n"
        logger.error(errtext)
        res.update({"error": True,
                    "message": errtext})
        return {"result": res}

    # 构建组合输出
    for item in set(OTYPE_COMBO.keys()).intersection(outType):
        outType.remove(item)
        outType = outType.union(OTYPE_COMBO[item])

    # 构建普通输出
    if outType - set(map(str.upper, OTYPE.keys())):
        errtext += "Warning: Unsupported Output Type keywords: %s \n" % list(outType - set(OTYPE.keys()))
        logger.warning(errtext)
        res.update({"warning": True,
                    "message": errtext})

    outType = outType.intersection(OTYPE.keys())

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

    # 增加相态指定功能
    if preferedPhase != "" and preferedPhase.lower() in PHASE:
        sub.specify_phase(getattr(cp, "iphase_" + preferedPhase.lower())) 

    for item in outType:
        if backend not in ("REFPROP", "HEOS") and item in ("CONDUCTIVITY", "V") and not mixture:
            res.update(dippr_wraper(sub, item))
            if "error" in res:
                return {"result": res}
        else:
            try:
                res.update({
                        item: sub.keyed_output(getattr(cp, OTYPE[item]))
                        })
            except Exception as e:
                errtext += "Calculation Error: Fail to cal [%s]:\n" % item
                errtext += str(e)
                res.update({"warning": True,
                            "message": errtext})

    q = sub.Q()
    for item in flash:
        if q < 0:
            errtext += "flash calculation can not perform on singularity phase.\n"
            res.update({"error": True,
                        "message": errtext})
            return {"result": res}
        
        try:
            if "FUGA" in item:
                # abstract.fugacity({number}) to get fugacity of substances
                res.update({
                    item: [getattr(sub, OTYPE_PHASE[item])(i) for i in range(len(mixture))]
                })
            elif item == "K":
                sub.specify_phase(cp.iphase_twophase)
                liq = sub.mole_fractions_liquid()
                vap = sub.mole_fractions_vapor()
                ks = list()
                for l, v in zip(liq, vap):
                    if l == 0:
                        ks.append(0)
                    else:
                        ks.append(v/l)
                res.update({item: ks})
            else:
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
            
    # 2020-6-5 增加额外EOS组分处理
    sub, mixture, backend, _res = subsHandler(sub, backend, mode_refprop)
    if "error" in _res:
        return {"result": _res}
    errtext += _res.get("message", "")
    res.update(_res)
    del _res
    
    # 将所有文本输入转化为大写
    inputType1 = inputType1.upper()
    inputType2 = inputType2.upper()
    
    if inputType1 == inputType2:
        errtext += "Input Error. Only one input Type [%s] is given.\n" % inputType1
        logger.error(errtext)
        res.update({"error": True,
                    "message": errtext})
        return {"result": res}
    
    if SequenceMatcher(None, inputType1, inputType2).find_longest_match(0, len(inputType1), 0, len(inputType2)).size:
        errtext += "Input Error. Input Type [%s&%s] is the same.\n" % (inputType1, inputType2)
        logger.error(errtext)
        res.update({"error": True,
                    "message": errtext})
        return {"result": res}
        
    if not {inputType1, inputType2}.issubset(ITYPE):
        errtext += "Input Error. Invalid input type combo [%s&%s].\n" % (inputType1, inputType2)
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
        errtext += "Input Error. Invalid values. Values are not numbers.\n"
        logger.error(errtext)
        res.update({"error": True,
                    "message": errtext})
        return {"result": res}
    
    # 2020-6-5 增加额外EOS组分处理
    # 2024-03-05 调整位置，减少不必要计算
    # sub, mixture, backend, _res = subsHandler(sub, backend, mode_refprop)
    # if "error" in _res:
    #     return {"result": _res}
    # errtext += _res.get("message", "")
    # res.update(_res)
    # del _res
    if not mixture:
        errtext += "Input Error: Can not calculate flashing for pure component.\n"
        logger.error(errtext)
        res.update({"error": True,
                    "message": errtext})
        return {"result": res}
    if type(sub) == str:
        res.update({"components": sub.split("&")})
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
        errtext += "Input Error: INFLOW is single phase\n"
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
    

def subsHandler(sub:str, backend:str, mode_refprop=False):
    res = dict()
    errtext = ""

    sub = sub.upper()
    backend = backend.upper()
    # print(mode_refprop, backend)

    # 检查是否混合物
    mixture = re.findall(MIXTURE_PATTERN, sub)
    # 检查是否指定backend
    # 未指定或错误则使用CoolProp
    if mode_refprop and backend == "REFPROP":
        backend = "REFPROP"
    elif backend in ("PENGROBINSON", "PENG-ROBINSON", "PR"):
        backend = "PR"
    elif backend in ("SRK", "S-RK"):
        backend = "SRK"
    else:
        if backend not in ("CP", "COOLPROP", "HEOS"):
            errtext += "Input Warning: Unsupported backend, using CoolProp as default.\n"
            res.update({
                "warning": True,
                "message": errtext
                        })
            logger.warning(errtext)
        backend = "HEOS"
    
    # 组分分析：

    # 1. mixtur?
    if mixture:
        sub = list(map(lambda x: x.split(":")[0], mixture))
        mixture = list(map(lambda x: float(x.split(":")[1]), mixture))
    else:
        sub = [sub]
    _sub = sub # substance list backup

    # which substance dict?
    # + refprop or coolprop?
    #  + building mixture from mixture?
    #   + exit
    #  + refprop name change
    #   -or HEOS HEOS name change
    # + EOS
    # - ERROR
    if (not (set(sub) - set(SUBS_P.keys()))) and backend in ("HEOS", "REFPROP"):
        if mixture and reduce(lambda acc, x: SUBS_P[x][2] or acc, sub, False):
            errtext += "Input Error: unable to build a mixture with a mixture.\n"
            logger.error(errtext)
            res.update({"error": True,
                    "message": errtext})
            return (None, None, None, res)

        sub = "&".join([SUBS_P[i][1] for i in sub]) if backend == "REFPROP" \
              else "&".join([SUBS_P[i][0] for i in sub])

        if "N/A" in sub:
            sub = "&".join([SUBS_P[i][0] for i in _sub])
            errtext += "Input Warning: Unsupported substances for Refprop, using CoolProp as default.\n"
            res.update({
                "warning": True,
                "message": errtext
                        })
            logger.warning(errtext)
            backend = "HEOS"

    elif (not set(sub) - SUBS_EOS) and EXEOS_READY:
        sub = "&".join(sub)
        if backend not in ("SRK", "PR"):
            errtext += "Input Warning: Extended substance is given, Using SRK backend instead.\n"
            res.update({
                "warning": True,
                "message": errtext
                        })
            logger.warning(errtext)
            backend = "SRK"
    else:
        errtext += f"Input Error: Unsupported substance in INPUT: {', '.join(sub)}\n"
        logger.error(errtext)
        res.update({
            "error": True,
            "message": errtext
                    })
        return (None, None, None, res)

    # 3. 检查混合组分输入是否均为正数&归一化
    if mixture:
        if not reduce(lambda acc, x: acc and (x > 0), mixture, True):
            errtext += "Input Error: Minus value in mixture fraction.\n"
            logger.error(errtext)
            res.update({"error": True,
                    "message": errtext})
            return (None, None, None, res)
        mixture = [i/sum(mixture) for i in mixture]

    return (sub, mixture, backend, res)

def dippr_wraper(sub:cp.AbstractState, item:str)->dict:
    sub_name = sub.fluid_names()[0]
    Pcc = sub.keyed_output(getattr(cp, OTYPE["P"]))
    Tar = sub.keyed_output(getattr(cp, OTYPE["T"]))
    Tcc = cp.PropsSI("T", "Q", 1, "P", Pcc, "SRK::" + sub_name)
    item = DIPP_CONV[item] + ("V" if Tar >= Tcc else "L")
    sub_name = DIPPR_NAME_CONV[sub_name]

    errtext = ""
    res = dict()
    try:
        func = DIPP_PARAM[sub_name][item]["func"]
        if func == "0":
            raise ValueError
    except (ValueError, KeyError, IndexError) as e:
        errtext += "Calculation Error: DIPPR function for [%s] not implete:\n" % sub_name
        errtext += str(e)
        res.update({"error": True,
                    "message": errtext})
    finally:
        try:
            res.update({
                item: getattr(dippr_functions, "function" + func)(DIPP_PARAM[sub_name][item]["coef"])(Tar)
                })
        except Exception as e:
            errtext += "Calculation Error: Fail to cal [%s]:\n" % item
            errtext += str(e)
            res.update({"warning": True,
                        "message": errtext})
    return res
