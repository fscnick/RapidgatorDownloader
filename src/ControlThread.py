# -*- coding: utf-8 -*-
'''
Created on 2014/2/26

@author: 10110045
'''
import DialogThread
import HTTPthread
import Main
import threading
import time

class ControlThread(threading.Thread):
    '''
    controller thread is used for checking work thread status and update dialog
    '''


    def __init__(self,dialogThread = None, workThread=None):
        '''
        Constructor
        '''
        super().__init__()
        
        self.fileUrl=None   # The download file url that need be forwarded to httpThread
        
        if dialogThread == None:
            self.dialogThread=DialogThread.DialogThread(self)
        else:
            self.dialogThread=dialogThread
            
        if workThread == None:
            self.workThread=HTTPthread.HTTPthread()
        else:
            self.workThread=workThread
        
        self.stopFlag=False
        
        self.loopTime=0.2
        
    def restartWorkThread(self):
        status=self.workThread.getHttpStatus()
        
        self.workThread=HTTPthread.HTTPthread()
        self.workThread.setHttpStatus(status)
    
        self.workThread.start()
        
    def setFileURL(self, fileUrl):
        self.fileUrl=fileUrl
        
    def getFileURL(self):
        return self.fileUrl
    
    def setStop(self):
        self.stopFlag=True
        
    def run(self):
        ''' start dialog and httpThread '''
        print("ControlThread start")
        
        self.workThread.start()
        
        self.dialogThread.start()
        
        
        while (True):
            time.sleep(self.loopTime)
            
            if self.stopFlag == True:
                ''' recieve a stop signal'''
                self.dialogThread.setDialogChange(self.dialogThread.TERMINATE)
                self.workThread.setStop()
                break
            
            op=self.workThread.getOP()
            
            if op == 0 and self.fileUrl != None:
                self.workThread.setURL(self.getFileURL())
                self.workThread.goToNextOP()
                
                self.restartWorkThread()
                
                self.dialogThread.setDialogChange(self.dialogThread.INFO_DIALOG)
                continue
                
            
            if op < 0:
                '''current job is done'''
                info=self.workThread.getStatusInfo()
                
                if "Error" in info:
                    '''some error occur'''
                    self.dialogThread.setDialogChange(self.dialogThread.INFO_DIALOG)
                    time.sleep(self.loopTime)
                    self.dialogThread.updateInfo(info)
                
                else:
                    ''' continue to next job state'''
                    
                    if op == -1:
                        self.dialogThread.setDialogChange(self.dialogThread.INFO_DIALOG)
                        print("set dialog change Info")
                        self.workThread.goToNextOP()
                        print("goto OP 2")
                        self.restartWorkThread()
                        continue
                    
                    elif op == -2:
                        self.workThread.goToNextOP()
                        print("goto OP 3")
                        self.restartWorkThread()
                        continue
                    
                    elif op == -3:
                        self.workThread.goToNextOP()
                        print("goto OP 4")
                        self.restartWorkThread()
                        continue
                    
                    elif op == -4:
                        self.workThread.goToNextOP()
                        print("goto OP 5")
                        self.restartWorkThread()
                        continue
                    
                    elif op == -5:
                        self.workThread.goToNextOP()
                        print("goto OP 6")
                        self.restartWorkThread()
                        continue
                    
                    elif op == -6:
                        print("download finish...")
                        self.dialogThread.updateInfo(self.workThread.getStatusInfo())
                        continue
                        
            else:
                '''update current status'''
                rr=self.dialogThread.updateInfo(self.workThread.getStatusInfo())
                if rr == 0:
                    print("control set stop")
                    self.setStop()
                        
            