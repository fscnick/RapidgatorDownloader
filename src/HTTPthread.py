# -*- coding: utf-8 -*-
'''
Created on 2014/2/25

@author: 10110045
'''
from _pyio import StringIO
from http import cookiejar
import HttpUtility
import OtherUtility
import ParserUtility
import http
import json
import sys
import threading
import time
import urllib

class HttpStatus():
    def __init__(self, cookies=None, fileUrl=None, javascript_var_parser=None, get_download_link_result=None,
                       captcha_html_page=None, download_url=None, op=None, statusInfo=None):

        self.cookies=cookies
        self.fileUrl=fileUrl
        self.javascript_var_parser=javascript_var_parser
        self.get_download_link_result=get_download_link_result
        self.captcha_html_page=captcha_html_page
        self.download_url=download_url
        
        self.op=op
        self.statusInfo=statusInfo
        
    def getCookies(self):
        return self.cookies
    
    def getFileUrl(self):
        return self.fileUrl
    
    def getJavascript_var_parser(self):
        return self.javascript_var_parser
    
    def getGet_download_link_result(self):
        return self.get_download_link_result
    
    def getCaptcha_html_page(self):
        return self.captcha_html_page
    
    def getDownlod_url(self):
        return self.download_url
    
    def getOP(self):
        return self.op
    
    def getStatusInfo(self):
        return self.statusInfo

class HTTPthread(threading.Thread):
    '''
    work thread.
    
    if self.op is negative, the current work is done.
    Thuther more, is self.statusInfo contains "Error" that some error occur.
    '''


    def __init__(self):
        '''
        Constructor
        '''
        super().__init__()
        
        self.stopFlag=False
        
        self.baseUrl="http://rapidgator.net"
        self.cookies=http.cookiejar.CookieJar()
        self.fileUrl=None
        self.javascript_var_parser=None
        self.get_download_link_result=None
        self.captcha_html_page=None
        self.download_url=None
        
        self.op=0
        self.statusInfo="Wait to Start"
        
    def setHttpStatus(self, status):
        self.cookies=status.getCookies()
        self.fileUrl=status.getFileUrl()
        self.javascript_var_parser=status.getJavascript_var_parser()
        self.get_download_link_result=status.getGet_download_link_result()
        self.captcha_html_page=status.getCaptcha_html_page()
        self.download_url=status.getDownlod_url()
        
        self.op=status.getOP()
        self.statusInfo=status.getStatusInfo()
        
    def getHttpStatus(self):
        status=HttpStatus(self.cookies, self.fileUrl, self.javascript_var_parser, self.get_download_link_result,
                          self.captcha_html_page, self.download_url, self.op, self.statusInfo)
        return status
        
    def setURL(self, url):
        self.fileUrl=url
        
    def setOP(self, opNum):
        self.op=opNum
        
    def setStatusInfo(self, info):
        self.statusInfo=info
        
    def getStatusInfo(self):
        return self.statusInfo
    
    def getOP(self):
        return self.op
    
    def setCurrentWorkDone(self):
        self.setOP(-self.getOP())
        
    def goToNextOP(self):
        self.setOP(-self.getOP()+1)
        
    def setStop(self):
        self.stopFlag=True
        
    def run(self):
        '''if self.op == 0:
            self.setStatusInfo("Ready!!")
            self.goToNextOP()'''
        
        if self.op == 1:
            ''' connect to file page and check it is allowed to download right now'''
            print("111111")
            self.setStatusInfo("Connect to file url...")
            
            http_page_response = HttpUtility.sendHttpRequest(self.fileUrl, None, None, self.cookies)
            start_html_page=HttpUtility.getHtmlPage(http_page_response)
            
            # parse the java script var in downloading page
            self.javascript_var_parser=ParserUtility.HTMLTagParser(True, self.fileUrl)
            self.javascript_var_parser.feed(start_html_page)

            if self.javascript_var_parser.get_downloadInfo().strip() != "":
                self.setStatusInfo("Error! "+self.javascript_var_parser.get_downloadInfo())
                print(self.javascript_var_parser.get_downloadInfo())
            
            self.setCurrentWorkDone()
            print("111111done")
            return
        
        if self.op == 2:
            ''' press slow download btn   (#btn-free)'''
            print("2222")
            self.setStatusInfo("Starting download procedure.")
            
            fid_param=urllib.parse.urlencode({'fid': self.javascript_var_parser.get_fid()})
            sid_response=HttpUtility.sendAjaxRequest(self.baseUrl+self.javascript_var_parser.get_startTimerUrl().strip()+"?"+fid_param,
                                             {'Referer': self.fileUrl}, 
                                             None, 
                                             self.cookies)
            sid_result=json.loads(sid_response.read().decode('utf-8'))
            if sid_result['state'] != "started":
                self.setStatusInfo("Error! after press slow download button.")
                print("Error! after press slow download button.")
                print("Stop!!!")
                self.setCurrentWorkDone()
                return
            
            self.javascript_var_parser.set_sid(sid_result['sid'])
            self.setCurrentWorkDone()
            print("2222done")
            return
        
        if self.op == 3 :
            ''' start counting down   ( at startTimer() )'''
            print("33333")
            for left_time in range(int(self.javascript_var_parser.get_secs())+1, 0, -1):
                if self.stopFlag == True:
                    print("User terminate!")
                    return
                
                self.setStatusInfo("Remaining: "+str(left_time)+" sec.")
                print("Remaining: ", left_time)
                time.sleep(1)
                
            self.setCurrentWorkDone()  
            print("33333done")  
            return
        
        if self.op == 4:
            ''' get download link     ( at getDownloadLink() )'''
            print("44444")
            self.setStatusInfo("Starting download procedure continue...")
            sid_param=urllib.parse.urlencode({'sid':self.javascript_var_parser.get_sid()})
            get_download_link_response=HttpUtility.sendAjaxRequest(self.baseUrl+self.javascript_var_parser.get_getDownloadUrl().strip()+"?"+sid_param,
                                             {'Referer': self.fileUrl}, 
                                             None, 
                                             self.cookies)
            self.get_download_link_result=json.loads(get_download_link_response.read().decode('utf-8'))
            if self.get_download_link_result['state'] != "done":
                self.setStatusInfo("Error! after get download link.")
                print("Error! after get download link.")
                print("Stop!!!")
                self.setCurrentWorkDone()
                return
            
            self.setCurrentWorkDone()
            print("44444done")
            return
        
        if self.op == 5:
            ''' go to download page   '''
            print("55555")
            self.setStatusInfo("Redirect to download url...")
            captcha_page_response=HttpUtility.sendHttpRequest(self.baseUrl+self.javascript_var_parser.get_captchaUrl(), {'Referer': self.fileUrl}, None, self.cookies)
            self.captcha_html_page=HttpUtility.getHtmlPage(captcha_page_response)
            self.download_url=ParserUtility.find_download_link(StringIO(self.captcha_html_page))
            if (self.download_url == None):
                self.setStatusInfo("Error! Download link not found")
                print("Error! Download link not found")
                self.setCurrentWorkDone()
                return 
            
            self.setCurrentWorkDone()
            print("55555done")
            return
        
        if self.op == 6 :
            ''' start to download '''
            print("66666")
            self.setStatusInfo("Prepare to download...")
            if self.download_url == None:
                self.setStatusInfo("Error! Download link not found")
                print("Error! Download link not found")
                self.setCurrentWorkDone()
                return
            # Not really download on testing
            #captcha_page_response=HttpUtility.sendHttpRequest(self.download_url, {'Referer': self.fileUrl, 'Connection': "keep-alive"}, None, self.cookies)
            #OtherUtility.write_file("aaa.zip", captcha_page_response.read())
            self.setCurrentWorkDone()
            self.setStatusInfo("DownLoad success!!! save to file aaa.zip")
            print("66666done")
            return
            