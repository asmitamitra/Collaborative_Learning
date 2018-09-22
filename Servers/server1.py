import asyncore
import socket
import time
import thread
from time import *
import threading, urllib2,urllib
import Queue                      #redundant!
import sys
from Tkinter import *
import tkFileDialog
import os
import ttk
from urllib2 import Request
import tkMessageBox
no_of_connections=0
no_of_acceptance=0
start_flag = False;
connect_flag = False;
request_flag=False;
url1=""
win = Tk()
win.title('minor wala kaam')

def run_thread(a) :
  print "asmita"
  asyncore.loop()
  
class GuiPart:
  def __init__(self, master, queue, endCommand):
    self.queue = queue
    self.L2 = Label(master, text="Destination path")
    self.L2.grid( row=1, column=0, sticky = W, padx=10, pady=10)
    self.v = StringVar()
    self.E2 = Entry(master, bd =5,textvariable=self.v,width=50)
    self.E2.grid( row=1, column=1, padx=2, pady=10)
    self.dir_opt = options = {}
    options['initialdir'] = 'C:\\'
    options['mustexist'] = False
    options['parent'] = master
    options['title'] = 'Select Location:'
    self.B1=Button(master, text='Browse',command=self.askdirectory,bd=2)
    self.B1.grid( row=1, column=2, padx=6, pady=0, sticky= E )
    self.B2=Button(master, text='Connect',command=self.start_pushed)
    self.B2.grid( row=3, column=1, padx=4, pady=10 )
    self.B3=Button(master, text='Start Download',command=self.start_download)
    self.B3.grid( row=5, column=1, padx=4, pady=10 )
    self.master=master

  def askdirectory(self):
    #called jab directory change krne wale button pr click ho...Browse pr
    (self.v).set(tkFileDialog.askdirectory(**self.dir_opt)) #set k andar jo hai vo dhund kr directory jo milegi, uska path dega and v will set its value in the text wala field
    
  def start_download(self):
    global start_flag, should_proceed
    start_flag = True
    should_proceed=True

  def start_pushed(self):                 #..........................shifted to the other place. jab koi client request bhejegaa..........
    global url1
    if len(url1)!=0 and len(self.v.get())!=0:
      print url1
      try:
        temp=urllib.urlopen(url1)
        print temp
      except:
        print "\n\n-----URL invalid------\n\n"
        tkMessageBox.showinfo("Error", "URL invalid")
      else:
        global connect_flag
        connect_flag = True
    else:
      print "\n\n-----URL and directory can't be empty------\n\n"
      tkMessageBox.showinfo("Error", "URL and directory can't be empty")
reqby=()
getaccess=True;
count_conn = 0
lol=[]   #.........................................to connect to all client sockets connected,........................................
# ...........................................basically jo bhi kaam pehle UI me kr rhe they like jo bhi connected clients hai,...........
#.............................. uski value, to get the value of client wanting the download to happen................

class ThreadedClient:

  def __init__(self, master):
    self.master = master
    self.queue = Queue.Queue()
    self.gui = GuiPart(master, self.queue, self.endApplication)
    self.running = 1

  #def workerThread1(self):
   # while self.running:
    #  sleep(2 * 0.3)
     # msg = 2
      #self.queue.put(msg)

  def endApplication(self):
    self.running = 0

def run_thread_gui(a) :
  global client
  print "shreya1"
  client = ThreadedClient(win)  
  print "shreya2"
  win.mainloop()

class EchoHandler(asyncore.dispatcher):
  def __init__(self,conn_sock, client_address,count_conn):
    self.Rep=Reply()
    self.CA = client_address
    self.conn_sock1=conn_sock
    self.cl_no=count_conn
    self.DATA = ''
    self.sizeToDownload=0
    self.acceptance=-1
    self.out_buffer = ''
    self.BUFFER = 1024
    self.is_writable = False
    self.sock = conn_sock
    asyncore.dispatcher.__init__(self, conn_sock)
    self.downloadedTillNow=0
    #self.started=0
    self.getaccess1=True        #............decide krega ki ye part lega download me ya nahi.......................
    self.i=0

  def handle_read(self):
    print "in here :P"
    global reqby
    global url1
    global request_flag
    global lol
    data = self.recv(1024*1024)
    if data:
      if self.acceptance==5:
        print "here we go ale ale ale"
        url1=data
        print "url1"+url1
        self.acceptance=-1
#...............................back to being a normal client........................
      #############################LATER DEKHNA HAI KI FOR A WRONG URL CHANGES HO JAYE#########################
      if data=="Start Transfer" and not(request_flag):
        print "hi shreya"
        request_flag=True
        self.acceptance=5 #..(CHECK LATER PROBLEM SORTED MAYBE)  baaki log khud se nahi bhej sakte kuch bhi agar request na kia jaye unse to koi faeda nahi yaha na.... 
        reqby=self.CA
        print "request from"+ repr(reqby)+"accepted"
        self.i=lol.index(self.conn_sock1)
        self.Rep.positive(self.i,"Send URL")
#.....................Acceptance ka check......check krna hai pakka..................REMEMBER!!!!!!!!!!!!!!!!!


      elif data=="Start Transfer":
        getaccess=False
        self.getaccess1=False
        print "request from"+ repr(self.CA)+"rejected"
        self.i=lol.index(self.conn_sock1)
        self.Rep.positive(self.i,"Reject")
#.....................Rejection ka check......check krna hai pakka..................REMEMBER!!!!!!!!!!!!!!!!!


      
      if self.acceptance==3:
        self.DATA+=data
      if data=="Sending data":
        self.acceptance=3
        self.Rep.positive(self.i,"Faltoo :P")

      if self.acceptance==2:
        self.downloadedTillNow+=int(data)
        print "\n---------Client ",self.cl_no," -- Downloaded till now = ",self.downloadedTillNow,"----\n"
        #if self.started==0 :
         # self.started=1
     
#....................Would you like to help in download ka response...................DONE HAI,NO CHANGES..!!!!!!!!!!!....
      if data=="acceptance=1":
        self.acceptance=1
      if data=="acceptance=0":
        self.acceptance=0

class EchoServer(asyncore.dispatcher):
  clients = {}
  clients_handler = []
  def __init__(self, host, port):
    asyncore.dispatcher.__init__(self)
    self.create_socket(socket.AF_INET, socket.SOCK_STREAM)
    self.set_reuse_addr()  # to mark socket as reusable
    self.bind((host, port))
    self.listen(5)
    self.obuffer = []

  def handle_accept(self):
    global lol
    pair = self.accept()
    if pair is None:
      pass
      print "here"
    else:
      print "there"
      sock, addr = pair
      EchoServer.clients[sock] = addr
      global count_conn
      count_conn = count_conn + 1
      print 'Incoming connection from %s' % repr(addr)
      handler = EchoHandler(sock,addr,count_conn)   #..................................fresh variableto keep trach of current cliet added...
      EchoServer.clients_handler.append(handler)    #..................................this client added to list of others.................. 
      lol.append(sock)

  def handle_connect(self):
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.connect(('', 8080))

  def write(self,cl_no,data):
    if len(EchoServer.clients_handler)>cl_no:
      EchoServer.clients_handler[cl_no].send(data)
    else:
      print "\nNo client connected\n"

  def getListOfClients(self):
    print "connected clients are : "
    for x in self.clients:
      print self.clients[x]

server = EchoServer("192.168.43.253", 8080)
if __name__ == "__main__":
  thread.start_new_thread(run_thread,("erte",) )
  thread.start_new_thread(run_thread_gui,("erte",) )

class Reply:
  def __init__(self):
    global server
    self.ser=server
  def positive(self,i,text):
    self.ser.write(i,text)

print "waiting for connections...\n"
st=time();
while(True):
  sleep(3)
  if request_flag:
    break
while(url1==""):
  pass

while True:                                          #....................bus run krega jab tak connect wala button press na hojaye...
  sleep(3)
  if len(EchoServer.clients)>no_of_connections:
    no_of_connections=len(EchoServer.clients)        #......................jitne clients ne accept kia hai, vo saare yaha aege..........
                                                    #.......................basically for keeping count of number of connected users.......
  if connect_flag==True:
    break
url = url1
print "\nurl entered is " + url + "\n"
os.chdir(client.gui.v.get())                       #................jo browse kia haina, usko kholna k liye use hoga...............
file_name = url.split('/')[-1]                     #................url se filename derive kia........................
f = open(file_name, 'wb')
u = urllib2.urlopen(url)
meta = u.info()

def download(i):
  if i==0:
    start=0
  else:        
    start=i*packet_size_each_thread[i-1]
  start1=str(start)
  end=start+packet_size_each_thread[i]-1
  end1=str(end)
  req = urllib2.Request(url, headers={'Range':'bytes='+start1+'-'+end1})
  u = urllib2.urlopen(req)
  block_sz = 32768
  temp='\0'
  while True:
    data=u.read(block_sz)
    if not data:
      break
    #print('%d Fetched %s from %s' % (i,len(data), url))
    temp=temp+data
    
  temp=temp[1:]
  print "\n\n"
  print len(temp),"\n\n Length of temp"
  f.seek(start)
  f.write(temp)

def start_parallel():
  threads = [threading.Thread(target=download, args = (i,)) for i in range(no_of_threads)]
  for t in threads:
    t.start()
  for t in threads:
    t.join()
a=0
items=[]                    #................client sockets ka track rakhne k liye, jo number yaha se jaega, vohi Handler array se write hoga
while a<len(lol):
  items.append(a)
  a+=1                     #............................get selection from here.to connect to.

print items
#no_of_connections and no_of acceptance. connection me jo connect hue, acceptance me jinhone positive response dia..................
#.......................no_of_responses jinhone react kia, chqahe positive ya negative................................................
#sending requests to all selected clients if they interested in download
i=0
while i<no_of_connections:
  if i in items:
    server.write(i,"Would you help me in download of "+url)
  i+=1
#waiting for requests to be responded
print "\n\n--------waiting for clients to respond--------\n\n"
while True:
  no_of_responses=0
  i=0
  while i < no_of_connections:
    if server.clients_handler[i].acceptance!=-1:     #ya to han ya na aya. warna agar -1 hi rehta to matlab ki respond hi nahi kia, no of responses k liye chahiye
        no_of_responses+=1
    if server.clients_handler[i].acceptance==1:       #.............jaha se downloading k liye haan aya, uska acceptance 2 krna padega, so as to keep track.................
        server.clients_handler[i].acceptance=2
        no_of_acceptance+=1
        server.write(i,str(no_of_acceptance))

    i+=1
  if no_of_responses==len(items):
    break
  sleep(2)
file_size = int(meta.getheaders("Content-Length")[0])
print  "file size total is  -------------",file_size,"----------"
print "no of acceptance is --------------",(no_of_acceptance),"------------"
packet_size_server=file_size/(no_of_acceptance+1)         #..................+1 kia cause apna server bhi to download kr rha hai.........
packet_size_each_client=[]
i=0
cnt=0
while i<no_of_connections:
  if server.clients_handler[i].acceptance==2:
    cnt+=1
    if cnt!=no_of_acceptance:
      packet_size_each_client.append(file_size/(no_of_acceptance+1))
    else:
      packet_size_each_client.append((file_size/(no_of_acceptance+1)) + (file_size%(no_of_acceptance+1)))
  else:
    packet_size_each_client.append(0)
  i+=1
#waiting for download button to be pressed
should_proceed=False
while should_proceed==False:
  sleep(2)
#sending details to those who accepted
i=0
start_from=packet_size_server
while i<no_of_connections:
  if server.clients_handler[i].acceptance==2:
    server.write(i,url)
    server.clients_handler[i].sizeToDownload=packet_size_each_client[i]
    server.write(i,str(start_from))
    print i+1," starts from ",start_from,"and downloads ",packet_size_each_client[i]
    sleep(1)
    sleep(1)
    start_from+=packet_size_each_client[i]
    server.write(i,str(packet_size_each_client[i]))
  i+=1
print "\n\n"
no_of_threads=2
packet_size_each_thread=[]
i=0
while i<no_of_threads:
  if i != no_of_threads-1:
    packet_size_each_thread.append(packet_size_server/no_of_threads)
  else:
    packet_size_each_thread.append((packet_size_server/no_of_threads) + (packet_size_server%no_of_threads))
  i+=1
st=time()
# start_parallel is starting download of own
start_parallel()
print time()-st
# clients to send downloaded data
print "\n\n --------waiting for clients to send downloaded data------\n\n"
while True:
  completed_downloads=0
  i=0
  while i < no_of_connections:
    if server.clients_handler[i].acceptance==3:
      if len(server.clients_handler[i].DATA)==server.clients_handler[i].sizeToDownload:
        completed_downloads+=1
    i+=1
  if completed_downloads==no_of_acceptance:
    break
  sleep(2)
main_data='\0'
i=0
while i<no_of_connections:
  if server.clients_handler[i].acceptance==3:
    main_data+=server.clients_handler[i].DATA
  i+=1
main_data=main_data[1:]
start=packet_size_server
print "\n\n------total data recieved from rest = ",len(main_data),"-----------\n\n"
f.seek(start)
f.write(main_data)
f.close()
print "\n\n-------hogya :P :)-----\n\n"
while True:
  a=1