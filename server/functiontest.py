# -*- coding: utf-8 -*-
"""
Created on Mon Jul 15 17:52:29 2019

@author: Zihao.MAI
"""

import resources.porting.prop as prop
from pprint import pprint as print

#print(prop.mProp("water", "D", "T", 276.0, "P", 101325.0))
#print(prop.mProp("water", "D,H,S", "T", 276.0, "P", 101325.0))
#print(prop.mProp("water", "D,H,HEAT", "T", 276.0, "P", 101325.0))
#print(prop.mProp("[OXYGEN:21, NITROGEN:79]", "D,H,A", "T", 276.0, "P", 101325.0))
#print(prop.mProp("[OXYGEN:21, NITROGEN:79]", "D,H,A", "T", 276.0, "P", 101325.0, "REFPROP"))
#
print(prop.flasher("[OXYGEN:21, NITROGEN:79]", "Q", 0.5, "P", 101325.0))
print(prop.flasher("[OXYGEN:21, NITROGEN:79]", "Q", 0.3, "P", 101325.0, "REFPROP"))

print(prop.flasher("[OXYGEN:21, NITROGEN:70, ARGON:1]", "Q", 0.3, "P", 101325.0, "REFPROP"))