import sys, socket, os
import pickle
import thread
from ServerWorker import ServerWorker

class Server:	
	
	def main(self):
		try:
			SERVER_PORT = 8000;
		except:
			print "[Usage: Server.py Server_port]\n"
		rtspSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		rtspSocket.bind(('', SERVER_PORT))
		rtspSocket.listen(5)        

		while True:
			conn, addr = rtspSocket.accept();
			all_files_in_this_folder = [f for f in os.listdir('../foo/') if os.path.isdir(os.path.join('../foo/', f))]
			print all_files_in_this_folder;

			conn.send(pickle.dumps(all_files_in_this_folder));
			# Receive client info (address,port) through RTSP/TCP session

			foldername = conn.recv(1024)
			print foldername;

			all_files_in_this_folder = [f for f in os.listdir('../foo/' + foldername) if os.path.isfile(os.path.join('../foo/'+foldername, f))]
			print all_files_in_this_folder;

			conn.send(pickle.dumps(all_files_in_this_folder))
			
			# thread.start_new_thread(self.callThread,(conn, rtspSocket,))			
			while True:
				clientInfo = {}
				clientInfo['rtspSocket'] = rtspSocket.accept()
				ServerWorker(clientInfo).run()		


	# def callThread(self, conn, rtspSocket): 

	# 	while True:
			

		

if __name__ == "__main__":
	(Server()).main()


