import os
import numpy as np

# pscyhopy imports
from psychopy import data, gui, logging
from psychopy import core, event, sound, visual, monitors

import markers 

monitor = monitors.Monitor('viewpixx')
win_size = (1920, 1080)
win_color = 'black'
win = visual.Window(
    size=monitor.getSizePix(), fullscr=False, screen=1, allowGUI=True, allowStencil=False,
    units='pix', monitor=monitor, colorSpace=u'rgb', color=win_color
    )
win.recordFrameIntervals = True

def check_abort(win):
    if event.getKeys(keyList=["escape"]):
        win.close()
        core.quit()

with markers.get_marker('viewpixx', win) as m:

    timer = core.CountdownTimer()

    for i in range(100):

        textstim = visual.TextStim(
            win=win, text=f'{i}',
            ori=0, pos=(0,0), height=32, 
            color='white', colorSpace='rgb',
            opacity=1, 
            )
        
        win.callOnFlip(timer.reset) 
        textstim.draw()
        
        m.send(i)
        win.flip()
        
        timer.add(1)
        while timer.getTime() > 0:
            check_abort(win)

        win.flip()


win.close()
core.quit()   