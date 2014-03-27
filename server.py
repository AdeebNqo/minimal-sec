#	
# Zola Mahlaza (AdeebNqo)
# 8 March 2014
# 
# Server to handle file storage
#   
#  "It's all talk until the code runs."
#  - Ward Cunningham
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
from keyconfig import KeyConfig
from keyconfig import Key
import passphrase

registeredclients = {}
connectedclients = {}
server_up = True
keyconfig = KeyConfig('server')

dbdatadir = '{}/datadb'.format(os.getcwd())
dbfiles = []

class sockethandler(threading.Thread):
	connection = None
	address = None
	connection_up = True
	authenticated = False
	def __init__(self,conn, addr):

		clients = keyconfig.getConfigItem(Key.OtherParties) #retrieving all clients authorized to access server
		for client in clients:
			registeredclients[client.username] = client.publickey
		self.connection = conn
		self.address = addr
		self.connection.setblocking(1)
		threading.Thread.__init__(self)
		self.daemon = True
	def stop(self):
		super(sockethandler, self).stop();
	def send(self,data):
		self.connection.sendall(data)
	def run(self):
		while 1:
			print('waiting for data...')
			data = self.connection.recv(1024).strip()
			print('server received -{}-'.format(data))
			if (data.startswith('CONNECT')):
				print('client attempting to connect...')
				clientname = data.split()[1]
				if (clientname in registeredclients.keys()):
					print('client is registered.')
					token = passphrase.getpassphrase().encode('ascii', 'ignore')
					print('generated passphrase is {}'.format(token))
					#encrypting
					pubkey = open(registeredclients[clientname],'r').read()
					rsakey = RSA.importKey(pubkey)
					rsakey = PKCS1_v1_5.new(rsakey)
					authtoken = base64.b64encode(rsakey.encrypt(token))
					print('encrypted token is {}'.format(authtoken))
					self.send(authtoken)
					print('sent authtoken')
					print('waiting for client response...')
					#Retrieve token again from client
					rtoken = self.connection.recv(1024).strip()
					print('client has responded. Now decoding response..')
					rtoken = base64.b64decode(rtoken)
					spriv = keyconfig.getConfigItem(Key.OwnPrivate)
					print('server private key is located at {}'.format(spriv))
					#decrypting authentication token
					privkey = open(spriv,'r').read()
					prsakey = RSA.importKey(privkey)
					prsakey = PKCS1_v1_5.new(prsakey)
					rtoken = prsakey.decrypt(rtoken,-1)
					print('client responded with {}'.format(rtoken))
					if (rtoken==-1):
						self.connection.close()
						raise Exception('Decryption of client token failed.')
					else:
						if (rtoken==token):
							print('entity authentication successful.')
							self.authenticated = True
						else:
							print('entity authentication unsuccessful')
							self.connection_up = False
							self.connection.close()
				else:
					print('client not registered')
					self.send('101 CONNECT FAILED')
			elif (data=='FILESEND'):
				print('reading in the recieved file..')
				#accepting incoming file
				data = self.connection.recv(8000).strip()
				ID = data.split()[0]
				f = open('{0}/{1}.nqo'.format(dbdatadir,ID),'wb+')
				f.write(data)
				f.close()
				print('received data {}'.format(data))
				self.send('FILERECIEVED')
			else:
				#connection lost
				print('{} has disconnected from server.'.format(self.address))
				break

class server():
	sockt = None
	def __init__(self,address):
		#loading or creating (if not exists) db store for the files
		if (os.path.exists(dbdatadir)):
			#db store folder does not exist
			os.mkdir(dbdatadir)
		else:
			#loading existing files
			for files in os.walk(dbdatadir):
				for File in files:
					dbfiles.append(File)
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
	addr = ('localhost',7778)
	servr = server(addr)
	servr.handle()
	
