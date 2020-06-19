import socket

def create_listen_socket(host, port):
	sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	#set protocol independent options, allow reusing address for this socket
	sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
	sock.bind((host, port))
	sock.listen(100)
	return sock

def parse_recvd_data(data):
	parts = data.split(b'\0')
	msgs = parts[:-1]
	rest = parts[-1]
	return (msgs, rest)

def recv_msgs(sock, data=bytes()):
	msgs = []
	while not msgs:
		recvd = sock.recv(4096)
		if not recvd:
			raise ConnectionError()
		data = data + recvd
		(msgs, rest) = parse_recvd_data(data)
	msgs = [msg.decode('utf-8') for msg in msgs]
	return (msgs, rest)

def prep_msg(msg):
	msg += '\0'
	return msg.encode('utf-8')

def send_msg(sock, msg):
	data = prep_msg(msg)
	sock.sendall(data)
