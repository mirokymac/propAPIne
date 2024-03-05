# -*- coding: utf-8 -*-
"""
Created on Tue Jul 16 13:55:19 2019

@author: Zihao.MAI
"""


from re import findall as refindall, subn as rereplace

__all__ = ["string_to_dict"]

def string_to_dict(text: str, rtn_on_fail=None) -> dict:
    if type(text) != str:
        return rtn_on_fail
    
    key_value = refindall("[a-zA-Z 0-9\-\:\_]+", text)

    if not key_value: # not any key-value pair
        return rtn_on_fail
    else:
        ret = dict()
        for item in key_value:
            tm = list(map(lambda x: x.strip(), item.split(":")))
            if len(tm) == 2:
                ret.setdefault(*tm)
            elif tm[0].upper() == "REFPROP":
                ret.setdefault("backend", "REFPROP")
            else:
                continue
        return ret

def string_to_list(text: str, rtn_on_fail=None) -> dict:
    if type(text) != str:
        return rtn_on_fail
    
    tolist = rereplace('[\[\]]|\s', '', text)[0]
    
    if not tolist:
        return rtn_on_fail
    else:
        tolist = tolist.split(',')
        return dict(tolist)

if __name__ == "__main__":
    print(string_to_dict("REFPROP", None))
    print(string_to_dict("test:string"))
