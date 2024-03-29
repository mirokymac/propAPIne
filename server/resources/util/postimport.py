# -*- coding: utf-8 -*-
"""
Created on Fri Apr 20 22:00:41 2018

from PYCookBook.Chapter10.12
@author: Zihao.MAI
"""

import importlib
import sys
from collections import defaultdict

_post_import_hooks = defaultdict(list)

class PostimportFinder:
    def __init__(self):
        self._skip = set()
        
    def find_module(self, fullname, path=None):
        if fullname in self._skip:
            return
        self._skip.add(fullname)
        return PostImportLoader(self)
    
class PostImportLoader:
    def __init__(self, finder):
        self._finder = finder
    
    def load_module(self, fullname):
        importlib.import_module(fullname)
        module = sys.modules[fullname]
        for func in _post_import_hooks[fullname]:
            func(module)
        self._finder._skip.remove(fullname)
        return module
    
def when_imported(fullname):
    def decorate(func):
        if fullname in sys.modules:
            func(sys.modules[fullname])
        else:
            _post_import_hooks[fullname].append(func)
        return func
    return decorate

sys.meta_path.insert(0, PostimportFinder())