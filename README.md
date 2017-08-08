# Autolib  
Collection of functions that I use for automated tasks (mostly with google chrome).  

# Mouse  
**move**: move the mouse on screen.  
**click**: click on the screen.  
**doubleclick**: double click on the screen.  
**randomClickBox, randomClick, random2ClickBox, random2Click**: click (or double click) randomly in the specified area.  
  
# Keyboard  
**press**: press a key.  
**copy**: do a Ctrl+C, return the clipboard content.  
**paste**: do a Ctrl+V.  
  
# Timing  
**delay**: do a sleep for X milliseconds.  
**randomDelay**: random sleep in the specified interval.  
  
# Screen reading  
**getScreen**: take a screenshot of the current Google Chrome window (see the Google Chrome part).  
**searchImage, searchImageRegion**: search one or multiple matches for a specified image on screen.  
**findImage, findImageRegion**: same as searchImage but return true if one match is found.  
**clickImage, clickImageRegion**: same as searchImage but click on the first match found and return true.  
**waitImage**: wait for an image to appear on screen for a specified amount of time (in 10th of second).  
**waitAndClickImage**: same as waitImage, click on the image if found.  
  
# Google Chrome  
**getScreen**: grab a screenshot of the current chrome window.  
**goToPage**: do a Ctrl+L, paste our URL in the address bar and press return.  
**urlMatch**: check if the last URL found match with our.  
**checkChromeSize**: update the chromeSize global variable.  
**checkForChrome**: check if the current window is a Google Chrome window.  
  
# Others  
**simpleui**: simple Tkinter UI for debug.  
**updateGui**: update the gui, to be called every tick.  
**log**: to fill the gui textbox.  
**smartlog**: same as log but to avoid repeted text.  
**close**: called when the gui is closed.  
**keyEvent**: called when a key is pressed.  
**createGui**: create the gui, set the keyboard hook for keyEvent.  
**checkEscape**: stop our bot if the escape key is pressed (work with keyEvent), to be called every tick.  