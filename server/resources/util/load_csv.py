# -*- coding: utf-8 -*-

import csv
import logging

logger = logging.getLogger(__name__)

class Load_csv:
    def __init__(self, path, render=None):
        self.path = path
        self.file = open(self.path, 'r')
        self.csv_cursor = self._csv_reload()
        if render:
            self.render = render
        
    def _csv_reload(self):
        try:
            self.file.close()
        except Exception as e:
            logger.error(str(e))
        self.file = open(self.path, 'r')
        return csv.reader(self.file)
    
    def __call__(self, render_object=None, path=None):
        """
        using render_object to define the shape of each row
        render_object: 
        """
        file = None
        if path:
            file = open(path, 'r')
            csv_cursor = csv.reader(open(self.path, 'r'))
        else:
            csv_cursor = self.csv_cursor = self._csv_reload()
        if not render_object and not self.render:
            return tuple()
            
        rtn = tuple()
        self.render = render_object
        if not render_object:
            return tuple()
        if isinstance(render_object, str):
            pass
        elif isinstance(render_object, tuple):
            for iteritem in csv_cursor:
                temp = tuple()
                for item in render_object:
                    if isinstance(item, Key):
                        temp += (item.format(iteritem), )
                    else:
                        temp += (item, )
                rtn += (temp, )
        elif isinstance(render_object, list):
            for iteritem in csv_cursor:
                temp = list()
                for item in render_object:
                    if isinstance(item, Key):
                        temp.append(item.format(iteritem))
                    else:
                        temp.append(item)
                rtn += (temp, )
        elif isinstance(render_object, dict):
            for iteritem in csv_cursor:
                temp = dict()
                for key, value in render_object.items():
                    if isinstance(key, Key):
                        key = key.format(iteritem)
                    if isinstance(value, Key):
                        value = value.format(iteritem)
                    temp.update({key: value})
                rtn += (temp, )
        elif isinstance(render_object, Key):
            for iteritem in csv_cursor:
                rtn += (render_object.format(iteritem), )
                
        if file:
            file.close()
            
        return rtn
    
    def __delete__(self):
        del self.csv_cursor
        try:
            self.file.close()
        except Exception as e:
            logger.error(str(e))
        
class Key:
    """
    Return specific indexed item from each row of an iterable object.
    If the index number is larger than the length of the a row, then return the last object of the row.
    """
    def __init__(self, index=0, func=None):
        self.index = index
        self.func = func
        
    def format(self, iterable):
        try:
            if self.func:
                    return self.func(iterable[self.index])
            else:
                return iterable[self.index]
        except IndexError as e:
            logger.error(e)
            if len(iterable) > 0:
                logger.error('Setting return value to the last item instead.')
                return iterable(len(iterable) - 1)
            else:
                logger.error('Seems an empty list')
                return None
        except Exception as e:
            logger.error(e)
            return None
    
        
class Key:
    """
    Return specific indexed item from each row of an iterable object.
    If the index number is larger than the length of the a row, then return the last object of the row.
    """
    def __init__(self, index=0, func=None):
        self.index = index
        self.func = func
        
    def format(self, iterable):
        try:
            if self.func:
                    return self.func(iterable[self.index])
            else:
                return iterable[self.index]
        except IndexError as e:
            logger.error(e)
            if len(iterable) > 0:
                logger.error('Setting return value to the last item instead.')
                return iterable(len(iterable) - 1)
            else:
                logger.error('Seems an empty list')
                return None
        except Exception as e:
            logger.error(e)
            return None


if __name__ == "__main__":
    loader = Load_csv("..\..\common\CoolProp.PropsSI.IO.csv")
    print(loader(Key(0)))