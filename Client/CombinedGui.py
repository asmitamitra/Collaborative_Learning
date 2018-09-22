# 5 buttons on right : 1 - Video Buffering, 2 - Live Lec, 3 -  Regular High Speed Downloader,4 - Bandwidth Downloader, 5 - Chats
# all should start with a list. User should be able to click anything on the list to start one of the things
# video buffering - list of videos available
# live lec should start with list of live lectures going on
# Downloader - files which can be downloaded
# Bandwith Downloader - File and who all are available to share the download
# Chats - list of all clients online

from __future__ import print_function

import wx
from twisted.internet import wxreactor
wxreactor.install()

from twisted.internet import reactor, protocol
from twisted.protocols import basic

import sys, signal,socket,thread,random,os,platform,cv2,pickle,struct
import numpy as np
from Tkinter import Tk
from ClientStreaming import Client
import re
if platform.system() == 'Windows':
	from PIL import ImageGrab
if platform.system() == 'Linux':
	import pyscreenshot as ImageGrab
from PIL import Image
from StringIO import StringIO

from imutils.video import WebcamVideoStream
from imutils.video import FPS
import argparse
import imutils

host = '192.168.43.157'
my_files = []
no_of_threads = 5
client_list = []
live_lec_list = []

if_connected = {
	'downloader' : None,
}

save_list = {
	'downloader' : None,
}
def fetchFile(sock,new_filename):
    	new_file = open(new_filename,'wb')
    	wif = sock.recv(1024)
    	while wif != '':        
        	new_file.write(wif)
		wif = sock.recv(1024)
    	new_file.close()
    	global no_of_threads 
    	no_of_threads -= 1

def start_another_server(filename):
	os.system('python ' + filename)

def screen_client(s,frame):
	while True:
		lent = int(s.recv(6))
		s.send("ok")
		a = s.recv(lent)
		frame.onView(a)
		time.sleep(0.1)

def signal_handler(signal, frame):
    	print ('\nGoodbye!')
    	sys.exit(0)

class LiveLecFrame(wx.Frame):
	def __init__(self,parent,lec_host):
		wx.Frame.__init__(self, parent,title='Live Lecture - (' + lec_host[0] + ' ' + lec_host[1] + ')', size=(400,400))
		self.panel = wx.Panel(self)		
		self.s=socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		self.s.connect((lec_host[0], 2001))
		self.lec_host = lec_host
		self.image = wx.EmptyImage(400,400)		
		self.imageCtrl = wx.StaticBitmap(self.panel,wx.ID_ANY,wx.BitmapFromImage(self.image))
	
	def live_lec_view(self):		
		fps = FPS().start()	
		data = ""
		payload_size = struct.calcsize("L")
		while True:
			while len(data)<payload_size:
				data+=self.s.recv(4096)

			packed_msg_size = data[:payload_size:]
			data = data[payload_size:]
			msg_size = struct.unpack("L", packed_msg_size)[0]

			while len(data)<msg_size:
				data+=self.s.recv(4096)
	
			frame_data = data[:msg_size]
			data = data[msg_size:]	
			frame = pickle.loads(frame_data)
			
			cv2.imshow('Live Lecture - (' + self.lec_host[0] + ' ' + self.lec_host[1] + ')', frame)
			key = cv2.waitKey(1) & 0xFF == ord('q')
			if key:
				self.s.close()
				break
			fps.update()
		cv2.destroyAllWindows()

class ScreenFrame(wx.Frame):
    	def __init__(self, parent,title, sock):
		wx.Frame.__init__(self, parent,title=title, size=(1200,750))
		self.SetCursor(wx.StockCursor(wx.CURSOR_PENCIL))
		self.panel = wx.Panel(self)
		self.panel.SetSize((1180,620))
		self.myWxImage = wx.EmptyImage( 1180, 620 )
		self.imageCtrl = wx.StaticBitmap(self.panel,wx.ID_ANY,wx.BitmapFromImage(self.myWxImage))
		self.NH=0
		self.NW=0
		# hook some mouse events
		self.imageCtrl.Bind(wx.EVT_LEFT_DOWN, lambda event,sock = sock : self.OnLeftDown(event,sock))
		self.imageCtrl.Bind(wx.EVT_RIGHT_DOWN, lambda event,sock = sock : self.OnRightDown(event,sock))
		self.imageCtrl.Bind(wx.EVT_LEFT_DCLICK, lambda event,sock = sock : self.OnLeftDouble(event,sock))
		self.imageCtrl.Bind(wx.EVT_KEY_DOWN, lambda event,sock = sock : self.self.OnKeyPress(event,sock))
		self.Show(True)

    	def OnLeftDown(self, event, s):
		ptx = event.GetX()
		pty = event.GetY()
		print ("x--->" + str(ptx))
		print ("y--->"+str(pty))
		s.send("10")
		s.send("1")
		s.send(str(len(str(ptx))))
		s.send(str(ptx))
		s.send(str(len(str(pty))))
		s.send(str(pty))
        
    
    	def OnRightDown(self, event, s):
		ptx = event.GetX()
		pty = event.GetY()
		print ("x--->" + str(ptx))
		print ("y--->"+str(pty))
		s.send("10")
		s.send("2")
		s.send(str(len(str(ptx))))
		s.send(str(ptx))
		s.send(str(len(str(pty))))
		s.send(str(pty))
        

    	def OnLeftDouble(self, event, s):
		ptx = event.GetX()
		pty = event.GetY()
		print ("x--->" + str(ptx))
		print ("y--->"+str(pty))
		s.send("10")
		s.send("3")
		s.send(str(len(str(ptx))))
		s.send(str(ptx))
		s.send(str(len(str(pty))))
		s.send(str(pty))

    	def OnKeyPress(self, event, s):
		keycode = event.GetKeyCode()
		s.send("10")
		s.send("4")
		print ("adasdf" + str(chr(keycode)))
		s.send(str(len(str(keycode))))
		s.send(str(keycode))
    
    	def onView(self,a):
	    	si=StringIO(a)
	    	im = Image.open(si)
		img=wx.ImageFromBuffer(im.size[0],im.size[1],im.tobytes())
	    	self.NW=1180
	    	self.NH=620
		new_img = wx.BitmapFromImage(img)
		self.imageCtrl.SetBitmap(new_img)
		self.panel.Refresh()
	    	img = img.Scale(1080,720)
	    	si.close()
	
class ChatPersonalFrame(wx.Frame):
    	def __init__(self,ip_port,parent):
        	wx.Frame.__init__(self, parent=parent, title=ip_port)
        	self.ip_port = ip_port
        	self.protocol = None  # twisted Protocol

        	sizer = wx.BoxSizer(wx.VERTICAL)
        	self.text = wx.TextCtrl(self, style=wx.TE_MULTILINE | wx.TE_READONLY)
        	self.ctrl = wx.TextCtrl(self, style=wx.TE_PROCESS_ENTER, size=(300, 25))
        	sizer.Add(self.text, 5, wx.EXPAND)
        	sizer.Add(self.ctrl, 0, wx.EXPAND)
        	self.SetSizer(sizer)
        	self.ctrl.Bind(wx.EVT_TEXT_ENTER, self.send)

    	def send(self,evt):
		message = str(self.ctrl.GetValue())
		self.protocol.sendLine('send ' + self.ip_port + ' ' + message)
		val = self.text.GetValue()
		self.text.SetValue(val + 'You : ' + message + '\n')
		self.text.SetInsertionPointEnd()
		self.ctrl.SetValue("")

class DataForwardingProtocol(basic.LineReceiver):
    	def __init__(self):
        	self.output = None

    	def dataReceived(self, data):
		gui = self.factory.gui
            	gui.protocol = self

        	if 'SERVER MESSAGE' in data:
			if 'Established' in data:
				ip,port = data[data.find("(")+1:data.find(")")].split(',')
				self.factory.personalgui.append(ChatPersonalFrame(ip + ' ' + port,gui))
				self.factory.personalgui[-1].Show()
				self.factory.personalgui[-1].protocol = self

			global client_list
			if 'Online' in data:
				ip,port = data[data.find("(")+1:data.find(")")].split(',')
				client_list.append((ip,port))
			elif 'Offline' in data:
				ip,port = data[data.find("(")+1:data.find(")")].split(',')
				client_list.remove((ip,port))
			elif 'Remote Control Request' in data:
				ip,port = data[data.find("(")+1:data.find(")")].split(',')
				result = gui.panel.ShowQuestion('('+ip+','+port+') want to share screen with you?')
				if result == wx.ID_YES:
					self.sendLine('screen_grant ' + ip + ' ' + port)
				elif result == wx.ID_NO:
					self.sendLine('screen_not_grant ' + ip + ' ' + port)
			elif 'Remote Control Grant' in data:
				thread.start_new(start_another_server,('serscreen.py',))
				ip,port = data[data.find("(")+1:data.find(")")].split(',')
				self.sendLine('screen_server_created ' + ip + ' ' + port)
			
			elif 'Remote Control Not Grant' in data:
				gui.panel.ShowMessage('('+ip+','+port+') is unavailable right now')
			
			elif 'Server Created' in data:
				ip,port = data[data.find("(")+1:data.find(")")].split(',')
				s=socket.socket(socket.AF_INET, socket.SOCK_STREAM)
				print ("Socket created")
				s.connect((ip,6009))
				print ("connected")
				screen_app = wx.App(False)
				frame = ScreenFrame(gui,'Screen Sharing - (' + ip + ' ' + port +')', s)				
				thread.start_new(screen_client,(s,frame,))
				screen_app.MainLoop()

			elif 'New Live Lecture' in data:
				ip,port = data[data.find("(")+1:data.find(")")].split(',')
				live_lec_list.append((ip,port))
	
			else:
				for m in re.finditer('\([0-9.,]+\)',data):
					ip,port = data[m.start()+1:m.end()-1].split(',')
					client_list.append((ip,port))
				for m in re.finditer('\{[0-9.,]+\}',data):
					ip,port = data[m.start()+1:m.end()-1].split(',')
					live_lec_list.append((ip,port))
        	else:
            		for pgui in self.factory.personalgui:
                		ip,port = data[data.find("(")+1:data.find(")")].split(',')
                		if pgui and pgui.ip_port == (ip + ' ' + port):
                    			val = pgui.text.GetValue()
                    			pgui.text.SetValue(val + data)
                    			pgui.text.SetInsertionPointEnd()

    	def connectionMade(self):
		pass

class ChatFactory(protocol.ClientFactory):
    	def __init__(self, gui):
        	self.personalgui = []
        	self.gui = gui
        	self.protocol = DataForwardingProtocol

    	def clientConnectionLost(self, transport, reason):
        	reactor.stop()
    	def clientConnectionFailed(self, transport, reason):
        	reactor.stop()


class GUIPanel(wx.Panel):
    	def __init__(self,parent):
		wx.Panel.__init__(self, parent)
		self.frame = parent
		self.labels = []
		
		self.mainSizer = wx.BoxSizer(wx.VERTICAL)
		controlSizer = wx.BoxSizer(wx.HORIZONTAL)
		self.widgetSizer = wx.BoxSizer(wx.VERTICAL)
	 
		self.see_video_button = wx.Button(self, -1, 'See Recorded Videos',size = (250, 40))
		self.see_video_button.Bind(wx.EVT_BUTTON, self.see_video)
		controlSizer.Add(self.see_video_button, 0, wx.CENTER|wx.ALL, 5)
		
		self.live_lec_button = wx.Button(self, -1, 'Live Lectures',size = (250, 40))
		self.live_lec_button.Bind(wx.EVT_BUTTON, self.live_lectures)
		controlSizer.Add(self.live_lec_button, 0, wx.CENTER|wx.ALL, 5)

		self.downloader_button = wx.Button(self, -1, 'Download Files',size = (250, 40))
		self.downloader_button.Bind(wx.EVT_BUTTON, self.download_file)
		controlSizer.Add(self.downloader_button, 0, wx.CENTER|wx.ALL, 5)

		self.shared_downloader_button = wx.Button(self, -1, 'Download Files with Help',size = (250, 40))
		#self.shared_downloader_button.Bind(wx.EVT_BUTTON, self.download_file)
		controlSizer.Add(self.shared_downloader_button, 0, wx.CENTER|wx.ALL, 5)

		self.see_other_client_button = wx.Button(self, -1, 'See Other Clients',size = (250, 40))
		self.see_other_client_button.Bind(wx.EVT_BUTTON, self.see_clients)
		controlSizer.Add(self.see_other_client_button, 0, wx.CENTER|wx.ALL, 5)

		self.mainSizer.Add(controlSizer, 0, wx.CENTER)
       		self.mainSizer.Add(self.widgetSizer, 0, wx.CENTER|wx.ALL, 10)
 
        	self.SetSizer(self.mainSizer)
	
	def ShowMessage(self, message):
        	dial = wx.MessageDialog(None, message, 'Info', wx.OK)
        	result = dial.ShowModal()

    	def ShowQuestion(self, message):
        	dial = wx.MessageDialog(None, message, 'Question', wx.YES_NO | wx.NO_DEFAULT | wx.ICON_QUESTION)
        	result = dial.ShowModal()
		return result

    	def destroy_widget_panel(self):
		self.widgetSizer.Clear(True)
	
	def live_lectures(self,event):
		self.destroy_widget_panel()
		new_button = wx.Button(self, -1, 'Take A Lecture Now')
		new_button.Bind(wx.EVT_BUTTON, self.start_live_lecture)
		self.widgetSizer.Add(new_button, 0, wx.ALL, 5)
		global live_lec_list
		for a_client in live_lec_list:
			childSizer = wx.BoxSizer(wx.HORIZONTAL)
			text = wx.StaticText(self,-1,'', style=wx.ALIGN_CENTRE)
            		text.SetLabel(str(a_client))
            		new_button = wx.Button(self, -1, 'Join this Lecture')
			new_button.Bind(wx.EVT_BUTTON, lambda event,temp = a_client : self.join_live_lecture(event,temp))
			childSizer.Add(text, 0, wx.ALL, 5)
            		childSizer.Add(new_button, 0, wx.ALL, 5)
			self.widgetSizer.Add(childSizer, 0, wx.ALL, 5)           		
			self.frame.fSizer.Layout()
            		self.frame.Fit()

	def start_live_lecture(self,event):
		thread.start_new(start_another_server,('fps_demo.py',))
		self.frame.protocol.sendLine('new_live_lec 0 0')

	def join_live_lecture(self,event,a_client):
		live_lec_frame = LiveLecFrame(self.frame,a_client)
		#live_lec_frame.Show()
		live_lec_frame.live_lec_view()
	
	def see_clients(self,event):	
		self.destroy_widget_panel()
		global client_list
		for a_client in client_list:
			childSizer = wx.BoxSizer(wx.HORIZONTAL)
			text = wx.StaticText(self,-1,'', style=wx.ALIGN_CENTRE)
            		text.SetLabel(str(a_client))
            		new_button = wx.Button(self, -1, 'Chat')
			new_button.Bind(wx.EVT_BUTTON, lambda event,temp = a_client : self.rest_chatting(event,temp))
			another_button = wx.Button(self, -1, 'Screen Sharing')
			another_button.Bind(wx.EVT_BUTTON, lambda event,temp = a_client : self.rest_screen_sharing(event,temp))
			childSizer.Add(text, 0, wx.ALL, 5)
            		childSizer.Add(new_button, 0, wx.ALL, 5)
			childSizer.Add(another_button,0,wx.ALL,5)
			self.widgetSizer.Add(childSizer, 0, wx.ALL, 5)           		
			self.frame.fSizer.Layout()
            		self.frame.Fit()

	def rest_chatting(self,event,a_client):
		ip_port = a_client[0] + ' ' + a_client[1]
		self.frame.protocol.sendLine('start ' + ip_port)


	def rest_screen_sharing(self,event,a_client):
		ip_port = a_client[0] + ' ' + a_client[1]
		self.frame.protocol.sendLine('screen_request ' + ip_port)

	def see_clients(self,event):	
		self.destroy_widget_panel()
		global client_list
		for a_client in client_list:
			childSizer = wx.BoxSizer(wx.HORIZONTAL)
			text = wx.StaticText(self,-1,'', style=wx.ALIGN_CENTRE)
            		text.SetLabel(str(a_client))
            		new_button = wx.Button(self, -1, 'Chat')
			new_button.Bind(wx.EVT_BUTTON, lambda event,temp = a_client : self.rest_chatting(event,temp))
			another_button = wx.Button(self, -1, 'Screen Sharing')
			another_button.Bind(wx.EVT_BUTTON, lambda event,temp = a_client : self.rest_screen_sharing(event,temp))
			childSizer.Add(text, 0, wx.ALL, 5)
            		childSizer.Add(new_button, 0, wx.ALL, 5)
			childSizer.Add(another_button,0,wx.ALL,5)
			self.widgetSizer.Add(childSizer, 0, wx.ALL, 5)           		
			self.frame.fSizer.Layout()
            		self.frame.Fit()

	def download_file(self,event):
		self.destroy_widget_panel()
		port = 4000
	    	if not if_connected['downloader']:
			sock = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
			sock.connect((host,port))
			if_connected['downloader'] =  sock
			
			file_list = sock.recv(1024).split(',')
			save_list['downloader'] = file_list
		else:
			sock = if_connected['downloader']
			file_list = save_list['downloader']
	    	
		for a_file in file_list:
            		text = wx.StaticText(self,-1,"", style=wx.ALIGN_CENTRE)
            		text.SetLabel(a_file)
            		new_button = wx.Button(self, -1, 'Download')
			new_button.Bind(wx.EVT_BUTTON, lambda event,temp = a_file : self.rest_of_simple_downloading(event,sock,temp))
            		self.widgetSizer.Add(text, 0, wx.ALL, 5)
            		self.widgetSizer.Add(new_button, 0, wx.ALL, 5)
            		self.frame.fSizer.Layout()
            		self.frame.Fit()

	def rest_of_simple_downloading(self,event,sock,filename):		
		global my_files    	        
		my_sockets = []
                sock.send(filename)
		ports_to_connect = sock.recv(1024).split()

		for i in range(5):
			my_sockets.append(socket.socket(socket.AF_INET,socket.SOCK_STREAM))
			my_sockets[-1].connect((host,int(ports_to_connect[i])))
			new_filename = str(i)+'.temp'       
			my_files.append(new_filename)
			thread.start_new(fetchFile,(my_sockets[-1],new_filename,))
	    
		global no_of_threads
		while no_of_threads > 0:
			pass

		data = ''
		for file_name in my_files:
			new_file = open(file_name,'rb')
			data += new_file.read()
			new_file.close()
			os.remove('./'+file_name)

		fetched_file = open(filename,'wb')
		fetched_file.write(data)
		fetched_file.close()
		
		self.ShowMessage('Download Complete')
		my_files = []
		no_of_threads = 5

class GUIFrame(wx.Frame):
	def __init__(self):
		wx.Frame.__init__(self, parent=None, title="Collaborative Learning")
		self.protocol = None
		self.fSizer = wx.BoxSizer(wx.VERTICAL)
		self.panel = GUIPanel(self)
		self.fSizer.Add(self.panel, 1, wx.EXPAND)
		self.SetSizer(self.fSizer)
		self.Fit()
		self.Show()

if __name__ == '__main__':
	app = wx.App(False)
	frame = GUIFrame()
	frame.Show()
	frame.Maximize(True)
	reactor.registerWxApp(app)
      	reactor.connectTCP(host, 5000, ChatFactory(frame))
      	reactor.run()
