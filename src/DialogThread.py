'''
Created on 2014/2/26

@author: 10110045
'''
from tkinter import Tk, Frame, Label, Entry, Button, messagebox, StringVar
import threading
import time

class DialogThread(threading.Thread):
    '''mantain dialog'''
    def __init__(self, controlThread=None):
        threading.Thread.__init__(self)

        self.dialogNeedChange=False
        self.dialogType=0
        
        self.dialog=None
        
        self.controlThread=controlThread
        
        self.URL_DIALOG=1
        self.INFO_DIALOG=2
        self.TERMINATE=100
        
        self.looptime=0.05      # this loop time must less than loop time in ControlThread for better responsivity
        
    def updateInfo(self, info):
        if self.dialogType == 2:
            self.dialog.frame.updateInfo(info)
        else:
            print("Not a valid dialog.")
        
    def setDialogChange(self, dialogType):
        if dialogType != self.dialogType:
            self.dialogNeedChange=True
            self.dialogType=dialogType
            print("dialogType set success!")
        else:
            print("dialogType is the current type.")
            
    def run(self):
        print("DialogThread start!!!")
        self.setDialogChange(self.URL_DIALOG)
        while(True):
            if self.dialogNeedChange == True and self.dialogType == 1:
                ''' invoke UrlDialog '''
                if self.dialog != None :
                    ''' erase old dialog '''
                    self.dialog.closeDialog()
                    self.dialog = None
                
                self.dialog=UrlDialog(self.controlThread)
                self.dialog.start()
                self.dialogNeedChange=False
                continue
                
            if self.dialogNeedChange == True and self.dialogType == 2:
                ''' invoke InfoDialog '''
                if self.dialog != None :
                    ''' erase old dialog '''
                    self.dialog.closeDialog()
                    self.dialog = None
                    
                self.dialog=InfoDialog()
                self.dialogNeedChange=False
                self.dialog.start()
                continue
            
            if self.dialogNeedChange == True and self.dialogType == self.TERMINATE:
                print("DialogThread terminate.")
                self.dialogNeedChange=False
                if self.dialog != None :
                    ''' erase old dialog '''
                    self.dialog.closeDialog()
                    self.dialog = None
                break
            
            time.sleep(self.looptime)
            
class UrlDialog(threading.Thread):
    def __init__(self, thread=None):
        threading.Thread.__init__(self)
        self.thread=thread
        self.dialogRoot=Tk()
        
        self.frame=GetUrlFrame(self.dialogRoot, self.thread)
        
    def closeDialog(self):
        self.dialogRoot.quit()
        self.dialogRoot.destroy()
        print("UrlDialog is terminated.")
 
    def run(self):
        
        print("UrlDialog is show up.")
        self.dialogRoot.mainloop()
                

class GetUrlFrame(Frame):
    def __init__(self, master=None, thread=None):
        Frame.__init__(self, master)
        self.controlThread=thread
        
        self.url=""
        self.urlFilter="rapidgator.net"

        self.grid()
        
        self.createWidgets()
        
        
        
    def createWidgets(self):
        self.inputText = Label(self)
        self.inputText["text"] = "URL:"
        self.inputText.grid(row=0, column=0)
        
        self.inputField = Entry(self)
        self.inputField["width"] = 50
        self.inputField.grid(row=0, column=1, columnspan=6)
        
        self.submitBtn = Button(self, command=self.clickSubmitBtn)
        self.submitBtn["text"] = "Submit"
        self.submitBtn.grid(row=0, column=7)
        

    def clickSubmitBtn(self):
        if self.urlFilter in self.inputField.get():
            self.url=self.inputField.get()

            self.controlThread.setFileURL(self.url)
            
            self.quit()
            
        else:
            messagebox.showerror(
                        "Url error!",
                        "Not Support host site!"
                                  )
        
        
    def getSubmitURL(self):
        return self.url
    
    
class InfoDialog(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self) 
        self.dialogRoot=Tk()
        self.frame=InfoFrame(self.dialogRoot)
        
    def closeDialog(self):
        self.dialogRoot.quit()
        self.dialogRoot.destroy()
        print("InfoDialog is terminated.")
        
    def run(self):
        
        print("InfoDialog is show up.")
        self.dialogRoot.mainloop()
    
class InfoFrame(Frame):
    def __init__(self,master=None):
        Frame.__init__(self, master)
        
        self.stringVar=StringVar()
        
        self.grid()
        self.createWidgets()
        
    def createWidgets(self):
        self.inputText=Label(self)
        #self.inputText['text']=self.workThread.getStatusInfo()
        self.inputText['textvariable']=self.stringVar
        self.inputText["width"] = 50
        self.inputText.grid(row=0, column=0, columnspan=6)
        
        
        self.cancelBtn = Button(self)   # need to implement
        self.cancelBtn["text"] = "Cancel"
        self.cancelBtn.grid(row=0, column=6)
        
    def updateInfo(self, str):
        self.stringVar.set(str)

        
if __name__ == '__main__':
    thread=DialogThread()
    thread.start()
    print("Start....")
    
    time.sleep(3)
    print("UrlDialog")
    thread.setDialogChange(1)
    
    time.sleep(3)
    print("InfoDialog")
    thread.setDialogChange(2)
    
    for i in range(10):
        time.sleep(1)
        thread.updateInfo(str(i))
        print(str(i))