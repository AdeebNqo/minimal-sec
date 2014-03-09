#	
# Zola Mahlaza
# 8 March 2014
#
import shelve
import pickle
import os
import socket
import random
import threading

registeredclients = ['client001']
connectedclients = {}
class sockethandler(threading.Thread):
	connection = None
	address = None
	def __init__(self,conn, addr):
		self.connection = conn
		self.address = addr
		threading.Thread.__init__(self)
	def run(self):
		data = self.connection.recv(1024).strip()
		print('server received {}'.format(data))
		if (data.startswith('CONNECT')):
			if (data.split()[1] in registeredclients):
				print('send him something')
				#do something
			else:
				self.connection.sendall('101 CONNECT FAILED')		
		print(data)
class server():
	files = []
	keytore =[]
	sockt = None
	def __init__(self,address):
		exists = False
		try:
			items = os.listdir('./data')
			tmpcount = 0
			for item in items:
				if (item=='keystore.ks' or item=='files.pkl'):
					tmpcount=tmpcount+1
					if (tmpcount==2):
						exists=True
						break
		except OSError:
			os.mkdir('./data')
		if (exists==False):
			#Creating the empty files
			open('./data/keystore.ks','w').close()
			open('./data/files.pkl','w').close()
		else:
			try:
				#load the stored files
				files = pickle.load(open('./data/files.pkl','r'))
				#loading stored keys
				keystore = shelve.open('keystore.ks')
			except EOFError:
				#the files are empty
				files = []
				keystore =[]
		self.sockt = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		self.sockt.bind(address)
		self.sockt.listen(1)
	def handle(self):
		while 1:
			conn, addr = self.sockt.accept()
			print('{} just connected.'.format(addr))
			connectedclients[addr] = conn
			handler = sockethandler(conn, addr)
			handler.start()
		
if __name__=='__main__':
	#ToDo: read server config
	addr = ('localhost',7777)
	servr = server(addr)
	servr.handle()
	
