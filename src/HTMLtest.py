# -*- coding: utf-8 -*-
'''
Created on 2013/6/30

@author: nick
'''
from _pyio import StringIO
from random import randrange
from tkinter import Tk, PhotoImage, Frame, Label, Entry, Button
from tkinter.constants import LEFT
import HttpUtility
import OtherUtility
import ParserUtility
import http
import http.cookiejar
import io
import json
import random
import re
import sys
import time
import urllib



DEBUG = True
captcha_response=""
    
def getChallenge(jsContent):
    m = re.search("", jsContent)
    # http= urllib.request.urlopen("http://api.solvemedia.com/papi/_challenge.js?k="+)
    
def getFwv():
    fwv = ""
    fwv += "fwv/"
    for i in range(6):
        if random.random() > 0.2:
            fwv += str(chr(randrange(26) + 65))
        else:
            fwv += str(chr(randrange(26) + 97))
            
    fwv += "."
    
    for i in range(4):
        fwv += str(chr(randrange(26) + 97))
    
    fwv += str(randrange(80) + 10)
    return fwv
    
def getJsParams(JsContent, publicKey):
    '''get params in challenge.script'''
    C_FORMAT = "js,swf11,swf11.7,swf,h5c,h5ct,svg,h5v,v/ogg,v/webm,h5a,a/ogg,ua/firefox,ua/firefox21,os/nt,os/nt5.1,%s,jslib/jquery,jslib/jqueryui"
    
    macher = re.search("magic:\s*'(.+)',", JsContent)
    magic = macher.group(1)
    macher = re.search("chalapi:\s*'(.+)',", JsContent)
    chalApi = macher.group(1)
    macher = re.search("chalstamp:\s*(\d+),", JsContent)
    chalStamp = macher.group(1)
    macher = re.search("size:\s*'(.+)',", JsContent)
    size = macher.group(1)
    macher = re.search("theme:\s*'(.+)',", JsContent)
    theme = macher.group(1)
    
    jsParams = {}
    jsParams.update({'k': publicKey})
    jsParams.update({'f': "_ACPuzzleUtil.callbacks%5B0%5D"})
    jsParams.update({'l': "en"})
    jsParams.update({'t': "img"})
    jsParams.update({'s': size})
    jsParams.update({'c': C_FORMAT % getFwv()})
    jsParams.update({'am': magic})
    jsParams.update({'ca': chalApi})
    jsParams.update({'ts': round(time.time() * 1000)})
    jsParams.update({'ct': chalStamp})
    jsParams.update({'th': theme})
    jsParams.update({'r': str(random.random())}) 
    
    return jsParams

def jsParamsToString(jsParams):  
    jsParamsStr = ""
    for key, value in jsParams.items():     
        jsParamsStr += key
        jsParamsStr += "="
        jsParamsStr += str(value)
        jsParamsStr += ";"
        
    return jsParamsStr[:len(jsParamsStr) - 1]  # remove last ';'

def showCaptcha(imageFile):
    
    dialogRoot = Tk()
    dialogRoot.title("Input text.")
    
    img = PhotoImage(file=imageFile)
    
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
            global captcha_response 
            captcha_response = inputEntry.get().strip()
            dialogRoot.destroy()

    
    button = Button(frame, text="蝣箏�", command=getInputText)
    button.pack(side=LEFT)
    
    frame.pack()
    
    dialogRoot.mainloop()

    
def getUserInputUrl():
    url = input("Please input a url:")
    if url == "" :
        url = "http://rapidgator.net/file/bf6293fc58898b2bacbd4b9b6e4bff8d/Android_Security.zip.html"
        #  simple and short file
        #  http://rapidgator.net/file/d19e13bbe42b6e092e76094ecb0df641/aaa.rar.html 
        
    if not "http://" in url:
        print("Not a valid URL.")
        return None
        
    return url

        
if __name__ == '__main__':
    
    baseUrl = "http://rapidgator.net"
    url = getUserInputUrl()
    print("GET user input: ", url)
    
    
    '''phase 1'''
    '''fetch the starting page of downloading url'''
    cookies = http.cookiejar.CookieJar()
    http_page_response = HttpUtility.sendHttpRequest(url, None, None, cookies)
    start_html_page=HttpUtility.getHtmlPage(http_page_response)
    
    # parse the java script var in downloading page
    javascript_var_parser=ParserUtility.HTMLTagParser(True, url)
    javascript_var_parser.feed(start_html_page)

    if javascript_var_parser.get_downloadInfo().strip() != "":
        print(javascript_var_parser.get_downloadInfo())
        sys.exit()
    
    # press slow download btn   (#btn-free)
    fid_param=urllib.parse.urlencode({'fid': javascript_var_parser.get_fid()})
    sid_response=HttpUtility.sendAjaxRequest(baseUrl+javascript_var_parser.get_startTimerUrl().strip()+"?"+fid_param,
                                             {'Referer': url}, 
                                             None, 
                                             cookies)
    sid_result=json.loads(sid_response.read().decode('utf-8'))
    if sid_result['state'] != "started":
        print("Error! after press slow download button.")
        print("Stop!!!")
        sys.exit()
    
    javascript_var_parser.set_sid(sid_result['sid'])
    
    
    # start counting down   ( at startTimer() )
    for left_time in range(int(javascript_var_parser.get_secs())+1, 0, -1):
            print("Remaining: ", left_time)
            time.sleep(1)


    # get download link     ( at getDownloadLink() )
    sid_param=urllib.parse.urlencode({'sid':javascript_var_parser.get_sid()})
    get_download_link_response=HttpUtility.sendAjaxRequest(baseUrl+javascript_var_parser.get_getDownloadUrl().strip()+"?"+sid_param,
                                             {'Referer': url}, 
                                             None, 
                                             cookies)
    get_download_link_result=json.loads(get_download_link_response.read().decode('utf-8'))
    if get_download_link_result['state'] != "done":
        print("Error! after get download link.")
        print("Stop!!!")
        sys.exit()
    
    # go to captcha page   
    captcha_page_response=HttpUtility.sendHttpRequest(baseUrl+javascript_var_parser.get_captchaUrl(), {'Referer': url}, None, cookies)
    captcha_html_page=HttpUtility.getHtmlPage(captcha_page_response)
    #print(captcha_html_page)   write to file instead for debug
    if captcha_html_page.strip() != "":
        OtherUtility.write_file("captcha_page.html", captcha_html_page.encode('utf-8'))
    else:
        print("Empty response.")
    '''pahse 2'''
    '''get download link'''
    
    download_url=ParserUtility.find_download_link(StringIO(captcha_html_page))
    if (download_url == None):
        print(captcha_page_response.read())
        print("Download link not found")
        sys.exit()
    else:
        print("Going to download.")
        print(download_url)
        
    captcha_page_response=HttpUtility.sendHttpRequest(download_url, {'Referer': url, 'Connection': "keep-alive"}, None, cookies)
    OtherUtility.write_file("aaa.zip", captcha_page_response.read())
    
    
    
    
    '''phase 2'''
    '''solve the captcha'''
    '''captcha is disappear'''
    '''# get noscript captcha url
    noscript_captcha_url=ParserUtility.find_noscript_captcha_url(StringIO(captcha_html_page))
    print(noscript_captcha_url)
    
    # request noscript captcha page
    noscript_captcha_response=HttpUtility.sendHttpRequest(noscript_captcha_url, {'connection':"keep-alive"}, None, cookies)
    noscript_captcha_html=HttpUtility.getHtmlPage(noscript_captcha_response)
    OtherUtility.write_file("captcha_noscript_page.html", noscript_captcha_html.encode('utf-8'))
    
    # prepare captcha response
    captcha_post_data=ParserUtility.find_noscript_post_data(StringIO(noscript_captcha_html))
    captcha_img_url=ParserUtility.find_noscript_captcha_img(StringIO(noscript_captcha_html))
    captcha_img_response=HttpUtility.sendHttpRequest("http://api.solvemedia.com"+captcha_img_url, {'connection':"keep-alive"}, None, cookies)
    captcha_img=HttpUtility.getImgFile(captcha_img_response)
    OtherUtility.write_file("captcha.gif", captcha_img)
    captcha_dialog_o=OtherUtility.captcha_dialog("captcha.gif")
    print(captcha_dialog_o.get_captcha_ans())'''