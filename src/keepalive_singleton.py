# -*- coding: utf-8 -*-
'''
Created on 2013/12/18

@author: 10110045
'''
import urllib.request
from keepalive import HTTPHandler


class keepalive_singleton(HTTPHandler):
    '''
    classdocs
    '''

    _instance = None
        
    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance=super(keepalive_singleton, cls).__new__(cls, *args, **kwargs)
        return cls._instance     
    
    
if __name__ == '__main__':
    s1=keepalive_singleton()
    s2=keepalive_singleton()
    if(id(s1)==id(s2)):
        print ("Same")
    else:
        print ("Different")