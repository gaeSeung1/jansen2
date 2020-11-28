PORT = 6000

# https://www.mixedcontentexamples.com
file = 'steveholt.jpg'
#host = 'localhost:6000'
host = 'gaeseung.local'

from http.client import HTTPConnection
import numpy as np
import cv2
from sys import argv

def Upload(body, headers={}):
    conn = HTTPConnection(f"{host}:{PORT}")
    conn.request('POST', '/', body=body, headers=headers)
    res = conn.getresponse()


def Download():
    with open(file, 'wb') as File:
        conn = HTTPConnection('www.mixedcontentexamples.com')
        conn.request("GET", "/Content/Test/steveholt.jpg")
        res = conn.getresponse()
        File.write(res.read())
        print('Downloaded to', file)

def DownloadAndUpload():
    Download()
    with open(file, 'rb') as File:
        Upload(File.read())

def UploadNumpy(img):
    result, img = cv2.imencode('.jpg', img, [int(cv2.IMWRITE_JPEG_QUALITY), 90])
    if not result:
        raise Exception('Image encode error')

    Upload(img.tobytes(), {
        "X-Client2Server" : "123"
    })



    