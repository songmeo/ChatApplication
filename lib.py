import socket

PORT = 4040

#sockets for receving connection requests
def create_listen_socket(host, port):
	sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM) #ipv4, tcp
	#set protocol-independent option
	sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1) #the layer itself ,permit reuse of local addresses 
	sock.bind((host, port)) 
	sock.listen(100) #number of unaccepted connections that the system allows before refusing new connections
	return sock

#parse messages using b'\0' as message delimiter
def recv_msg(sock):
	data = bytearray()
	msg = ''
	while not msg:
		recvd = sock.recv(4096)
		if not recvd:
			raise ConnectionError()
		data = data + recvd
		if b'\0' in recvd:
			msg = data.rstrip(b'\0')
	msg = msg.decode('utf-8')
	return msg

def prep_msg(msg):
	msg += '\0'
	return msg.encode('utf-8')

def send_msg(sock, msg):
	data = prep_msg(msg)
	sock.sendall(data)
