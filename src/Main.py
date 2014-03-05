# -*- coding: utf-8 -*-
'''
Created on 2014/2/25

    ┌gui         <─┐
    │              │(update ui)
main┼control thread┤
    │              │(check status)
    └work thread <─┘
    
@author: 10110045
'''

from tkinter import *
import ControlThread
import DialogThread
import HTTPthread
import time

        
if __name__ == '__main__':
    controlThread=ControlThread.ControlThread()
    controlThread.start()
    
    
    '''httpThread=HTTPthread.HTTPthread()
    dialogThread=DialogThread.DialogThread(httpThread)
    controlThread=ControlThread.ControlThread(dialogThread, httpThread)
    controlThread.start()'''
    #dialog.retrieveURL()
    
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