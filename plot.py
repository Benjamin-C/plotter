import serial
import time
import threading

# ser = None
ser = serial.Serial('/dev/ttyUSB0', 115200)

file = open("text.gcode", "w")

import matplotlib.pyplot as plt
fig,ax = plt.subplots()

xlog = []
ylog = []
xfly = []
yfly = []

robotX = 0
robotY = 0
robotZ = 0

print(ser)

serialReadRunning = True
def readSerial():
    while(serialReadRunning):
        pass
        # print(ser)
        # print(ser.readline())

def g0(x=None, y=None, z=None, e=None, f=None):
    gmove(0, x, y, z, e, f)

def g1(x=None, y=None, z=None, e=None, f=None):
    gmove(1, x, y, z, e, f)

def gmove(gnum, x=None, y=None, z=None, e=None, f=None):
    sx = f" x{x:.1f}" if x != None else ""
    sy = f" y{y:.1f}" if y != None else ""
    sz = f" z{z:.1f}" if z != None else ""
    se = f" e{e:.1f}" if e != None else ""
    sf = f" f{f:d}" if f != None else ""
    cmd(f"g{gnum}{sx}{sy}{sz}{se}{sf}\n")
    global robotX, robotY
    robotX = x if x != None else robotX
    robotY = y if y != None else robotY
    if z != None and z < 0:
        xlog.append(None)
        ylog.append(None)
        xfly.append(robotX)
        yfly.append(robotY)
    if x != None or y != None:
        xlog.append(robotX)
        ylog.append(robotY)
        if xfly[-1] != None:
            xfly.append(robotX)
            yfly.append(robotY)
            xfly.append(None)
            yfly.append(None)

def cmd(c):
    file.write(c)
    if ser != None:
        ser.write(c.encode())
    else:
        print(c[:-1])

# (x, y, liftonredraw)
# If lift is true or omitted, the line will be drawn from the previous point to this point when redraw is enabled.
# If lift is false, the line from the previous point to this point will not be drawn
# Use values from 0-1 as a fraction of the size (width/height) of the character
from linefont import linefont

def writeLetter(l, x, y, z, width=10, height=None, zlift=10, font=None, redraw=False):
    ''' Writes a letter
    
    l is the letter
    x, y, are the x, y, position of the lower left corner of the letter
    z is the z height to draw at
    width is the width in mm, default 10
    height is the height in mm, default (3/2)*width
    zlift is the amount to lift the pen when not drawing, default 10mm
    font is the font to use, default to linefont'''
    if height == None:
        height = width * (4/2)
    if font == None:
        font = linefont
    if l in font:
        g0(z=z-zlift)
        g0((font[l][0][0]*width) + x, (font[l][0][1]*height) + y)
        lifted = True
        for step in font[l]:
            if len(step) > 2 and not (redraw and step[2]):
                if not lifted:
                    g0(z=z-zlift)
                    lifted = True
            else:
                if lifted:
                    g0(z=z)
                    lifted = False
            gmove(0 if lifted else 1, (step[0]*width) + x, (step[1]*height) + y)
        g0(z=z-zlift)
    else:
        print("Letter not in font")
    return (width, height)

if ser != None:
    reader = threading.Thread(target=readSerial)
    reader.start()
    print("Reader started")
    time.sleep(2)

def plotText(text, x, y, width=10, spacing=3, wrapwidth=1e99, delay=0):
    ''' Plots a string of text on the page
    
    text is the string to plot. Unknown characters will be left blank
    x, y is the position to start at
    width is the width of each character, defaults to 10
    spacing is the gap to leave between characters, defaults to 2
    wrapwidth is the width to wrap text to, defaults to 1e99, use large numbers to disable
    '''
    mx = x
    for l in text:
        w, h = writeLetter(l, mx, y, 0, width, redraw=False)
        time.sleep(delay)
        mx += w + spacing
        if mx > x + wrapwidth:
            mx = x
            y -= h + (spacing * (h/w))


print("Plotting")
cmd("g90")
g0(f=100*60)
g0(z=-20)
# ser.write(b"g1 x10 f60000\n\r")
sx = 0
y = 0
width = 12
spacing = 2
x = sx
# plotText("Hello World", 0, 0, 15, 3)
# plotText("ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789abcdefghijklmnopqrstuvwxyz.,+-=_[]()<>{}'\"/\\:;?|!@#$%^&*", 0, 150, wrapwidth=250, delay=0)

plotText("A", 0, 0, 15, 3)

ax.plot(xlog, ylog)
ax.plot(xfly, yfly, alpha=0.25)
xl = ax.get_xlim()
yl = ax.get_ylim()
size = max(xl[1]-xl[0],yl[1]-yl[0])
ax.set_xlim([((xl[0]+xl[1]-size)/2), ((xl[0]+xl[1]+size)/2)])
ax.set_ylim([((yl[0]+yl[1]-size)/2), ((yl[0]+yl[1]+size)/2)])
ax.grid("both")
ax.set_aspect('equal', adjustable='box')
file.close()
plt.savefig("plot.pdf")
# plt.show()

serialReadRunning = False
if ser != None:
    ser.close()
exit()