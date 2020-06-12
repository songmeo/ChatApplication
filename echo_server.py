import socket

class Server(object):
	def __init__(self, host, port, sock):
		self.HOST = host
		self.PORT = port
		self.SOCK = sock

	def recv_msg(self, sock):
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
		print('Received echo: ' + msg)
		return msg

	def send_msg(self, sock, msg):
		msg += '\0'
		data = msg.encode('utf-8')
		sock.sendall(data)
		print('Sent msg: {}'.format(msg))


	def handle_client(self, client_sock, client_addr):
		try:
			msg = self.recv_msg(client_sock)
			print('{}: {}'.format(client_addr, msg))
			self.send_msg(client_sock, msg)
		except (ConnectionError, BrokenPipeError):
			print('Socket error')
		finally:
			print('Closed connection to {}'.format(client_addr))
			client_sock.close()

if __name__ == '__main__':
	HOST =  '' #listening on all interfaces
	PORT = 4040

	SOCK = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	SOCK.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
	SOCK.bind((HOST, PORT))
	SOCK.listen(100)

	server = Server(HOST,PORT,SOCK)
	addr = SOCK.getsockname()
	print('Listening on {}'.format(addr))

	while True:
		client_sock, client_addr = SOCK.accept()
		print('Connection from {}'.format(client_addr))
		server.handle_client(client_sock, client_addr)

