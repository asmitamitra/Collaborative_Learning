import asyncore
import socket
import time
import thread
from time import *
import threading, urllib2,urllib
import Queue
import sys
from Tkinter import *
import tkFileDialog, Tkconstants
import os
import ttk
from urllib2 import Request, HTTPError, URLError
import httplib
import tkMessageBox
from Tkinter import *

 
def foo1():
  execfile("clr.py")
  
root = Tk()
root.title('Minorrr')
ent = Entry(root,bd =5,width=50)
ent.insert(0, 'KAKKAR :P')               
ent.pack(side=TOP, fill=X)                     
 
btn1 = Button(root, text='SAY HI',command=foo1) 
btn1.pack(side=LEFT)

root.mainloop()