#!/usr/bin/env python
import PySimpleGUI as sg
import cv2
import numpy as np
import threading

"""
Demo program that displays a webcam using OpenCV
"""

import random
import machine

def main():

    p = machine.Plotter("/dev/ttyUSB1", True)

    sg.theme('Black')

    def mkbtn(key, text=None):
        if text == None:
            text = key
        return sg.pin(sg.Button(text, key=key, size=(4,4), font='Helvetica 14'), shrink=False)

    # controls = sg.Column([ [mkbtn("A0"), mkbtn("A1"), mkbtn("A2"), mkbtn("A3")],
    #                        [mkbtn("B0"), mkbtn("B1"), mkbtn("B2"), mkbtn("B3")],
    #                        [mkbtn("C0"), mkbtn("C1"), mkbtn("C2"), mkbtn("C3")]])

    controls = sg.Column([ [sg.Column([[mkbtn("A0")], [mkbtn("B0", "-x")], [mkbtn("C0")]]),
                            sg.Column([[mkbtn("A1", "+y")], [mkbtn("B1", "H")], [mkbtn("C1", "-y")]]),
                            sg.Column([[mkbtn("A2", "STH")], [mkbtn("B2", "+x")], [mkbtn("C2", "z0")]]),
                            sg.Column([[mkbtn("A3", "+z")], [mkbtn("B3")], [mkbtn("C3", "-z")]])
                        ]])
                           
                        #    mkbtn("A1"), mkbtn("A2"), mkbtn("A3")],
                        #    , mkbtn("B1"), mkbtn("B2"), mkbtn("B3")],
                        #    , mkbtn("C1"), mkbtn("C2"), mkbtn("C3")]])
    
    # define the window layout
    layout = [[sg.Text('OpenCV Demo', size=(40, 1), justification='center', font='Helvetica 20')],
              [sg.Image(filename='', key='image'), controls],
              [sg.Button('Go', size=(10, 1))]]

    # create the window and show it without the plot
    window = sg.Window('Demo Application - OpenCV Integration', layout, location=(800, 400), finalize=True)

    # ---===--- Event LOOP Read and display frames, operate the GUI --- #

    hiddenButtons = "A0 B3 C0".split(" ")
    for b in hiddenButtons:
        window[b].Update(visible=False)

    cap = cv2.VideoCapture("/dev/video16")
    
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
            p.relMode()
            p.g1(y=5)
        elif event == 'C1':
            print("towards")
            p.relMode()
            p.g1(y=-5)
        elif event == 'B0':
            print("left")
            p.relMode()
            p.g1(x=-5)
        elif event == 'B2':
            print("right")
            p.relMode()
            p.g1(x=5)
        elif event == 'A3':
            print("up")
            p.relMode()
            p.g1(z=-0.5)
        elif event == 'C3':
            print("down")
            p.relMode()
            p.g1(z=0.5)
        elif event == 'B1':
            ht = threading.Thread(target=p.home)
            ht.start()
            print("Home")
        elif event == "Go":
            print("Plotting")
            p.plotText("Ben", width=15, spacing=3)
        elif event == "A2":
            print("Set tool height")
            p.absMode()
            p.g1(z=30)
        elif event == "C2":
            print("z0")
            p.absMode()
            p.g1(z=0)

        ret, frame = cap.read()
        imgbytes = cv2.imencode('.png', frame)[1].tobytes()  # ditto
        window['image'].update(data=imgbytes)

main()
