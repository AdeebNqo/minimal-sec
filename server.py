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
from Crypto.PublicKey import RSA
from Crypto.Cipher import PKCS1_v1_5
import sys
import base64

registeredclients = {}
connectedclients = {}
server_up = True
class sockethandler(threading.Thread):
	connection = None
	address = None
	connection_up = True
	def __init__(self,conn, addr):
		registeredclients['client001'] = '{}/keys/server/client001.pub'.format(os.getcwd())#registering default client
		self.connection = conn
		self.address = addr
		self.connection.setblocking(1)
		threading.Thread.__init__(self)
		self.daemon = True
	def stop(self):
		super(sockethandler, self).stop();
	def run(self):
		while 1:
			print('waiting for data...')
			data = self.connection.recv(1024).strip()
			print('server received {}'.format(data))
			if (data.startswith('CONNECT')):
				clientname = data.split()[1]
				if (clientname in registeredclients.keys()):
					print('client is registered.')
					token = "kneel before zod"
					#encrypting
					pubkey = open(registeredclients[clientname],'r').read()
					rsakey = RSA.importKey(pubkey)
					rsakey = PKCS1_v1_5.new(rsakey)
					authtoken = base64.b64encode(rsakey.encrypt(token))
					print('encrypted token is {}'.format(authtoken))
					self.connection.sendall(authtoken)
					print('sent authtoken')
					print('waiting for client response...')
					#Retrieve token again from client
					rtoken = self.connection.recv(1024).strip()
					print('client has responded')
					rtoken = base64.b64decode(rtoken)
					privkey = open('{}/keys/server/server'.format(os.getcwd()),'r').read()
					prsakey = RSA.importKey(privkey)
					prsakey = PKCS1_v1_5.new(prsakey)
					rtoken = prsakey.decrypt(rtoken,-1)
					print('client responded with {}'.format(rtoken))
					if (rtoken==-1):
						self.connection.close()
						raise Execption('Decryption of client token failed.')
					else:
						if (rtoken==token):
							print('entity authentication successful.')
						else:
							print('entity authentication unsuccessful')
							self.connection_up = False
							self.connection.close()
				else:
					self.connection.sendall('101 CONNECT FAILED')
			

class server():
	files = []
	keytore =[]
	sockt = None
	def __init__(self,address):
		exists = False
		try:
			items = os.listdir('./data')
			tmpcount = 0
			if ('keystore.ks' in items and 'files.pkl' in items):
				exists = True
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
		while server_up:
			conn, addr = self.sockt.accept()
			print('{} just connected.'.format(addr))
			connectedclients[addr] = conn
			handler = sockethandler(conn, addr)
			handler.start()
		
if __name__=='__main__':
	#handling contrl-c
	#ToDo: read server config
	addr = ('localhost',7778)
	servr = server(addr)
	servr.handle()
	
