import platform
import cv2
import numpy as np
import socket
import sys
import pickle
import struct, thread
# if OS is Windows
if platform.system() == 'Windows':
	from PIL import ImageGrab
# if OS is Linux
if platform.system() == 'Linux':
	import pyscreenshot as ImageGrab
import time
from PIL import Image
from StringIO import StringIO
import PIL
import pyautogui

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM);

s.bind(('',6009));
s.listen(10);
conn_list=[]

def serverScreenShare(conn) :
	while True:
		imgobj=ImageGrab.grab()
		st = StringIO()
		imgobj=imgobj.resize((1180,620), PIL.Image.ANTIALIAS)
		imgobj.save(st, "JPEG", quality=70, optimize=True, progressive=True)
		print len(st.getvalue())
		conn.send(str(len(st.getvalue())))
		print conn.recv(2);
		conn.send(st.getvalue())   # notify the client of the change
		st.close()
		time.sleep(0.1)
		if conn.recv(2)=="10":
			choice = int(conn.recv(1))
			if choice==1:
				len1 = int(conn.recv(1))
				x1=int(float(conn.recv(len1))*1.15)
				len2=int(conn.recv(1))
				y1=int(float(conn.recv(len2))*1.23)
				print "Coordx",str(x1);
				print "Coord y",str(y1);
				pyautogui.click(x=x1, y=y1)

			elif choice==2:
				len1=int(conn.recv(1));
				x2=int(float(conn.recv(len1))*1.15)
				len2=int(conn.recv(1));
				y2=int(float(conn.recv(len2))*1.23)
				print "Coordx",str(x2);
				print "Coord y",str(y2);
				pyautogui.click(button='right', x=x2, y=y2)
			elif choice==3:
				len1 = int(conn.recv(1))
				x3=int(float(conn.recv(len1))*1.15)
				len2-int(conn.recv(1))
				y3=int(float(conn.recv(len2))*1.23)
				print "Coordx",str(x3);
				print "Coord y",str(y3);
				pyautogui.click(button='left', clicks=2, x=x3, y=y3)
			elif choice==4:
				len1 = int(conn.recv(1))
				keycode=int(conn.recv(len1));
				print chr(keycode);
				pyautogui.typewrite(chr(keycode), interval=0.1);
			




while True:
	conn, addr = s.accept();
	conn_list.append(conn);
	print addr
	thread.start_new(serverScreenShare,(conn,));
	#thread.start_new(mouseMove,(conn,));
