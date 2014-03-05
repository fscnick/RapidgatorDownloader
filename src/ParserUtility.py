# -*- coding: utf-8 -*-
'''
Created on 2013/12/20

@author: 10110045
'''
from _pyio import StringIO
from html.parser import HTMLParser
from xml.etree import ElementTree
import codecs
import re


def extract_float(string):
    match=re.search('([0-9.])',string)
    if match:
        return float(match.group(1))


class HTMLTagParser(HTMLParser):
    '''parse the javascript var at the bottom of starting downloading page'''
    def __init__(self, strict, url):
        HTMLParser.__init__(self, strict)
        
        self.url = url
        
        self.script_flag = False
        self.script_data = ""
        
        self.startTimerUrl = ""
        self.getDownloadUrl = ""
        self.captchaUrl = ""
        self.secs = ""
        self.download_link = ""
        self.sid = ""
        self.fid = ""
        
        self.fileSize = -1  # in bytes
        
        self.firstDiv = False  # class="text-block file-descr"
        self.secondDiv = False  # class="btm"
        self.thirdDiv = False  # no attr
        self.fileSizeStrong = False
        
        self.allowOrNot=False # <div id="table_header" class="table_header">
        self.downloadInfo=""
    
    def handle_starttag(self, tag, attrs):
        
        if tag == "script":
            for attr in attrs:
                if attr == ("type", "text/javascript"):
                    self.script_flag = True
                    
        if self.firstDiv == False and self.secondDiv == False and self.thirdDiv == False and tag == "div":
            for attr in attrs:
                if attr == ("class", "text-block file-descr"):
                    self.firstDiv = True
                    return
                    
        if self.firstDiv == True and self.secondDiv == False and self.thirdDiv == False and tag == "div":
            for attr in attrs:
                if attr == ("class", "btm"):
                    self.secondDiv = True
                    self.firstDiv = False
                    return
        
                    
        if self.firstDiv == False and self.secondDiv == True and self.thirdDiv == False and tag == "div":
            self.thirdDiv = True
            self.secondDiv = False
            return
            
        if self.firstDiv == False and self.secondDiv == False and self.thirdDiv == True and tag == "strong" :
            self.fileSizeStrong = True
            self.thirdDiv =False
            return
        
        if self.allowOrNot == False and tag == "div":
            if ("id","table_header") in attrs and ("class","table_header") in attrs:
                self.allowOrNot=True
                return
                    
                    
    def handle_data(self, data):
        if self.script_flag == True:
            lines = data.split(";")
            for line in lines:
                result = re.search("    var (.+) = '?([\w,_,\/]*)'?", line)
                if result:
                    var = result.group(1)
                    value = result.group(2)
                    if var == "startTimerUrl":
                        self.startTimerUrl = value

                    elif var == "getDownloadUrl":
                        self.getDownloadUrl = value

                    elif var == "captchaUrl":
                        self.captchaUrl = value

                    elif var == "secs":
                        self.secs = value

                    elif var == "download_link":
                        self.download_link = value

                    elif var == "sid":
                        self.sid = value

                    elif var == "fid":
                        self.fid = value  

                        
        if self.fileSizeStrong == True:
            if "KB" in data:
                self.fileSize = extract_float(data) * 1024
            if "MB" in data:
                self.fileSize = extract_float(data) * 1024 * 1024
            if "GB" in data:
                self.fileSize = extract_float(data) * 1024 * 1024 * 1024
                
            self.firstDiv = False
            self.secondDiv = False
            self.thirdDiv = False
            self.fileSizeStrong = False
            
        if self.allowOrNot == True:
            self.downloadInfo=data
            self.allowOrNot=False
            
                       
        
    def handle_endtag(self, tag):
         if tag == "script" and self.script_flag == True:
            self.script_flag = False
            
    def show_data(self):
        print("startTimerUrl: ", self.startTimerUrl)
        print("getDownloadUrl: ", self.getDownloadUrl)
        print("captchaUrl: ", self.captchaUrl)
        print("secs: ", self.secs)
        print("download_link: ", self.download_link)
        print("sid: ", self.sid)
        print("fid: ", self.fid)
        print()
        print("file_size: ", self.fileSize)
        print("download info: ", self.downloadInfo)
        
    def get_startTimerUrl(self):
        return self.startTimerUrl
                     
    def get_getDownloadUrl(self):
        return self.getDownloadUrl
             
    def get_captchaUrl(self):
        return self.captchaUrl
    
    def get_secs(self):
        return self.secs
             
    def get_download_link(self):
        return self.download_link
               
    def get_sid(self):
        return self.sid
             
    def get_fid(self):
        return self.fid
    
    def get_fileSize(self):
        return self.fileSize

    def set_sid(self, sid):
        self.sid=sid
        
    def get_downloadInfo(self):
        return self.downloadInfo
        


def find_noscript_captcha_url(data):
    iframe_line=""
    for line in data.readlines():
        if "iframe" in line:
            iframe_line=line
            break
    
    if iframe_line=="":
        return None
    
    match=re.search("src=\"(.*)\"\sheight",iframe_line)
    return match.group(1)

def find_noscript_captcha_img(data):
    img_line=""
    for line in data.readlines():
        if "img" in line and "adcopy-puzzle-image" in line:
            img_line=line
            break
    
    if img_line=="":
        return None

    match=re.search("src=\"(.*)\"\salt",img_line)
    return match.group(1)

def find_noscript_post_data(data):
    hidden_line_data={}
    for line in data.readlines():
        if "input" in line and "hidden" in line:
            if "adcopy_challenge" in line:
                match=re.search("name=\"(.*)\"\sid=\".*\"\svalue=\"(.*)\"",line)
            else:
                match=re.search("name=\"(.*)\"\svalue=\"(.*)\"",line)
                
            hidden_line_data[match.group(1)]=match.group(2)
            
    if hidden_line_data=={}:
        return None
    
    return hidden_line_data

def find_download_link(data):
    download_link=""
    for line in data.readlines():
        if "rapidgator" in line and "download" in line and "index" in line and "session_id" in line:
            match=re.search("return\s'(.*)'",line)
            download_link=match.group(1)
            return download_link
        
    return None
    


if __name__ == '__main__':
    page=codecs.open("captcha_page.html", "r", "utf-8")
    link=find_download_link(page)
    print(link)