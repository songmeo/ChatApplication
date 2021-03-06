import select
import lib
import socket
from types import SimpleNamespace
from collections import deque

class Server:
	def __init__(self, host = '', port = 4040):
		self.chatrooms = {
			"default": [] #list of clients
		}
		self.HOST = host
		self.PORT = port
		self.clients = {}
		self.usernames = set()

	def init(self):
		self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
		self.sock.bind((self.HOST, self.PORT))
		self.sock.listen(100)

		self.poll = select.poll()
		self.poll.register(self.sock, select.POLLIN)
		addr = self.sock.getsockname()
		print('Listening on {}'.format(addr))

		while True:
			for fd, event in self.poll.poll():

				# clear up closed socket
				if event & (select.POLLHUP |
						select.POLLERR |
						select.POLLNVAL) :
					self.poll.unregister(fd)
					del self.clients[fd]

				# accept new connection, add clients to server client dict
				elif fd == self.sock.fileno():
					client_sock, addr = self.sock.accept()
					fd = client_sock.fileno()

					username = self.add_username(client_sock)

					client = self.create_client(client_sock, username)
					self.clients[fd] = client
					self.poll.register(fd, select.POLLIN)

					#send list of chatrooms to new client
					chatrooms = ""
					for room in self.chatrooms.keys():
						members = len(self.chatrooms[room])
						chatrooms += room + " <{}>::".format(members)
					chatrooms = chatrooms[:-2]
					lib.send_msg(client_sock, chatrooms)
					msg = "Please choose a chatroom. You can type a new name to create new room."
					lib.send_msg(client_sock, msg)

					#client sends back the chatroom he wants to join
					chatroom = client_sock.recv(32).decode().rstrip('\x00')
					if chatroom not in self.chatrooms.keys():
						self.chatrooms[chatroom] = []
					client.room = chatroom
					self.chatrooms[chatroom].append(client)

					welcome_msg = "{} joined {}!".format(username, chatroom)
					self.broadcast_msg(welcome_msg, self.chatrooms[client.room])
					print('Connection from {}'.format(addr))

				# handle received data on socket
				elif event & select.POLLIN:
					client = self.clients[fd]
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
						self.broadcast_msg(msg, self.chatrooms[client.room])

				# send msg to client
				elif event & select.POLLOUT:
					client = self.clients[fd]
					data = client.send_queue.popleft()
					sent = client.sock.send(data)
					if sent < len(data):
						client.sends.appendleft(data[sent:])
					if not client.send_queue:
						self.poll.modify(client.sock, select.POLLIN)

	def create_client(self, sock, usr):
		return SimpleNamespace(
				sock=sock,
				rest=bytes(),
				username = usr,
				room = "default",
				send_queue=deque())

	def add_username(self, client_sock):
		lib.send_msg(client_sock, "Welcome! Please type username: ")
		exist = True
		while exist:
			username = client_sock.recv(4096).decode().rstrip('\x00')
			if username in self.usernames:
				lib.send_msg(client_sock, "Oops username exists. Please choose a different one: ")
			else:
				self.usernames.add(username)
				exist = False
		return username

	def broadcast_msg(self, msg, receivers = []):
		data = lib.prep_msg(msg)
		if not receivers:
			receivers = self.clients.values()
		for client in receivers:
			client.send_queue.append(data)
			self.poll.register(client.sock, select.POLLOUT)

def main():
	import os
	try:
		port = int(sys.argv[1])
	except:
		port = int(input("Port: "))
	s = Server(port = port)
	s.init()

if __name__ == '__main__':
	main()
