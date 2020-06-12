import socket

class Server(object):
	def __init__(self, host, port):
		self.HOST = host
		self.PORT = port

	def create_socket(self):
		self.SOCK = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		self.SOCK.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
		self.SOCK.bind((self.HOST, self.PORT))
		self.SOCK.listen(100)

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
		return msg

	def send_msg(self, sock, msg):
		msg += '\0'
		data = msg.encode('utf-8')
		sock.sendall(data)
		print('Sent msg: {}'.format(msg))


	def handle_client(self, client_sock, client_addr):
		try:
			msg = self.recv_msg(client_sock)
			self.send_msg(client_sock, msg)
		except (ConnectionError, BrokenPipeError):
			print('Socket error')
		finally:
			print('Closed connection to {}'.format(client_addr))
			client_sock.close()

if __name__ == '__main__':
	HOST =  '' #listening on all interfaces
	PORT = 4040

	server = Server(HOST,PORT)
	server.create_socket()
	addr = server.SOCK.getsockname()
	print('Listening on {}'.format(addr))

	while True:
		client_sock, client_addr = server.SOCK.accept()
		print('\nConnection from {}'.format(client_addr))
		server.handle_client(client_sock, client_addr)

