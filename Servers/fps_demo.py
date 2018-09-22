# import the necessary packages
from __future__ import print_function
from imutils.video import WebcamVideoStream
from imutils.video import FPS
import argparse
import imutils
import cv2
import pickle, thread
import socket, struct;

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM);

s.bind(('',2000));
s.listen(10);
conn_list=[]

print("[INFO] sampling frames from webcam...")
stream = cv2.VideoCapture(0)
fps = FPS().start()

import pyaudio
import wave
CHUNK = 1024
FORMAT = pyaudio.paInt16
CHANNELS = 2
RATE = 44100
RECORD_SECONDS = 1

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

def serverScreen() :
	
	while True:

		# grab the frame from the stream and resize it to have a maximum
		# width of 400 pixels
		(grabbed, frame) = stream.read()
		frame = imutils.resize(frame, width=400)


		data = pickle.dumps(frame);
		for conn in conn_list :
			conn.sendall(struct.pack("L", len(data))+data);
		fps.update();			
#			audioframes=record(frame)
			#print (pickle.dumps(audioframes))	
#			play(audioframes,frame)		
			#	s.sendall(pickle.dumps(audioframes))


def serverAudio() :
	
	while True:

		# frames=record()

		# data = pickle.dumps(frame);
		for conn in conn_list :
			# conn.sendall(struct.pack("L", len(data))+data);
			audioframes=record()
			play(audioframes)		
			#s.sendall(pickle.dumps(audioframes))



thread.start_new(serverScreen,());
thread.start_new(serverAudio,())

while True:

	conn, addr = s.accept();
	conn_list.append(conn);

 
# loop over some frames
# while True:
# 	# grab the frame from the stream and resize it to have a maximum
# 	# width of 400 pixels
# 	(grabbed, frame) = stream.read()
# 	frame = imutils.resize(frame, width=400)
 
# 	# # check to see if the frame should be displayed to our screen
# 	# if args["display"] > 0:
# 	# 	cv2.imshow("Frame", frame)
# 	# 	key = cv2.waitKey(1) & 0xFF
 
# 	# # update the FPS counter
# 	fps.update()
 
# stop the timer and display FPS information
#fps.stop()
# print("[INFO] elasped time: {:.2f}".format(fps.elapsed()))
# print("[INFO] approx. FPS: {:.2f}".format(fps.fps()))
 
# # do a bit of cleanup
# stream.release()
# cv2.destroyAllWindows()

# created a *threaded* video stream, allow the camera sensor to warmup,
# and start the FPS counter
# print("[INFO] sampling THREADED frames from webcam...")
# vs = WebcamVideoStream(src=0).start()
# fps = FPS().start()
 
# # loop over some frames...this time using the threaded stream
# while fps._numFrames < args["num_frames"]:
# 	# grab the frame from the threaded video stream and resize it
# 	# to have a maximum width of 400 pixels
# 	frame = vs.read()
# 	frame = imutils.resize(frame, width=400)
 
# 	# check to see if the frame should be displayed to our screen
# 	if args["display"] > 0:
# 		cv2.imshow("Frame", frame)
# 		key = cv2.waitKey(1) & 0xFF
 
# 	# update the FPS counter
# 	fps.update()
 
# # stop the timer and display FPS information
# fps.stop()
# print("[INFO] elasped time: {:.2f}".format(fps.elapsed()))
# print("[INFO] approx. FPS: {:.2f}".format(fps.fps()))
 
# # do a bit of cleanup
# cv2.destroyAllWindows()
# vs.stop()
