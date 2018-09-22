import cv2;
import numpy as np
import socket
import sys
import pickle
import struct, thread
import pyaudio
import wave
CHUNK = 1024
FORMAT = pyaudio.paInt16
CHANNELS = 2
RATE = 44100
RECORD_SECONDS = 3

def record():	
	p = pyaudio.PyAudio()

	stream = p.open(format=FORMAT,
					channels=CHANNELS,
					rate=RATE,
					input=True,
					frames_per_buffer=CHUNK)

	print("Recording")
	audioframes = []
	for i in range(0, int(RATE / CHUNK * RECORD_SECONDS)):
		
		data = stream.read(CHUNK)
		#print "AUdio", data	
		audioframes.append(data)

	print("Recording finished")

	stream.stop_stream()
	stream.close()
	p.terminate()	
	
	print len("".join(audioframes))#
	return audioframes

def play(audioframes):
	play=pyaudio.PyAudio()
	stream_play=play.open(format=FORMAT,
						  channels=CHANNELS,
						  rate=RATE,
						  output=True)


	stream_play.write("".join(audioframes))

	stream_play.stop_stream()
	stream_play.close()
	play.terminate()

def recv_all(sock):
	msg=""
	data=""
	while not data.endswith("a."):
		msg=sock.recv(1024)
		if not msg:
			break
		data=data+msg
	return data


cap = cv2.VideoCapture(0);

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM);

s.bind(('',7000));
s.listen(10);
conn_list=[]

def serverScreen() :
	
	while True:
		ret, frame = cap.read();

		data = pickle.dumps(frame);
			

		for conn in conn_list :
			conn.sendall(struct.pack("L", len(data))+data);

thread.start_new(serverScreen,());

while True:

	conn, addr = s.accept();
	conn_list.append(conn);

	print "Speak"
	frames=record()
	#print (pickle.dumps(frames))			
	s.sendall(pickle.dumps(frames))
	play(frames);
