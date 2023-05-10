#!/usr/bin/env python
import PySimpleGUI as sg
import cv2
import numpy as np
import threading
import bencvlib
import time
import platform

"""
Demo program that displays a webcam using OpenCV
"""

import random
import machine

camport = None
serport = None

if platform.system() == 'Linux':
    camport = "/dev/video16"
    serport = "/dev/ttyUSB0"
elif platform.system() == 'Darwin':
    camport = "/dev/ttyS016"
    serport = "/dev/tty.usbserial-DN02K2C4"

def main():

    p = machine.Plotter(serport, True)
    p.readPos()

    sg.theme('Black')

    def mkbtn(key, text=None):
        if text == None:
            text = key
        return sg.pin(sg.Button(text, key=key, size=(5,5), font='Helvetica 14'), shrink=False)

    controls = sg.Column([ [sg.Column([[mkbtn("A0", "Slow")], [mkbtn("B0", "-x")], [mkbtn("C0", "Fast")]]),
                            sg.Column([[mkbtn("A1", "+y")], [mkbtn("B1", "H")], [mkbtn("C1", "-y")]]),
                            sg.Column([[mkbtn("A2", "STH")], [mkbtn("B2", "+x")], [mkbtn("C2", "Center")]]),
                            sg.Column([[mkbtn("A3", "+z")], [mkbtn("B3", "z0")], [mkbtn("C3", "-z")]]),
                            sg.Column([[sg.Text('X step', size =(5, 1)), sg.InputText(size =(5, 1), key="stepx")], [sg.Text('Y step', size =(5, 1)), sg.InputText(size =(5, 1), key="stepy")], [sg.Text('Z step', size =(5, 1)), sg.InputText(size =(5, 1), key="stepz")], [sg.Text('Feed', size =(5, 1)), sg.InputText(size =(5, 1), key="feed")]])
                        ]])
    
    # define the window layout
    layout = [[sg.Text('OpenCV Demo', size=(40, 1), justification='center', font='Helvetica 20')],
              [sg.Image(filename='', key='image'), controls],
              [sg.Button('Go', size=(10, 1)), sg.Text("000.000", key="posx"), sg.Text("000.000", key="posy"), sg.Text("000.000", key="posz"), sg.Text("Status: ", key="status")],
              [sg.Text("Thresh", size=(6, 1)), sg.Slider(range=(0, 255), default_value=75, expand_x=True, enable_events=True, orientation='horizontal', key='threshslider')],
              [sg.Text("Blur", size=(6, 1)), sg.Slider(range=(0, 255), default_value=11, expand_x=True, enable_events=True, orientation='horizontal', key='blurslider')],
              [sg.Image(filename='', key='image2')]]

    # create the window and show it without the plot
    window = sg.Window('Demo Application - OpenCV Integration', layout, location=(800, 400), finalize=True)

    # ---===--- Event LOOP Read and display frames, operate the GUI --- #

    # hiddenButtons = "C2 none".split(" ")
    # for b in hiddenButtons:
    #     if b in window:
    # window["C2"].Update(visible=False)

    cap = cv2.VideoCapture(camport)

    def setSlowSpeed():
        window['stepx'].update(value=f"5")
        window['stepy'].update(value=f"5")
        window['stepz'].update(value=f"0.5")
        window['feed'].update(value="1200")

    def setFastSpeed():
        window['stepx'].update(value=f"25")
        window['stepy'].update(value=f"25")
        window['stepz'].update(value=f"5")
        window['feed'].update(value="60000")

    def move(dir, mul, vals):
        if dir in "xyz":
            print("Read values")
            try:
                step = float(vals["step" + dir]) * mul
                speed = float(vals["feed"])
                p.relMode()
                p.cmd(f"{dir}{step:.1f} f{speed:.0f}")
            except Exception as e:
                print("Something is wrong!")
                print(e)
        else:
            print("Invalid dir")

    setSlowSpeed()

    def waitForDone(sleep=0, waitForPlotter=True):
        if waitForPlotter:
            p.waitForDistZero()
        time.sleep(sleep)

    doingCenterMove = False
    centerMoveSize = 16
    origCenterMoveSize = 16
    centerWaitThread = None

    while True:
        event, values = window.read(timeout=20)
        if event == 'Exit' or event == sg.WIN_CLOSED:
            return

        elif event == 'Record':
            recording = True

        elif event == 'Stop':
            recording = False
            img = np.full((480, 640), 255)
            # this is faster, shorter and needs less includes
            imgbytes = cv2.imencode('.png', img)[1].tobytes()
            window['image'].update(data=imgbytes)

        elif event == 'A1':
            print("away")
            move("y", 1, values)
        elif event == 'C1':
            print("towards")
            move("y", -1, values)
        elif event == 'B0':
            print("left")
            move("x", -1, values)
        elif event == 'B2':
            print("right")
            move("x", 1, values)
        elif event == 'A3':
            print("up")
            move("z", 1, values)
        elif event == 'C3':
            print("down")
            move("z", -1, values)
        elif event == 'B1':
            ht = threading.Thread(target=p.home)
            ht.start()
            print("Home")
        elif event == "Go":
            print("Plotting")
            p.relMode()
            p.g1(x=62.9, y=17.4, f=60000)
            p.plotText("A", width=15, spacing=3)
        elif event == "A2":
            print("Set tool height")
            p.absMode()
            p.g1(z=30)
        elif event == "B3":
            print("z0")
            p.absMode()
            p.g1(z=0)
        elif event == "A0":
            setSlowSpeed()
        elif event == "C0":
            setFastSpeed()
        elif event == "C2":
            centerMoveSize = origCenterMoveSize * 2
            doingCenterMove = True

        ret, frame = cap.read()

        if frame is not None:

            grayImage = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            thresh = int(values["threshslider"])
            blur = int(values["blurslider"])
            grayImage = cv2.medianBlur(grayImage, 1+((blur//2)*2))
            cX, cY, img, = bencvlib.findCenter(grayImage, thresh)
            cv2.circle(frame, (cX, cY), 5, (255, 0, 255), -1)

            # Getting the height and width of the image
            height = frame.shape[0]
            width = frame.shape[1]
            midx = width//2
            midy = height//2

            if doingCenterMove:
                if centerWaitThread is None or not centerWaitThread.is_alive():
                    if centerMoveSize > 0.1:
                        centerMoveSize /= 2
                        gx = 0
                        gy = 0
                        if cX > midx:
                            gx = centerMoveSize
                        else:
                            gx = -centerMoveSize
                        if cY > midy:
                            gy = -centerMoveSize
                        else:
                            gy = centerMoveSize
                        print(f"Centering {centerMoveSize}")
                        p.moveRel(gx, gy)
                        if centerMoveSize > 1:
                            centerWaitThread = threading.Thread(target=waitForDone, args=(1,))
                        else:
                            centerWaitThread = threading.Thread(target=waitForDone, args=(2,False))
                        centerWaitThread.start()
                    else:
                        doingCenterMove = False
                        centerMoveSize = 999

            # Drawing the lines
            cv2.line(frame, (width//2, 0), (width//2, height), (64, 64, 64), 1)
            cv2.line(frame, (0, height//2), (width, height//2), (64, 64, 64), 1)

            imgbytes = cv2.imencode('.png', frame)[1].tobytes()  # ditto
            window['image'].update(data=imgbytes)

            imgbytes2 = cv2.imencode('.png', img)[1].tobytes()  # ditto
            window['image2'].update(data=imgbytes2)

        x,y,z = p.getPos()
        window['posx'].update(value=f"x:{x:7.3f}")
        window['posy'].update(value=f"y:{y:7.3f}")
        window['posz'].update(value=f"z:{z:7.3f}")

        if p.broken:
            window['status'].update(value="Status: Broke")
        else:
            if doingCenterMove:
                window['status'].update(value=f"Status: Centering {centerMoveSize:.2g}")
            else:
                window['status'].update(value="Status: Ready")

main()
exit()
