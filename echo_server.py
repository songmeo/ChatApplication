import lib

HOST = '' #listening on all interfaces
PORT = lib.PORT

def handle_client(sock, addr):
	try:
		msg = lib.recv_msg(sock)
		print('{}: {}'.format(addr, msg))
		lib.send_msg(sock, msg)
	except (ConnectionError, BrokenPipeError):
		print('Socket error')
	finally:
		print('Closed connection to {}'.format(addr))
		sock.close()

if __name__ == '__main__':
	listen_sock = lib.create_listen_socket(HOST, PORT)
	addr = listen_sock.getsockname()
	print('Listening on {}'.format(addr))

	while True:
		client_sock, addr = listen_sock.accept()
		print('Connection from {}'.format(addr))
		handle_client(client_sock, addr)
	
