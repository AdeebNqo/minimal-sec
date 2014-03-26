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
from keyconfig import KeyConfig
from keyconfig import Key

registeredclients = {}
connectedclients = {}
server_up = True
keyconfig = KeyConfig('server')

class sockethandler(threading.Thread):
	connection = None
	address = None
	connection_up = True
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
	def run(self):
		while 1:
			print('waiting for data...')
			data = self.connection.recv(1024).strip()
			print('server received -{}-'.format(data))
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
					privkey = open(keyconfig.getConfigItem(Key.OwnPrivate),'r').read()
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
						else:
							print('entity authentication unsuccessful')
							self.connection_up = False
							self.connection.close()
				else:
					self.connection.sendall('101 CONNECT FAILED')
			else:
				#connection lost
				print('{} has disconnected from server.'.format(self.address))
				break

class server():
	sockt = None
	def __init__(self,address):
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
	
