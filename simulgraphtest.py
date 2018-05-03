import sys
import gtk, gobject
import matplotlib
matplotlib.use('GTKAgg')
import pylab as p
import numpy as nx 
import time

import threading 



ax = p.subplot(111)
canvas = ax.figure.canvas

# for profiling
tstart = time.time()

# create the initial line
x = nx.arange(0,2*nx.pi,0.01)
line, = ax.plot(x, nx.sin(x), animated=True)

# save the clean slate background -- everything but the animated line
# is drawn and saved in the pixel buffer background
background = canvas.copy_from_bbox(ax.bbox)


# just a plain global var to pass data (from main, to plot update thread)
global mypass

# http://docs.python.org/library/multiprocessing.html#pipes-and-queues
from multiprocessing import Pipe
global pipe1main, pipe1upd
pipe1main, pipe1upd = Pipe()


# the kind of processing we might want to do in a main() function,
# will now be done in a "main thread" - so it can run in
# parallel with gobject.idle_add(update_line)
def threadMainTest():
    global mypass
    global runthread
    global pipe1main

    print("tt")

    interncount = 1

    while runthread: 
        mypass += 1
        if mypass > 100: # start "speeding up" animation, only after 100 counts have passed
            interncount *= 1.03
        pipe1main.send(interncount)
        time.sleep(0.01)
    return


# main plot / GUI update
def update_line(*args):
    global mypass
    global t0
    global runthread
    global pipe1upd

    if not runthread:
        return False 

    if pipe1upd.poll(): # check first if there is anything to receive
        myinterncount = pipe1upd.recv()

    update_line.cnt = mypass

    # restore the clean slate background
    canvas.restore_region(background)
    # update the data
    line.set_ydata(nx.sin(x+(update_line.cnt+myinterncount)/10.0))
    # just draw the animated artist
    ax.draw_artist(line)
    # just redraw the axes rectangle
    canvas.blit(ax.bbox)

    if update_line.cnt>=500:
        # print the timing info and quit
        print ('FPS:' , update_line.cnt/(time.time()-tstart))

        runthread=0
        t0.join(1)   
        print ("exiting")
        sys.exit(0)

    return True



global runthread

update_line.cnt = 0
mypass = 0

runthread=1

gobject.idle_add(update_line)

global t0
t0 = threading.Thread(target=threadMainTest)
t0.start() 

# start the graphics update thread
p.show()

print ("out" )# will never print - show() blocks indefinitely! 