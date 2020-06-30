import lib
import sys, socket, threading

class Client(object):

	def __init__(self, host, port):
		self.HOST = host
		self.PORT = port
		self.SOCK = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		self.SOCK.connect((host,port))

	def handle_input(self):
		while True:
			msg = input()
			if msg == 'q':
				self.SOCK.shutdown(socket.SHUT_RDWR)
				self.SOCK.close()
				break
			try:
				lib.send_msg(self.SOCK, msg)
			except (BrokenPipeError, ConnectionError):
				break

def main():
	#HOST = sys.argv[-1] if len(sys.argv) > 1 else '127.0.0.1'
	try:
		host = sys.argv[1].split(":")[0]
	except:
		host = input("Host: ")
	try:
		port = int(sys.argv[1].split(":")[1])
	except:
		port = int(input("Port: "))
	client = Client(host, port)

	thread = threading.Thread(target=client.handle_input,
				daemon=True)
	thread.start()
	rest = bytes()
	addr = client.SOCK.getsockname()
	while True:
		try:
			(msgs, rest) = lib.recv_msgs(client.SOCK)
			for msg in msgs:
				print(msg)
		except ConnectionError:
			print('Socket error')
			client.SOCK.close()
			break

if __name__ == '__main__':
	main()
