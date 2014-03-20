# -*- coding: utf-8 -*-
"""An HTTP handler for urllib2 that supports HTTP 1.1 and keepalive.

This is keepalive.py from the urlgrabber project, available under the GNU LGPL
ported to python 3 (with help from 2to3).

>>> import urllib2
>>> from keepalive import HTTPHandler
>>> keepalive_handler = HTTPHandler()
>>> opener = urllib2.build_opener(keepalive_handler)
>>> urllib2.install_opener(opener)
>>> 
>>> fo = urllib2.urlopen('http://www.python.org')

To remove the handler, simply re-run build_opener with no arguments, and
install that opener.

You can explicitly close connections by using the close_connection()
method of the returned file-like object (described below) or you can
use the handler methods:

  close_connection(host)
  close_all()
  open_connections()

>>> keepalive_handler.close_all()

EXTRA ATTRIBUTES AND METHODS

  Upon a status of 200, the object returned has a few additional
  attributes and methods, which should not be used if you want to
  remain consistent with the normal urllib2-returned objects:

    close_connection()  -  close the connection to the host
    readlines()         -  you know, readlines()
    status              -  the return status (ie 404)
    reason              -  english translation of status (ie 'File not found')

  If you want the best of both worlds, use this inside an
  AttributeError-catching try:

  >>> try: status = fo.status
  >>> except AttributeError: status = None

  Unfortunately, these are ONLY there if status == 200, so it's not
  easy to distinguish between non-200 responses.  The reason is that
  urllib2 tries to do clever things with error codes 301, 302, 401,
  and 407, and it wraps the object upon return.

  You can optionally set the module-level global HANDLE_ERRORS to 0,
  in which case the handler will always return the object directly.
  If you like the fancy handling of errors, don't do this.  If you
  prefer to see your error codes, then do.

"""

import http.client
import socket
import urllib.request
import urllib.error
import urllib.parse

#STRING_VERSION = '.'.join(map(str, VERSION))
DEBUG = 0
HANDLE_ERRORS = 1

class HTTPHandler(urllib.request.HTTPHandler):
    def __init__(self, cookies=None):
        urllib.request.HTTPHandler.__init__(self)
        self._connections = {}
        
    def close_connection(self, host):
        """close connection to <host>
        host is the host:port spec, as in 'www.cnn.com:8080' as passed in.
        no error occurs if there is no connection to that host."""
        self._remove_connection(host, close=1)
    
    def open_connections(self):
        """return a list of connected hosts"""
        return list(self._connections.keys())
    
    def close_all(self):
        """close all open connections"""
        for host, conn in list(self._connections.items()):
            conn.close()
        self._connections = {}
    
    def _remove_connection(self, host, close=0):
        if host in self._connections:
            if close: self._connections[host].close()
            del self._connections[host]
    
    def _start_connection(self, h, req):
        try:
            if req.has_data():
                data = req.get_data()
                h.putrequest('POST', req.get_selector())
                if 'Content-type' not in req.headers:
                    h.putheader('Content-type',
                                'application/x-www-form-urlencoded')
                if 'Content-length' not in req.headers:
                    h.putheader('Content-length', '%d' % len(data))
            else:
                h.putrequest('GET', req.get_selector())
        except socket.error as err:
            raise urllib.error.URLError(err)
        
        for args in self.parent.addheaders:
            h.putheader(*args)
        for k, v in list(req.headers.items()):
            h.putheader(k, v)
            
        # add unredirect headers in headers one of this is cookies   
        # modify by fscnick@hotmail.com
        for k, v in list(req.unredirected_hdrs.items()):
            h.putheader(k, v)
            
        h.endheaders()
        if req.has_data():
            h.send(data)
    
    def do_open(self, http_class, req):
        host = req.get_host()
        if not host:
            raise urllib.error.URLError('no host given')
        
        try:
            need_new_connection = 1
            h = self._connections.get(host)
            if not h is None:
                try:
                    self._start_connection(h, req)
                except socket.error as e:
                    r = None
                else:
                    try: r = h.getresponse()
                    except http.client.ResponseNotReady as e: r = None
                
                if r is None or r.version == 9:
                    # httplib falls back to assuming HTTP 0.9 if it gets a
                    # bad header back.  This is most likely to happen if
                    # the socket has been closed by the server since we
                    # last used the connection.
                    if DEBUG: print(("failed to re-use connection to %s" % host))
                    h.close()
                else:
                    if DEBUG: print(("re-using connection to %s" % host))
                    need_new_connection = 0
            if need_new_connection:
                if DEBUG: print(("creating new connection to %s" % host))
                h = http_class(host)
                self._connections[host] = h
                self._start_connection(h, req)
                r = h.getresponse()
        except socket.error as err:
            raise urllib.error.URLError(err)
        
        # if not a persistent connection, don't try to reuse it
        if r.will_close: self._remove_connection(host)
        
        if DEBUG:
            print(("STATUS: %s, %s" % (r.status, r.reason)))
        r._handler = self
        r._host = host
        r._url = req.get_full_url()
        
        if r.status == 200 or not HANDLE_ERRORS:
            return r
        else:
            return self.parent.error('http', req, r, r.status, r.reason, r.msg)
    
    def http_open(self, req):
        return self.do_open(HTTPConnection, req)

class HTTPResponse(http.client.HTTPResponse):

    # we need to subclass HTTPResponse in order to
    # 1) add readline() and readlines() methods
    # 2) add close_connection() methods
    # 3) add info() and geturl() methods

    # in order to add readline(), read must be modified to deal with a
    # buffer.  example: readline must read a buffer and then spit back
    # one line at a time.  The only real alternative is to read one
    # BYTE at a time (ick).  Once something has been read, it can't be
    # put back (ok, maybe it can, but that's even uglier than this),
    # so if you THEN do a normal read, you must first take stuff from
    # the buffer.

    # the read method wraps the original to accomodate buffering,
    # although read() never adds to the buffer.
    # Both readline and readlines have been stolen with almost no
    # modification from socket.py
    

    def __init__(self, sock, debuglevel=0, strict=0, method=None):
        if method: # the httplib in python 2.3 uses the method arg
            http.client.HTTPResponse.__init__(self, sock, debuglevel, method)
        else: # 2.2 doesn't
            http.client.HTTPResponse.__init__(self, sock, debuglevel)
        self.fileno = sock.fileno
        self._rbuf = b""
        self._rbufsize = 8096
        self._handler = None # inserted by the handler later
        self._host = None    # (same)
        self._url = None     # (same)

    _raw_read = http.client.HTTPResponse.read

    def close_connection(self):
        self.close()
        self._handler._remove_connection(self._host, close=1)
        
    def info(self):
        return self.msg

    def geturl(self):
        return self._url

    def read(self, amt=None):
        # the _rbuf test is only in this first if for speed.  It's not
        # logically necessary
        if self._rbuf and not amt is None:
            L = len(self._rbuf)
            if amt > L:
                amt -= L
            else:
                s = self._rbuf[:amt]
                self._rbuf = self._rbuf[amt:]
                return s

        s = self._rbuf + self._raw_read(amt)
        
        self._rbuf = b''
        return s

    def readline(self, limit=-1):
        data = ""
        i = self._rbuf.find(b'\n')
        while i < 0 and not (0 < limit <= len(self._rbuf)):
            new = self._raw_read(self._rbufsize)
            if not new: break
            i = new.find(b'\n')
            if i >= 0: i = i + len(self._rbuf)
            self._rbuf = self._rbuf + new
        if i < 0: i = len(self._rbuf)
        else: i = i+1
        if 0 <= limit < len(self._rbuf): i = limit
        data, self._rbuf = self._rbuf[:i], self._rbuf[i:]
        return data

    def readlines(self, sizehint = 0):
        total = 0
        list = []
        while 1:
            line = self.readline()
            if not line: break
            list.append(line)
            total += len(line)
            if sizehint and total >= sizehint:
                break
        return list


class HTTPConnection(http.client.HTTPConnection):
    # use the modified response class
    response_class = HTTPResponse
    
#########################################################################
#####   TEST FUNCTIONS
#########################################################################

def error_handler(url):
    global HANDLE_ERRORS
    orig = HANDLE_ERRORS
    keepalive_handler = HTTPHandler()
    opener = urllib.request.build_opener(keepalive_handler)
    urllib.request.install_opener(opener)
    pos = {0: 'off', 1: 'on'}
    for i in (0, 1):
        print(("  fancy error handling %s (HANDLE_ERRORS = %i)" % (pos[i], i)))
        HANDLE_ERRORS = i
        try:
            fo = urllib.request.urlopen(url)
            foo = fo.read()
            fo.close()
            try: status, reason = fo.status, fo.reason
            except AttributeError: status, reason = None, None
        except IOError as e:
            print(("  EXCEPTION: %s" % e))
            raise
        else:
            print(("  status = %s, reason = %s" % (status, reason)))
    HANDLE_ERRORS = orig
    hosts = keepalive_handler.open_connections()
    print(("open connections:", ' '.join(hosts)))
    keepalive_handler.close_all()

def continuity(url):
    from hashlib import md5
    format = '%25s: %s'
    
    # first fetch the file with the normal http handler
    opener = urllib.request.build_opener()
    urllib.request.install_opener(opener)
    fo = urllib.request.urlopen(url)
    foo = fo.read()
    fo.close()
    m = md5(foo)
    print((format % ('normal urllib', m.hexdigest())))

    # now install the keepalive handler and try again
    opener = urllib.request.build_opener(HTTPHandler())
    urllib.request.install_opener(opener)

    fo = urllib.request.urlopen(url)
    foo = fo.read()
    fo.close()
    m = md5(foo)
    print((format % ('keepalive read', m.hexdigest())))

    fo = urllib.request.urlopen(url)
    foo = b''
    while 1:
        f = fo.readline()
        if f: foo = foo + f
        else: break
    fo.close()
    m = md5(foo)
    print((format % ('keepalive readline', m.hexdigest())))

def comp(N, url):
    print(('  making %i connections to:\n  %s' % (N, url)))

    sys.stdout.write('  first using the normal urllib handlers')
    # first use normal opener
    opener = urllib.request.build_opener()
    urllib.request.install_opener(opener)
    t1 = fetch(N, url)
    print(('  TIME: %.3f s' % t1))

    sys.stdout.write('  now using the keepalive handler       ')
    # now install the keepalive handler and try again
    opener = urllib.request.build_opener(HTTPHandler())
    urllib.request.install_opener(opener)
    t2 = fetch(N, url)
    print(('  TIME: %.3f s' % t2))
    print(('  improvement factor: %.2f' % (t1/t2, )))
    
def fetch(N, url, delay=0):
    lens = []
    starttime = time.time()
    for i in range(N):
        if delay and i > 0: time.sleep(delay)
        fo = urllib.request.urlopen(url)
        foo = fo.read()
        fo.close()
        lens.append(len(foo))
    diff = time.time() - starttime

    j = 0
    for i in lens[1:]:
        j = j + 1
        if not i == lens[0]:
            print(("WARNING: inconsistent length on read %i: %i" % (j, i)))

    return diff

def test(url, N=10):
    print("checking error hander (do this on a non-200)")
    try: error_handler(url)
    except IOError as e:
        print("exiting - exception will prevent further tests")
        sys.exit()
    print()
    print("performing continuity test (making sure stuff isn't corrupted)")
    continuity(url)
    print()
    print("performing speed comparison")
    comp(N, url)
    
if __name__ == '__main__':
    import time
    import sys
    try:
        N = int(sys.argv[1])
        url = sys.argv[2]
    except:
        print(("%s <integer> <url>" % sys.argv[0]))
    else:
        test(url, N)