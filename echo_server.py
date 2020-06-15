import threading, socket, queue

class Server(object):
	send_queues = {}
	lock = threading.Lock()

	def __init__(self, host, port):
		self.HOST = host
		self.PORT = port

	def create_socket(self):
		self.SOCK = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		self.SOCK.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
		self.SOCK.bind((self.HOST, self.PORT))
		self.SOCK.listen(100)

	def parse_recvd_data(data):
		parts = data.split(b'\0')
		msgs = parts[:-1]
		rest = parts[-1]
		return (msgs, rest)

	def recv_msgs(self, sock, data=bytes()):
		msgs = []
		while not msgs:
			recvd = sock.recv(4096)
			if not recvd:
				raise ConnectionError()
			data = data + recvd
			(msgs, rest) = self.parse_recvd_data(data)
		msgs = [msg.decode('utf-8') for msg in msgs]
		return (msgs, rest)

	def send_msg(self, sock, msg):
		msg += '\0'
		data = msg.encode('utf-8')
		sock.sendall(data)
		print('Sent msg: {}'.format(msg))


	def handle_client_recv(self, client_sock, client_addr):
		rest = bytes()
		while True:
			try:
				(msgs, rest) = self.recv_msgs(client_sock, rest)
				self.send_msg(client_sock, msg)
			except (ConnectionError, EOFError):
				handle_disconnect(client_sock, client_addr)
				break
			for msg in msgs:
				msg = '{}: {}'.format(client_addr, msg)
				print(msg)
				broadcast_msg(msg)

	def handle_client_send(self, sock, q, addr):
		while True:
			msg = q.get()
			if msg == None: break
			try:
				self.send_msg(sock, msg)
			except (ConnectionError, BrokenPipe):
				handle_disconnect(sock, addr)
				break

	def broadcast_msg(msg):
		with lock:
			for q in self.send_queues.values():
				q.put(msg)

	def handle_disconnect(sock, addr):
		fd = sock.fileno()
		with lock:
			q = self.send_queues.get(fd, None)
		if q:
			q.put(None)
			del self.send_queues[fd]
			addr = sock.getpeername()
			print('Client {} disconnected'.format(addr))
			sock.close()

if __name__ == '__main__':
	HOST =  '' #listening on all interfaces
	PORT = 4040

	server = Server(HOST,PORT)
	server.create_socket()
	addr = server.SOCK.getsockname()
	print('Listening on {}'.format(addr))

	while True:
		client_sock, client_addr = server.SOCK.accept()

		thread = threading.Thread(target=server.handle_client,
					args=[client_sock, client_addr],
					daemon=True) #daemon is for exiting without having to close other threads first
		thread.start()

		print('\nConnection from {}'.format(client_addr))

