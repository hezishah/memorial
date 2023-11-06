#Information taken from: https://www.kan.org.il/lobby/kidnapped/

import xml.etree.ElementTree as ET
import requests
import pygame
from io import BytesIO
from bidi.algorithm import get_display
import webview
import urllib

X = 230
Y = 500
ACTION = pygame.event.custom_type()
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

def displayPerson(indx, scrn, data):
    scrn.fill((0,0,0))
    headers = {
        'User-Agent': 'Mozilla',
        'From': 'h@h.com'  # This is another valid field
    }
    # create a surface object, image is drawn on it.
    response = None
    while True:
        try:
            response = requests.get(urllib.parse.unquote(data[indx][0]), headers=headers)
            break
        except Exception as e:
            print(e)
    img = pygame.image.load(BytesIO(response.content))
    
    # Using blit to copy content from one surface to other
    factor = img.get_width() / 230.0
    IMAGE_SMALL = pygame.transform.scale(img, (230, img.get_height() / factor))
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
    pygame.display.flip()

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
    scrn = pygame.display.set_mode((X, Y))
    
    #webview.create_window(memorialData[0][2], memorialData[0][0])
    #webview.start()

    # set the pygame window name
    pygame.display.set_caption("Captured")
    cur = 0
    displayPerson(0, scrn, memorialData)
    status = True
    pygame.time.set_timer(pygame.event.Event(ACTION, action=getIndex(cur, len(memorialData))), 2000, 1)
    while (status):
    
    # iterate over the list of Event objects
    # that was returned by pygame.event.get() method.
        for i in pygame.event.get():
    
            # if event object type is QUIT
            # then quitting the pygame
            # and program both.
            if i.type == pygame.QUIT:
                status = False
            if i.type == ACTION:
                # if there's an ACTION event, invoke its action!!!
                cur = i.action
                displayPerson(cur, scrn, memorialData)
                pygame.time.set_timer(pygame.event.Event(ACTION, action=getIndex(cur, len(memorialData))), 2000, 1)

    
    # deactivates the pygame library
    pygame.quit()
if __name__ == "__main__":
    main()