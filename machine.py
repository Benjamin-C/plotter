import serial
import time
import threading
import matplotlib.pyplot as plt
from linefont import linefont
import re

if __name__ == "__main__":
    import opencvtest

class Plotter():

    def __init__(self, port, printSer=False):
        # ser = None
        self._ser = serial.Serial(port, 115200)

        self.printSer = printSer

        self._file = open("text.gcode", "w")

        self._robotX = 0
        self._robotY = 0
        self._robotZ = 0

        self._xlog = []
        self._ylog = []
        self._xfly = [0]
        self._yfly = [0]

        self._readyEvent = threading.Event()
        self._okEvent = threading.Event()
        self._distZeroEvent = threading.Event()
        self._runningEvent = threading.Event()
        self._runningEvent.set()

        self._serin = []

        self.broken = False

        if self._ser != None:
            self._reader = threading.Thread(target=self.readSerial)
            self._reader.start()
            # print("Reader started")
            time.sleep(2)
        print("Ready")

    def readSerial(self):
        while(self._runningEvent.is_set()):
            # pass
            # print(ser)
            if self._ser != None:
                try:
                    start = time.time()
                    line = self._ser.readline()
                    end = time.time()
                    # print("Time: " + str(end - start))
                except Exception:
                    print("Something went wrong, serial closing!")
                    return
                if line != None:
                    line = line.decode()[:-1]
                    if '"stat":3' in line or 'stat:3' in line:
                        self._readyEvent.set()
                        print("[~~] Found done")
                    if "ok>" in line:
                        self._okEvent.set()
                        print("[~~] Found OK")
                    if 'dist:0' in line:
                        self._distZeroEvent.set()
                        print("[~~] Found dist:0")
                    self._serin.append(line)
                    if self.printSer:
                        print("[<-]", line)
                    if "posx" in line:
                        self._robotX = float(re.search("([0-9]+)(\.+)([0-9]+)", line.split("posx")[1])[0])
                    if "posy" in line:
                        self._robotY = float(re.search("([0-9]+)(\.+)([0-9]+)", line.split("posy")[1])[0])
                    if "posz" in line:
                        self._robotZ = float(re.search("([0-9]+)(\.+)([0-9]+)", line.split("posz")[1])[0])
                    if '"st":204' in line:
                        self.broken = True
                    
            else:
                print("ser was none")
                time.sleep(1)
        print("Closing")
        self._runningEvent.set()

    def getPos(self):
        return self._robotX, self._robotY, self._robotZ

    def readPos(self):
        if self._ser != None:
            while self._ser.in_waiting:
                pass
        self._serin = [""]
        print(len(self._serin))
        self.cmd("?")
        print(self._serin)
        while "ok>" not in self._serin[-1]:
            pass

        def prepLine(line):
            parts = line.split(" ")
            ret = []
            for part in parts:
                if part != "":
                    ret.append(part)
            return ret

        print("Parsing ...")
        for line in self._serin:
            parts = prepLine(line)
            if len(line) > 2:
                if parts[0] == "X":
                    self._robotX = float(parts[2])
                if parts[0] == "Y":
                    self._robotY = float(parts[2])
                if parts[0] == "Z":
                    self._robotZ = float(parts[2])
        print(f"Done {self._robotX:.1f},{self._robotY:.1f},{self._robotZ:.1f}")

    def home(self):
        print("Homing")
        self.cmd("g28.2 z0")
        self.waitForCompletion()
        self.cmd("g28.2 x0")
        self.waitForCompletion()
        self.cmd("g28.2 y0")
        self.waitForCompletion()
        self.g0(0, 0, 0)
        self.waitForCompletion()
        self._robotX = 0
        self._robotY = 0
        self._robotZ = 0

    def g0(self, x=None, y=None, z=None, e=None, f=None):
        self.gmove(0, x, y, z, e, f)

    def g1(self, x=None, y=None, z=None, e=None, f=None):
        self.gmove(1, x, y, z, e, f)

    def gmove(self, gnum, x=None, y=None, z=None, e=None, f=None):
        sx = f" x{x:.1f}" if x != None else ""
        sy = f" y{y:.1f}" if y != None else ""
        sz = f" z{z:.1f}" if z != None else ""
        se = f" e{e:.1f}" if e != None else ""
        sf = f" f{f:d}" if f != None else ""
        self.cmd(f"g{gnum}{sx}{sy}{sz}{se}{sf}")
        self._robotX = x if x != None else self._robotX
        self._robotY = y if y != None else self._robotY
        if z != None and z < 0:
            self._xlog.append(None)
            self._ylog.append(None)
            self._xfly.append(self._robotX)
            self._yfly.append(self._robotY)
        if x != None or y != None:
            self._xlog.append(self._robotX)
            self._ylog.append(self._robotY)
            if self._xfly[-1] != None:
                self._xfly.append(self._robotX)
                self._yfly.append(self._robotY)
                self._xfly.append(None)
                self._yfly.append(None)

    def moveRel(self, x=None, y=None, z=None, f=None, fast=True):
        self.relMode()
        self.gmove(1 if fast else 0, x, y, z, f)
        self.absMode()

    def cmd(self, c=""):
        self._file.write(c)
        if self.printSer:
            print("[->]", c)
        if self._ser != None:
            self._ser.write((c+"\n").encode())

    def absMode(self):
        self.cmd("g90")

    def relMode(self):
        self.cmd("g91")

    # (x, y, liftonredraw)
    # If lift is true or omitted, the line will be drawn from the previous point to this point when redraw is enabled.
    # If lift is false, the line from the previous point to this point will not be drawn
    # Use values from 0-1 as a fraction of the size (width/height) of the character

    def writeLetter(self, l, x, y, z, width=10, height=None, zlift=10, font=None, redraw=False, writespd=60000, travelspd=60000):
        ''' Writes a letter
        
        l is the letter
        x, y, are the x, y, position of the lower left corner of the letter
        z is the z height to draw at
        width is the width in mm, default 10
        height is the height in mm, default (3/2)*width
        zlift is the amount to lift the pen when not drawing, default 10mm
        font is the font to use, default to linefont'''
        self.absMode()
        if height == None:
            height = width * (4/2)
        if font == None:
            font = linefont
        if l in font:
            self.g0(z=z-zlift, f=travelspd)
            self.g0((font[l][0][0]*width) + x, (font[l][0][1]*height) + y, f=travelspd)
            lifted = True
            for step in font[l]:
                if len(step) > 2 and not (redraw and step[2]):
                    if not lifted:
                        self.g0(z=z-zlift, f=travelspd)
                        lifted = True
                else:
                    if lifted:
                        self.g0(z=z, f=travelspd)
                        lifted = False
                self.gmove(0 if lifted else 1, (step[0]*width) + x, (step[1]*height) + y, f=(travelspd if lifted else writespd))
            self.g0(z=z-zlift, f=travelspd)
        else:
            print("Letter not in font")
        return (width, height)

    def plotText(self, text, x=None, y=None, width=10, spacing=3, wrapwidth=1e99, delay=0):
        ''' Plots a string of text on the page
        
        text is the string to plot. Unknown characters will be left blank
        x, y is the position to start at, defaults to current machine position
        width is the width of each character, defaults to 10
        spacing is the gap to leave between characters, defaults to 2
        wrapwidth is the width to wrap text to, defaults to 1e99, use large numbers to disable
        '''

        self.readPos()
        if x == None:
            x = self._robotX
        if y == None:
            y = self._robotY
            
        mx = x
        for l in text:
            w, h = self.writeLetter(l, mx, y, 30, width=width, redraw=False)
            self.waitForCompletion()
            # time.sleep(delay)
            mx += w + spacing
            if mx > x + wrapwidth:
                mx = x
                y -= h + (spacing * (h/w))

    def waitForCompletion(self):
        print("[##] Waiting for completion ...")
        self._readyEvent.wait()
        time.sleep(0.1)
        self._readyEvent.clear()
        print("[##] Done waiting for completion ")

    def waitForOK(self):
        print("[##] Waiting for OK ...")
        self._okEvent.wait()
        time.sleep(0.1)
        self._okEvent.clear()
        print("[##] Done waiting for OK ")

    def waitForDistZero(self):
        print("[##] Waiting for dist:0 ...")
        self._distZeroEvent.wait()
        time.sleep(0.1)
        self._distZeroEvent.clear()
        print("[##] Done waiting for dist:0 ...")

    def plotPreview(self):
        fig,ax = plt.subplots()
        ax.plot(self._xlog, self._ylog)
        ax.plot(self._xfly, self._yfly, alpha=0.25)
        xl = ax.get_xlim()
        yl = ax.get_ylim()
        size = max(xl[1]-xl[0],yl[1]-yl[0])
        ax.set_xlim([((xl[0]+xl[1]-size)/2), ((xl[0]+xl[1]+size)/2)])
        ax.set_ylim([((yl[0]+yl[1]-size)/2), ((yl[0]+yl[1]+size)/2)])
        ax.grid("both")
        ax.set_aspect('equal', adjustable='box')
        plt.savefig("plot.pdf")
        # plt.show()

    def savegcode(self):
        self._file.close()

    def close(self):
        if self._ser != None:
            self._runningEvent.clear()
            self._runningEvent.wait()
            self._ser.close()