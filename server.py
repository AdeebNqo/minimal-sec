#	
# Zola Mahlaza
# 8 March 2014
#
import shelve
import pickle
import os
import SocketServer
class server(SocketServer.BaseRequestHandler):
	def __init__(self):
		super(server, self).__init__()
		print('created!')
	def handle(self):
		data = self.request.recv(1024).strip()
		print('{} says'.format(self.client_address[0]))
		print(data)
		
if __name__=='__main__':
	#ToDo: read server config
	finalserver = SocketServer.TCPServer(('localhost', 7777),server)
	finalserver.serve_forever()
