import socket,thread,random,os

all_ports_used = []
host = ''
all_files_being_send = []

def sendfile(conn,data):
    index = 0
    while len(data) > (index+1)*1024:
        conn.send(data[index*1024:(index+1)*1024])
        index += 1
    if len(data)%1024:
        conn.send(data[index*1024:])
    conn.close()

def clientTransfer(conn,addr):
    all_files_in_this_folder = [f for f in os.listdir('.') if os.path.isfile(os.path.join('.', f))]
    conn.send(','.join(all_files_in_this_folder))

    while True:
        filename = conn.recv(1024)
        file = open('./'+filename,'rb')
        data = file.readlines()
        chunksize = len(data)/5
        my_ports_used = []
        my_sockets = []
        my_conn = []
        index = 0
        while index < 5:
            port_number = random.randint(10000,50000)
            if port_number not in all_ports_used:
                my_ports_used.append(port_number)
                all_ports_used.append(port_number)
                my_sockets.append(socket.socket(socket.AF_INET,socket.SOCK_STREAM))
                my_sockets[-1].bind((host,port_number))
                my_sockets[-1].listen(1)
                index += 1

        conn.send(' '.join(str(x) for x in my_ports_used))

        index = 0

        while index < 5:
            new_conn,new_addr = my_sockets[index].accept()
            my_conn.append(new_conn)
            if index < 4:
                thread.start_new(sendfile,(new_conn,''.join(data[index*chunksize:(index+1)*chunksize]),))
            else:
                thread.start_new(sendfile,(new_conn,''.join(data[index*chunksize:]),))
            index += 1

    conn.close()

def mainfunction():
    port = 4000
    sock = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
    sock.bind((host,port))
    sock.listen(10)
    while True:
        conn,addr = sock.accept()
        thread.start_new(clientTransfer,(conn,addr))

    while True:
        pass

if __name__ == '__main__':
    mainfunction()
