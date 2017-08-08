# -*- coding: utf-8 -*-
import time
from time import strftime
import threading
import win32gui # pywin
import random
import numpy as np # pip install numpy
import cv2 # opencv
import PIL.ImageGrab as ig # pip install Pillow
import pywinauto # pip install pywinauto
import pyperclip
import Tkinter
import ttk
import pythoncom, pyHook # https://sourceforge.net/projects/pyhook/

app = None
hm = None
escapeEvent = False
appRunning = False
appPaused = False
chromeFound = False
chromeMutex = threading.Lock()
chromeSize = [0, 0, 1, 1]
currentUrl = ""
myUrl = "google.com" # example url

logSize = 0 # contain the number of lines in the logbox
logLimit = 200 # logbox line limit (old lines will be deleted)
logStrings = [] # store the strings to be put in the logbox
logMutex = threading.Lock() # to make thread safe actions
logtext = None


def move(x,y): # move the mouse
    pywinauto.mouse.move(coords=(x, y))

def click(x,y): # move the mouse and click
    pywinauto.mouse.move(coords=(x, y))
    pywinauto.mouse.click(coords=(x, y))

def doubleclick(x,y): # move the mouse and click
    pywinauto.mouse.move(coords=(x, y))
    pywinauto.mouse.double_click(coords=(x, y))

def press(Key): # press a key, see http://pywinauto.readthedocs.io/en/latest/code/pywinauto.keyboard.html
    pywinauto.keyboard.SendKeys(Key)

def copy():
    pywinauto.keyboard.SendKeys('^c') # Ctrl+C
    return pyperclip.paste() # return clipboard content

def paste():
    pywinauto.keyboard.SendKeys('^v') # Ctrl+V

def randomClickBox(minX, minY, maxX, maxY):
    click(random.randint(minX, maxX), random.randint(minY, maxY))

def randomClick(box):
    if len(box) >= 4:
        click(random.randint(box[0], box[0]+box[2]), random.randint(box[1], box[1]+box[3]))

def random2ClickBox(minX, minY, maxX, maxY):
    doubleclick(random.randint(minX, maxX), random.randint(minY, maxY))

def random2Click(box):
    if len(box) >= 4:
        doubleclick(random.randint(box[0], box[0]+box[2]), random.randint(box[1], box[1]+box[3]))

def randomDelay(min, max): # ms
    time.sleep(random.randint(min, max)/1000)

def delay(t): # ms
    time.sleep(t/1000)

def debug_printTime(tick): # tick is the starting time
    print str(((cv2.getTickCount() - tick)/cv2.getTickFrequency())) + " s" # print elapsed time

def getScreen():
    screen = ig.grab(bbox=[chromeSize[0],chromeSize[1],chromeSize[0]+chromeSize[2],chromeSize[1]+chromeSize[3]]) # get the screen
    return np.array(screen, dtype='uint8').reshape((screen.size[1],screen.size[0],3)) # convert for opencv        

def goToPage(url):
    time.sleep(0.005)
    press('^l')
    pyperclip.copy(url)
    time.sleep(0.005)
    press('^v')
    time.sleep(0.005)
    press('{VK_RETURN}')

def urlMatch(url, template):
    if url.find(template) != -1:
        return True
    return False

def checkChromeSize(hwnd):
    global chromeSize
    size = win32gui.GetWindowRect(hwnd) # get the window position and size
    chromeSize = [size[0], size[1], size[2]-size[0], size[3]-size[1]] # update our global variable

def checkForChrome():
    global chromeFound
    global currentUrl
    chromeFound = False
    hwnd = win32gui.GetForegroundWindow()
    if win32gui.GetWindowText(hwnd).find("- Google Chrome") != -1:
        press('^l') # Ctrl+L (F6 doesn't behave properly in repeated use) to access the URL
        currentUrl = copy()
        if urlMatch(currentUrl, myUrl):
            checkChromeSize(hwnd) # update the size and position
            chromeFound = True
    return chromeFound

def searchImage(filename, threshold=0.95, limit=1):
    template = cv2.imread("data/" + filename,0) # read the image file
    if template is None:
        print "error"
        return [[-1]]

    img = getScreen() # get the screen
    img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY) # convert for opencv
    
    w, h = template.shape[::-1] # get the size
    res = cv2.matchTemplate(img,template,eval('cv2.TM_CCOEFF_NORMED')) # template matching
    loc = np.where(res >= threshold) # 0.9 is the default threshold

    coor = []
    for pt in zip(*loc[::-1]):
        coor.append([pt[0]+chromeSize[0], pt[1]+chromeSize[1], w, h]) # get all the matches and add the window position
        if len(coor) >= limit:
            break

    if len(coor) == 0:
        return [[-1]] # return -1 if empty
    return coor

def searchImageRegion(filename, region, threshold=0.95, limit=1):
    if not isinstance(region, list) or len(region) < 4:
        return [[-1]]
    res = searchImage(filename, threshold, limit)
    if res[0][0] == -1:
        return res
    ok = []
    for i in range(0, len(res)):
        if res[i][0] >= region[0] and res[i][1] >= region[1] and res[i][0]+res[i][2] <= region[0]+region[2] and res[i][1]+res[i][3] <= region[1]+region[3]:
            ok.append(res[i])
    if len(ok) == 0:
        return [[-1]]
    return ok

def findImage(filename, threshold=0.95):
    if searchImage(filename, threshold, 1)[0][0] != -1:
        return True
    return False

def findImageRegion(filename, region, threshold=0.95):
    if searchImageRegion(filename, region, threshold, 1)[0][0] != -1:
        return True
    return False

def clickImage(filename, dClick = False):
    elems = searchImage(filename, 0.95, 1)
    if elems[0][0] != -1:
        if dClick:
            random2Click(elems[0])
        else:
            randomClick(elems[0])
        return True
    return False

def clickImageRegion(filename, region, dClick = False):
    elems = searchImageRegion(filename, region, 0.95, 1)
    if elems[0][0] != -1:
        if dClick:
            random2Click(elems[0])
        else:
            randomClick(elems[0])
        return True
    return False

def waitImage(filename, limit):
    for i in range(0, limit):
        elems = searchImage(filename, 0.95, 1)[0]
        if elems[0] != -1:
            return elems
        delay(100)
    return [-1]

def waitAndClickImage(filename, limit):
    elems = waitImage(filename, limit)
    if elems[0] != -1:
        randomClick(elems)
        return True
    return False

class simpleui(Tkinter.Tk):
    def __init__(self, parent): # the UI is built here
        global logtext
        Tkinter.Tk.__init__(self,parent)
        self.parent = parent
        
        logframe = ttk.Frame(self)
        logframe.grid(row=0, column=0, sticky="nw") # position and width
        logframe.grid_propagate(False)
        scrollbar = Tkinter.Scrollbar(logframe) # the scroll bar
        logtext = Tkinter.Text(logframe, width=55, height=35, state=Tkinter.DISABLED, yscrollcommand=scrollbar.set) # the log box itself
        logtext.pack(side=Tkinter.LEFT, fill=Tkinter.Y, expand=False)
        scrollbar.pack(side=Tkinter.LEFT, fill=Tkinter.Y)
        scrollbar.config(command=logtext.yview)

def updateGui(): # called in the main thread (because Tkinter isn't thread safe)
    global logSize

    if not appRunning: # no update if the app isn't running
        return

    # log update
    logMutex.acquire()
    logtext.configure(state="normal") # state set to normal to write in
    for i in range(0, len(logStrings)):
        logtext.insert(Tkinter.END, logStrings[i]+"\n")
        if logSize > logLimit: # one call = one line, so if the number of line reachs the limit...
            logtext.delete(1.0, 2.0) # delete the oldest line
        else: # else, increase
            logSize += 1
    logtext.configure(state="disabled") # back to read only
    logtext.yview(Tkinter.END) # to the end of the text
    del logStrings[:] # delete the stored lines
    logMutex.release()

def log(text, timestamp=True):
    if not appRunning:
        return
    logMutex.acquire()
    if timestamp: # append to our list of line (see updateGui() for more)
        logStrings.append("[" + strftime("%H:%M:%S") + "] " + text)
    else:
        logStrings.append(text)
    logMutex.release()

def smartlog(text, id, timestamp=True):
    if smartlog.previous == id:
        return
    smartlog.previous = id
    log(text, timestamp)
smartlog.previous = -1

def close(): # called by the app when closed
    global appRunning
    appRunning = False
    app.destroy()

def keyEvent(event):
    global escapeEvent
    global appPaused
    if event.Key == 'Escape':
        escapeEvent = True
    elif event.Key == 'F7':
        appPaused = not appPaused
        if appPaused:
            log("Pause")
        else:
            log("Resume")
    return True

def createGui(name, callback=None):
    global app
    global hm
    app = simpleui(None)
    app.title(name)
    app.resizable(width=False, height=False) # not resizable
    app.protocol("WM_DELETE_WINDOW", close) # call close() if we close the window

    # (Windows only) hook to quit when we hit the escape key
    hm = pyHook.HookManager()
    if callback == None:
        hm.KeyDown = keyEvent # function to be called
    else:
        hm.KeyDown = callback
    hm.HookKeyboard()

def checkEscape():
    if escapeEvent:
        close()