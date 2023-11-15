#Information taken from: https://www.kan.org.il/lobby/kidnapped/

import re
from urllib.parse import urlparse
import xml.etree.ElementTree as ET
from urllib.request import Request
import pygame
#from io import BytesIO
from bidi.algorithm import get_display
#import webview
import urllib
import http
import cv2
from face_detector import YoloDetector
# importing the module
#import bson
#import numpy as np

def urlEncodeNonAscii(b):
    return re.sub('[\x80-\xFF]', lambda c: '%%%02x' % ord(c.group(0)), b)

model = YoloDetector(target_size=720, device="cpu", min_face=90)
    
X = 230
Y = 500
ACTION = pygame.event.custom_type()
ACTION_ZOOM = pygame.event.custom_type()
def formatText(t):
    if t:
        t = t.strip()
        if len(t) > 0 and t != "undefined" and t != "None":
            return(t.replace("undefined","").replace("None","").strip())
        return ""
    return ""

def getIndex(cur, len):
    curNew = cur + 1
    if curNew == len:
        curNew = 0
    return curNew

images = []
bbox = None
scale = 1.0
scaleStart = 1.0
def displayPerson(indx, scrn, data):
    global images
    global bbox
    global scale
    global scaleStart
    scrn.fill((0,0,0))
    headers = {
        'User-Agent': 'Mozilla',
        'From': 'h@h.com'  # This is another valid field
    }
    # create a surface object, image is drawn on it.
    img = None
    if len(images) <= indx:
        response = None

        try:
            opener = urllib.request.build_opener()
            url = urllib.parse.unquote(data[indx][0],encoding='utf-8')
            urlparts = url.split("//")
            
            if len(urlparts) > 1:
                urlparts[1] = urllib.parse.quote(urlparts[1])
            url = "//".join(urlparts)
            while True:
                req = urllib.request.Request(
                    url, 
                    data=None, 
                    headers=headers
                )
                requestObj = urllib.request.urlopen(req)
                response=b''
                while True:
                    try:
                        responseJSONpart = requestObj.read()
                    except http.client.IncompleteRead as icread:
                        response = response + icread.partial
                        continue
                    else:
                        response = response + responseJSONpart
                        break
                with open("images/" + str(indx) + ".jpg", "wb") as f:
                    f.write(response)
                try:
                    img = pygame.image.load("images/"+str(indx) + ".jpg")
                    break
                except Exception as e:
                    print(e)
            images.append(img)
        except Exception as RESTex:
            print("Exception occurred making REST call: " + RESTex.__str__())
            exit(0)
    else:
        img = images[indx]
    # Using blit to copy content from one surface to other
    factor = img.get_width() / 230.0
    IMAGE_SMALL = pygame.transform.scale(img, (230, img.get_height() / factor))
    cvimg = pygame.surfarray.array3d(pygame.transform.flip(pygame.transform.rotate(img,90), flip_x=False, flip_y=True))
    retry = 10
    fxy = 1.0
    while retry:
        bboxes,points = model.predict(cvimg)
        if len(bboxes[0]) > 0:
            break
        cvimg = cv2.resize(cvimg, (0,0), fx=1.1, fy=1.1)
        fxy *= 1.1
        retry -= 1
    if retry == 0:
        bboxes = [[[0,0,230,230]]]
    else:
        for boxes in bboxes[0]:
            boxes[0] /= fxy
            boxes[1] /= fxy
            boxes[2] /= fxy
            boxes[3] /= fxy
    #print(bboxes,points)
    boxwidthx = bboxes[0][0][2] - bboxes[0][0][0]
    scale = boxwidthx / (img.get_width() * 2.0)
    if scale < 1.0:
        scale = 1.0
    scaleStart = scale
    bbox = bboxes[0][0]
    for boxes in bboxes[0]:
        #pygame.draw.rect(IMAGE_SMALL, (0,255,0), pygame.Rect(boxes[0]/factor, boxes[1]/factor, (boxes[2]-boxes[0])/factor, (boxes[3]-boxes[1])/factor), 2)
        bbox[0] = min(bbox[0],boxes[0])
        bbox[1] = min(bbox[1],boxes[1])
        bbox[2] = max(bbox[2],boxes[2])
        bbox[3] = max(bbox[3],boxes[3])
    return
    if False:
        # convert to grayscale of each frames
        gray = cv2.cvtColor(cvimg, cv2.COLOR_RGB2GRAY)
        # read haacascade to detect faces in input image
        face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_alt.xml')
        #face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')

        # detects faces in the input image
        try:
            faces = face_cascade.detectMultiScale(gray, 1.1, 2)
            print('Number of detected faces:', len(faces))\

            # loop over all the detected faces
            for (x,y,w,h) in faces:
                # To draw a rectangle around the detected face
                pygame.draw.rect(IMAGE_SMALL, (0,255,255), pygame.Rect(x/factor, y/factor, w/factor, h/factor), 2)  
                #cv2.rectangle(IMAGE_SMALL,(x,y),(x+w,y+h),(0,255,255),2)
        except Exception as e:
            print(e)
    scrn.blit(IMAGE_SMALL, (0, 0))
    x = 0
    y = 0
    pygame.font.init()
    font = pygame.font.SysFont("tahoma", 20)
    width, height = font.size(data[indx][1])
    xoffset = (X-width) // 1.5
    yoffset = (Y-height) // 1.5 + 100
    coords = x+xoffset, y+yoffset
    color=(255,0,100)
    bidi_text = get_display(data[indx][1])
    txt = font.render(bidi_text, True, color)
    scrn.blit(txt, coords)
    

    width, height = font.size(data[indx][2])
    xoffset = (X-width) // 1.5
    yoffset = (Y-height) // 1.5 + 150
    coords = x+xoffset, y+yoffset
    color=(100,100,255)
    bidi_text = get_display(data[indx][2])
    txt = font.render(bidi_text, True, color)
    scrn.blit(txt, coords)
    

    # paint screen one time
    pygame.display.update()
    #pygame.display.flip()

def zoomPerson(indx, scrn, data):
    global images
    global scale
    global scaleStart
    global bbox
    scrn.fill((0,0,0))
    # create a surface object, image is drawn on it.
    img = images[indx]
    # Using blit to copy content from one surface to other
    factor = ( scale * 230.0 ) / img.get_width()
    dx = (bbox[0] + bbox[2])/4.0
    dy = (bbox[1] + bbox[3])/4.0
    boxwidthx = (bbox[2] - bbox[0]) * factor
    #if boxwidthx < 230:
    scale += 0.01 
    IMAGE_SMALL = pygame.transform.smoothscale_by(img, factor)

    #pygame.draw.rect(IMAGE_SMALL, (0,255,0), pygame.Rect(bbox[0]/factor, bbox[1]/factor, (bbox[2]-bbox[0])/factor, (bbox[3]-bbox[1])/factor), 2)
    x = (scale - scaleStart) * ( - dx * factor) - (scale - scaleStart) * 50.0
    y = (scale - scaleStart) * ( - dy * factor) + (scale - scaleStart) * 50.0
    scrn.blit(IMAGE_SMALL, (x,y))
    #print((x,y))
    pygame.draw.rect(scrn, (0,0,0), (0, scrn.get_height()-150, scrn.get_width(), 300))

    x = 0.0
    y = 0.0
    pygame.font.init()
    font = pygame.font.SysFont("tahoma", 20)
    width, height = font.size(data[indx][1])
    xoffset = (X-width) // 1.5
    yoffset = (Y-height) // 1.5 + 100
    coords = x+xoffset, y+yoffset
    color=(255,0,100)
    bidi_text = get_display(data[indx][1])
    txt = font.render(bidi_text, True, color)
    scrn.blit(txt, coords)
    

    width, height = font.size(data[indx][2])
    xoffset = (X-width) // 1.5
    yoffset = (Y-height) // 1.5 + 150
    coords = x+xoffset, y+yoffset
    color=(100,100,255)
    bidi_text = get_display(data[indx][2])
    txt = font.render(bidi_text, True, color)
    scrn.blit(txt, coords)
    

    # paint screen one time
    pygame.display.update()
    #pygame.display.flip()

def main():
    memorialList = ET.parse("memorial-list.xml")
    memorialData = []
    name = ""
    takenFrom = ""
    img = ""
    for elem in memorialList.iter():
        if elem.tag == 'img':
            val = formatText(elem.attrib['src'])
            if len(val.strip()) > 0:
                #print(val)
                name = val
        if elem.tag == 'span':
            val = formatText(elem.tail)
            if len(val.strip()) > 0:
                #print(val)
                takenFrom = val
        if elem.tag == 'div':
            val = formatText(elem.text)
            if len(val.strip()) > 0:
                #print(val)
                img = val
                memorialData.append([name, takenFrom,img])
    #print(memorialData)
    # activate the pygame library .
    pygame.init()
 
    # create the display surface object
    # of specific dimension..e(X, Y).
    scrn = pygame.display.set_mode((X, Y), flags=pygame.HWACCEL, vsync=1)
    
    #webview.create_window(memorialData[0][2], memorialData[0][0])
    #webview.start()

    # set the pygame window name
    pygame.display.set_caption("Captured")
    cur = 0
    displayPerson(0, scrn, memorialData)
    status = True
    timerNex = pygame.time.set_timer(pygame.event.Event(ACTION, action=getIndex(cur, len(memorialData))), 2000, 1)
    timerZoom = pygame.time.set_timer(pygame.event.Event(
                    ACTION_ZOOM, 
                    action=getIndex(cur, len(memorialData))), 
                    3, 
                    1)
    stopped = False
    while (status):
    
    # iterate over the list of Event objects
    # that was returned by pygame.event.get() method.
        for i in pygame.event.get():
    
            # if event object type is QUIT
            # then quitting the pygame
            # and program both.
            if i.type == pygame.QUIT:
                status = False
            if i.type == pygame.KEYDOWN:
                if i.key == pygame.K_LEFT:
                    if cur > 0:
                        cur -= 1
                if i.key == pygame.K_RIGHT:
                    if cur+1 < len(memorialData):
                        cur += 1
                displayPerson(cur, scrn, memorialData)
                zoomPerson(cur, scrn, memorialData)
                stopped = True
            if i.type == ACTION:
                if stopped:
                    continue
                # if there's an ACTION event, invoke its action!!!
                cur = i.action
                displayPerson(cur, scrn, memorialData)
                timerNex = pygame.time.set_timer(pygame.event.Event(ACTION, action=getIndex(cur, len(memorialData))), 2000, 1)
                timerZoom = pygame.time.set_timer(pygame.event.Event(
                    ACTION_ZOOM, 
                    action=getIndex(cur, len(memorialData))), 
                    33, 
                    1)
            if i.type == ACTION_ZOOM:
                if stopped:
                    continue
                zoomPerson(cur, scrn, memorialData)
                timerZoom = pygame.time.set_timer(pygame.event.Event(
                    ACTION_ZOOM, 
                    action=getIndex(cur, len(memorialData))), 
                    33, 
                    1)
    
    # deactivates the pygame library
    pygame.quit()
if __name__ == "__main__":
    main()