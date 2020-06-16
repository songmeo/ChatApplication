import sys, socket, threading

class Client(object):

	def __init__(self, host, port):
		self.HOST = host
		self.PORT = port
		self.SOCK = ''

	def create_socket(self):
		self.SOCK = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

	def handle_input(self):
		print("Type messages:")
		while True:
			msg = input()
			if msg == 'q':
				self.sock.shutdown(socket.SHUT_RDWR)
				self.sock.close()
				break
			try:
				self.send_msg(msg)
			except (BrokenPipeError, ConnectionError):
				break

	def parse_recvd_data(self, data):
		parts = data.split(b'\0')
		msg = parts[:-1]
		rest = parts[-1]
		return (msg, rest)

	def recv_msgs(self, data=bytes()):
		data = bytearray()
		msgs = []
		while not msgs:
			recvd = self.SOCK.recv(4096)
			if not recvd:
				raise ConnectionError()
			data = data + recvd
			(msgs, rest) = self.parse_recvd_data(data)
		msg = [msg.decode('utf-8') for msg in msgs]
		return (msgs, rest)

	def send_msg(self, msg):
		msg += '\0'
		data = msg.encode('utf-8')
		self.SOCK.sendall(data)
		print('Sent msg: {}'.format(msg))

	def connect_socket(self):
		self.SOCK.connect((HOST, PORT))
		print('\nConnected to {}:{}'.format(HOST, PORT))

	def close_socket(self):
		self.SOCK.close()
		print('Closed connection to server\n')

if __name__ == '__main__':

	HOST = sys.argv[-1] if len(sys.argv) > 1 else '127.0.0.1'
	PORT = 4040
	client = Client(HOST, PORT)

	client.create_socket()
	client.connect_socket()
	thread = threading.Thread(target=client.handle_input,
				daemon=True)
	thread.start()
	rest = bytes()
	addr = client.SOCK.getsockname()
	while True:
		try:
			(msgs, rest) = client.recv_msgs()
			for msg in msgs:
				print(msg)
		except ConnectionError:
			print('Socket error')
			client.SOCK.close()
			break
