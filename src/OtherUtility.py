'''
Created on 2013/12/20

@author: 10110045
'''
from tkinter import Tk, PhotoImage, Frame, Label, Entry, Button
from tkinter.constants import LEFT
import HttpUtility
import array
import os
import time

def write_file(file_name, data):
    file=open(file_name,"wb")
    try:
        file.write(data)
    except IOError:
        pass
    finally:
        file.close()
        
def write_download_file(httpResponse, fileName, chunk_size=256 , setStatusInfo = None, needStop = None):
    '''write http download file progress'''
    if os.path.isfile(fileName+".tmp"):
        print("Erasing the old temp file...")
        os.remove(fileName+".tmp")
        
    tmpFile=open(fileName+".tmp", "ab+")
    
    totalFileSize=int(httpResponse.info().get_all('Content-Length')[0])
    currentDownloaded=0
    
    while currentDownloaded < totalFileSize:
        if needStop != None and needStop() == True:
            print("Manually stop at downloading file.")
            break
        
        chunk=httpResponse.read(int(chunk_size))
        currentDownloaded+=len(chunk)
        
        # write to file per chunk
        tmpFile.write(chunk)
        
        downloadedPercent=round(100*float(currentDownloaded)/totalFileSize)
        
        print("current downloading:   "+str(downloadedPercent)+" %")
        if setStatusInfo != None:
            setStatusInfo("current downloading:   "+str(downloadedPercent)+" %")
    
    tmpFile.close()
            
    if currentDownloaded != totalFileSize:
        print("The download file lenth didn't meets the expect.")
        return 1
    
    if os.path.isfile(fileName):
        print("Erasing the old file with same name...")
        os.remove(fileName)
    
    os.rename(fileName+".tmp",fileName)
    return 0
    
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
    file_name="Public Relations Strategy.pdf"
    url="http://dl.dropboxusercontent.com/u/48186266/Public%20Relations%20Strategy.pdf"
    
    response=HttpUtility.sendHttpRequest(url, {'Connection': "keep-alive"}, None, None)
    
    write_download_file(response, file_name)