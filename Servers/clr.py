import socket
import threading, urllib2
import Queue
import sys
from time import *
import asyncore
reqq=""
url1=""
client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client_socket.connect(('localhost', 8080))
ch1=raw_input("Start Transfer?")
print "ch1 "+ch1
if ch1==str(1):
    print "HI! I'm HERE"
    client_socket.send("Start Transfer")
    reqq=client_socket.recv(8812)
    print "reqq "+reqq
    if reqq=="Send URL":
        url1=raw_input("Enter URL")
        print "url1"+url1
        client_socket.send(url1)
request_to_download=client_socket.recv(8812)
print request_to_download
print "1.Yes\n0.No"
choice=raw_input()
main_data=[]
if choice=='1':
    response="acceptance=1"
else:
    response="acceptance=0"
client_socket.send(response)
#.........................agar response poitive aya to server client number bhej dega,jisk basis pr judge krega apna client ki header ko size kitna dene ka hai..................
#.........................client number k baad url bhejega......................
#.........................fir start from....................................
#..........................fir har clint k liye required packet size.........................
if choice=='1':
    client_no=int(client_socket.recv(8812))
no_of_threads=2                  #................To be changed later, abhi static le lo...............................
class hifi:
    def __init__(self):
        global client_socket
        global no_of_threads
        global main_data
        self.url = client_socket.recv(8812)             #server sends url, followed by start address and then packet size..................
        self.start_from=int(client_socket.recv(8812))
        self.packet_size_each_client=int(client_socket.recv(8812))
        print "\n\n------amount to download= ",self.packet_size_each_client,"--------\n\n"   
        self.packet_size_each_thread=[]
        i=0
        while i<no_of_threads:
            if i != no_of_threads-1:
                self.packet_size_each_thread.append(self.packet_size_each_client/no_of_threads)
            else:
                self.packet_size_each_thread.append((self.packet_size_each_client/no_of_threads) + (self.packet_size_each_client%no_of_threads))
            i+=1
        u = urllib2.urlopen(self.url)
        main_data.append([])
        main_data.append([])
    def download(self,i):
        global client_no
        print i
        xyz=raw_input(str(i)+"lalala client number "+str(client_no))
        global main_data
        global client_no
        global no_of_threads
        x=client_no*no_of_threads
        if i==x:
            start=self.start_from
        else:
            start=self.start_from + (i-(x))*self.packet_size_each_thread[i-(x)-1]
        start1=str(start)
        end=start+ self.packet_size_each_thread[i-(x)]-1
        end1=str(end)
        print "diffrence"+str(end-start)
        req = urllib2.Request(self.url, headers={'Range':'bytes='+start1+'-'+end1})
        u = urllib2.urlopen(req)
        block_sz = 32768
        temp='\0'
        a=0
        while True:
            data=u.read(block_sz)
            if not data:
                break
            #print('%d Fetched %s from %s' % (i,len(data), self.url))
            temp=temp+data
            client_socket.send(str(len(data)))
            print "a"+str(a)
            a+=1
        main_data[i-x]=temp[1:]
    def start_parallel(self):
        global client_no
        global main_data
        global no_of_threads
        #result = Queue.Queue()
        x=client_no*no_of_threads
        y=x+no_of_threads
        threads = [threading.Thread(target=self.download, args = (i,)) for i in range(x,y)]   #.........................har client k 2 threads, plus apne khud k 2, client number *2 se agaya ki har client kitni baari chala . bus isk baad isi range me bhejdo.......
        for t in threads:
            t.start()
        for t in threads:
            t.join()


if choice=='1':
    inst=hifi()
    st=time()
    inst.start_parallel()
    print time()-st
    print "\n\n------sending data-----\n\n"
    client_socket.send("Sending data")
    lala=client_socket.recv(1024)
    for i in range(2):
        print len(main_data[i])
        client_socket.send(str(main_data[i]))
    print "\n\n----completed-----\n\n"
    #to keep the cmd on
    while True:
        a=1

