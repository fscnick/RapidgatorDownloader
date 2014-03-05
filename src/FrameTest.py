'''
Created on 2014/2/27

@author: 10110045
'''
from tkinter import Tk, Frame, Button
import threading
import time

class testThread(threading.Thread):
    def __init__(self, dialog, frame, frame2):
        super().__init__()
        self.dialog=dialog
        self.frame=frame
        self.frame2=frame2
        frame.grid(row=0, column=0, sticky="nsew")
        frame2.grid(row=0, column=0, sticky="nsew")
        
        
        
        
    def run(self):
        print("In thread.")
        self.button = Button(
            frame, text="Hellow", fg="red", command=say_hi
            )
        self.button.grid(row=0, column=0)
        
        qBtn = Button(frame2, text="QUIT", command=frame2.quit)
        qBtn.grid(row=0, column=0)
        
        self.dialog.mainloop()
        #self.frame.destroy()
        print("QUIT")

def say_hi(self):
        print ("hi there, everyone!")

if __name__ == '__main__':
    dialogRoot=Tk()
    frame=Frame(dialogRoot)
    
    
    frame2=Frame(dialogRoot)
    
    thread=testThread(dialogRoot, frame, frame2)
    thread.start()
    
    print("Wait")
    time.sleep(10)
    #frame.destroy()
    
    print("change")
    frame.tkraise(frame2)
    
    print("done")