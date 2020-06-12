import sys, socket

class Client(object):
	def __init__(self, host, port, sock):
		self.HOST = host
		self.PORT = port
		self.SOCK = sock

	def recv_msg(self):
		data = bytearray()
		msg = ''
		while not msg:
			recvd = SOCK.recv(4096)
			if not recvd:
				raise ConnectionError()
			data = data + recvd
			if b'\0' in recvd:
				msg = data.rstrip(b'\0')
		msg = msg.decode('utf-8')
		print('Received echo: ' + msg)

	def send_msg(self, msg):
		msg += '\0'
		data = msg.encode('utf-8')
		SOCK.sendall(data)
		print('Sent msg: {}'.format(msg))

	def connect_socket(self):
		SOCK.connect((HOST, PORT))
		print('\nConnected to {}:{}'.format(HOST, PORT))

	def close_socket(self):
		SOCK.close()
		print('Closed connection to server\n')

if __name__ == '__main__':

	HOST = sys.argv[-1] if len(sys.argv) > 1 else '127.0.0.1'
	PORT = 4040
	SOCK = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	client = Client(HOST, PORT, SOCK)

	while True:
		try:
			client.connect_socket()

			print("Type message, enter to send, 'q' to quit")
			msg = input()
			if msg == 'q':
				break

			client.send_msg(msg)

		except ConnectionError:
			print('Socket error')
			break

		finally:
			client.close_socket()
