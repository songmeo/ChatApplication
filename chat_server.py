import eventlet
import eventlet.queue as queue
import lib

class Server(object):
	send_queues = {}
	#lock = threading.Lock()

	def __init__(self, host, port):
		self.HOST = host
		self.PORT = port

	def handle_client_recv(self, client_sock, client_addr):
		rest = bytes()
		while True:
			try:
				(msgs, rest) = lib.recv_msgs(client_sock, rest)
			except (ConnectionError, EOFError):
				self.handle_disconnect(client_sock, client_addr)
				break
			for msg in msgs:
				msg = '{}: {}'.format(client_addr, msg)
				print(msg)
				self.broadcast_msg(msg)

	def handle_client_send(self, sock, q, addr):
		while True:
			msg = q.get()
			if msg == None: break
			try:
				lib.send_msg(sock, msg)
			except (ConnectionError, BrokenPipe):
				self.handle_disconnect(sock, addr)
				break

	def broadcast_msg(self, msg):
		for q in self.send_queues.values():
			q.put(msg)

	def handle_disconnect(self, sock, addr):
		fd = sock.fileno()
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

	server = Server(HOST, PORT)
	server.SOCK = eventlet.listen((HOST,PORT))
	addr = server.SOCK.getsockname()
	print('Listening on {}'.format(addr))

	while True:
		client_sock,addr = server.SOCK.accept()
		q = queue.Queue()
		server.send_queues[client_sock.fileno()] = q
		eventlet.spawn_n(server.handle_client_recv,
				client_sock,
				addr)
		eventlet.spawn_n(server.handle_client_send,
				client_sock,
				q,
				addr)
		print('Connection from {}'.format(addr))
