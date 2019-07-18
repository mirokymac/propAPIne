# -*- coding: utf-8 -*-
"""
Created on Tue Jul 16 13:55:19 2019

@author: Zihao.MAI
"""


from re import findall as refindall

__all__ = ["string_to_dict"]

def string_to_dict(text: str, rtn_on_fail=None) -> dict:
    if type(text) != str:
        return rtn_on_fail
    
    key_value = refindall("[a-zA-Z 0-9\-\:\_]+", text)
    
    if not key_value:
        return rtn_on_fail
    else:
        key_value = list(map(
                lambda x: list(map(
                        lambda y: y.strip(),
                        x.split(":")
                        )),
                key_value
                ))
        return dict(key_value)