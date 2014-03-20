# -*- coding: utf-8 -*-
'''
Created on 2014/2/25
┌┬┐├┼┤└┴┘─│
                          main
                            │
                        (invoke)
                            │
        ┌─────────────ControlThread─────────────┐
        │              ^    │    │              │
     update            │    │    │         check status
        │           notify  │    │              │
        V              │    │ notify            V
    DialogThread ──────┘    │    └──────────> HTTPthread(workThread)
           ^                │                   ^
           └────────signal terminate────────────┘    
    
    "notify" include "teminate" and "set url"
    
    the indeed download code is commented for testing conveniently.
    
    unfinishied job:
                       1. Exception _tkinter.TclError: 'out of stack space (infinite loop?)' in <bound method StringVar.__del__ of <tkinter.StringVar object at 0x0216ACD0>> ignored
                        
                       2. dialog terminate progress(done)
                       
                       3. percentage of downloading(done)
                       
                       4. asking save file dialog
                        
                        
    test file url: "http://rapidgator.net/file/bf6293fc58898b2bacbd4b9b6e4bff8d/Android_Security.zip.html"
@author: Nick Chen (fscnick@hotmail.com)
'''

from tkinter import *
import ControlThread
import DialogThread
import HTTPthread
import time

        
if __name__ == '__main__':
    controlThread=ControlThread.ControlThread()
    controlThread.start()
    
    ''' testing procedure '''
    '''httpThread = HTTPthread.HTTPthread()
    httpThread.setURL("http://rapidgator.net/file/bf6293fc58898b2bacbd4b9b6e4bff8d/Android_Security.zip.html")
    httpThread.start()
    while(True):
        time.sleep(0.5)
        op=httpThread.getOP()
        
        
        if op < 0:
            print(str(httpThread.getOP())+" : "+httpThread.getStatusInfo())
            if "Error" in httpThread.getStatusInfo():
                break
            httpThread.goToNextOP()
            httpThread.run()
        else:
            print(str(httpThread.getOP())+" : "+httpThread.getStatusInfo())'''