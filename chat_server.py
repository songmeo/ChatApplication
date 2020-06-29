import select
import lib
from types import SimpleNamespace
from collections import deque

class Server:
	def __init__(self, host, port):
		self.HOST = host
		self.PORT = port
		self.clients = {}
		self.usernames = set()

	def create_client(self, sock, usr):
		return SimpleNamespace(
				sock=sock,
				rest=bytes(),
				username = usr,
				send_queue=deque())

	def add_username(self, client_sock):
		lib.send_msg(client_sock, "Welcome! Please type username: ")
		exist = True
		while exist:
			username = client_sock.recv(4096).decode().rstrip('\x00')
			prev_len = len(self.usernames)
			self.usernames.add(username)
			if prev_len == len(self.usernames):
				lib.send_msg(client_sock, "Oops username exists. Please choose a different one: ")
				exist = True
			else:
				exist = False
		return username

	def broadcast_msg(self, msg):
		data = lib.prep_msg(msg)
		for client in self.clients.values():
			client.send_queue.append(data)
			poll.register(client.sock, select.POLLOUT)

if __name__ == '__main__':
	HOST = ''
	PORT = 4040
	s = Server(HOST, PORT)
	listen_sock = lib.create_listen_socket(HOST, PORT)
	poll = select.poll()
	poll.register(listen_sock, select.POLLIN)
	addr = listen_sock.getsockname()
	print('Listening on {}'.format(addr))

	while True:
		for fd, event in poll.poll():

			# clear up closed socket
			if event & (select.POLLHUP |
					select.POLLERR |
					select.POLLNVAL) :
				poll.unregister(fd)
				del s.clients[fd]

			# accept new connection, add clients to server client dict
			elif fd == listen_sock.fileno():
				client_sock, addr = listen_sock.accept()
				fd = client_sock.fileno()

				username = s.add_username(client_sock)

				s.clients[fd] = s.create_client(client_sock, username)
				poll.register(fd, select.POLLIN)

				welcome_msg = "{} joined the chat!".format(username)
				s.broadcast_msg(welcome_msg)
				print('Connection from {}'.format(addr))

			# handle received data on socket
			elif event & select.POLLIN:
				client = s.clients[fd]
				addr = client.sock.getpeername()
				recvd = client.sock.recv(4096)
				if not recvd:
					client.sock.close()
					print('Client {} disconnected'.format(addr))
					continue
				data = client.rest + recvd
				(msgs, client.rest) = lib.parse_recvd_data(data)
				for msg in msgs:
					msg = '{}: {}'.format(client.username, msg.decode())
					print(msg)
					s.broadcast_msg(msg)

			# send msg to client
			elif event & select.POLLOUT:
				client = s.clients[fd]
				data = client.send_queue.popleft()
				sent = client.sock.send(data)
				if sent < len(data):
					client.sends.appendleft(data[sent:])
				if not client.send_queue:
					poll.modify(client.sock, select.POLLIN)
