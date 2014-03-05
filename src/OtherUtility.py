'''
Created on 2013/12/20

@author: 10110045
'''
import time
from tkinter import Tk, PhotoImage, Frame, Label, Entry, Button
from tkinter.constants import LEFT

def write_file(file_name, data):
    file=open(file_name,"wb")
    try:
        file.write(data)
    except IOError:
        pass
    finally:
        file.close()
        

def count_down_timer(secs):
    for left_time in range(secs+1, 0, -1):
            print("Remaining: ", left_time)
            time.sleep(1)
            
class captcha_dialog():
    def __init__(self, img_file):
        self.captcha_ans=""
        if img_file == None:
            return
        
        self.show_captcha(img_file)
        
        
    def get_captcha_ans(self):
        return self.captcha_ans    
        
        
    def show_captcha(self,img_file):
        dialogRoot = Tk()
        dialogRoot.title("Input text.")
    
        img = PhotoImage(file=img_file)
    
        frame = Frame(dialogRoot)
    
        imal = Label(frame, image=img)
        imal.pack()
    
        label = Label(frame)
        label['text'] = "Your Input:"
        label.pack(side=LEFT)
    
        inputEntry = Entry(frame)
        inputEntry["width"] = 50
        inputEntry.pack(side=LEFT)
    
        def getInputText():
            '''callback of button'''
            # global inputEntry, dialogRoot
            if inputEntry.get().strip() == "":
                print("Please enter a message.")
            else:
                self.captcha_ans = inputEntry.get().strip()
                dialogRoot.destroy()

    
        button = Button(frame, text="Submit", command=getInputText)
        button.pack(side=LEFT)
    
        frame.pack()
        dialogRoot.mainloop()
if __name__ == '__main__':
    pass