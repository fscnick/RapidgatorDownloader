# -*- coding: utf-8 -*-
'''
Created on 2013/12/20

@author: 10110045
'''
from keepalive_singleton import keepalive_singleton
import traceback
import urllib

'''debug flag'''
DEBUG=False

def sendHttpRequest(url, headers, data, cookies):
    '''send an http request to url,
    if data in None GET will use.
    the default connect is keep-alive.'''
    if url == None:
        print("URL is None.")
        return None
    
    if not "http://" in url:
        print("Not a valid URL.")
        return None
    
    if headers != None and type(headers) != type({}) :
        print("Header must be 'dict' type.")
        return None
    elif headers == None:
        headers = {}
    
    if data != None and type(data) != type ({}):
        print("data must be 'None' or 'dict' type .")
        return None
    else:
        if data != None:
            encodedData = urllib.parse.urlencode(data)
            encodedData = encodedData.encode(encoding='utf_8')
            print("encodeData:\n ", encodedData)
        else:
            encodedData = None
            
    
    # prepare http handle
    if headers != None and 'Connection' in headers and headers['Connection'] == "keep-alive":
        keepalive_handler=keepalive_singleton();
        opener = urllib.request.build_opener( keepalive_handler,
                                             urllib.request.HTTPCookieProcessor(cookies))
    else:
        opener = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(cookies))
    urllib.request.install_opener(opener)
    
    # set request url
    httpRequest = urllib.request.Request(url, encodedData, headers)
    
    # request HTTP
    try:
        response = opener.open(httpRequest)
        
        if (DEBUG):
            print("HEADER: \n", headers, " \n")
            print("DATA: \n", data, "\n")
            print("COOKIES: \n", cookies, "\n")
    except:
        print("Fail open Url:" + url)
        
        if (DEBUG):
            print("HEADER: \n", headers, " \n")
            print("DATA: \n", data, "\n")
            print("COOKIES: \n", cookies, "\n")
            traceback.print_exc()
            
        
    return response


def sendAjaxRequest(url, headers, data, cookies):
    '''send ajax request to url'''
    if 'Content-type' in headers and headers['Content-type']!="application/x-www-form-urlencoded":
        headers['Content-type']!="application/x-www-form-urlencoded"
    if 'Content-type' not in headers:
        headers.update({'Content-type' : "application/x-www-form-urlencoded"})
    

    if 'XMLHttpRequest' in headers and headers['X-Requested-With']!="XMLHttpRequest":
        headers['X-Requested-With']="XMLHttpRequest"
    if 'X-Requested-With' not in headers:
        headers.update({'X-Requested-With' : "XMLHttpRequest"})
        
    if 'Connection' not in headers:
        headers.update({'Connection':"keep-alive"})
        
    return sendHttpRequest(url, headers, data, cookies)
    

def getHtmlPage(http_response):
    '''convert a http response to plain text'''
    return http_response.read().decode('utf-8')

def getImgFile(http_response):
    '''convert http response to image file'''
    return http_response.read()


if __name__ == '__main__':
    pass