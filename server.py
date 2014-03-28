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
from Crypto.Cipher import AES
from Crypto.Cipher import PKCS1_v1_5
import sys
import base64
from keyconfig import KeyConfig
from keyconfig import Key
import passphrase
from security import security
import subprocess

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
	security = None #Object that has utility security methods
	clientname = None
	def __init__(self,conn, addr):
		self.security = security()
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
			#print('server received -{}-'.format(data))
			if (data.startswith('CONNECT')):
				print('client attempting to connect...')
				clientname = data.split()[1]
				self.clientname = clientname
				if (clientname in registeredclients.keys()):
					#print('STATUS: client is registered.')
					#print('STATUS: generating nonce and token...')
					token = passphrase.getpassphrase().encode('ascii', 'ignore').replace('\n', ' ').replace('\r', '')
					#print('STATUS: done generating token.')
					#generating nonce and sending it to client alongside token
					nonce = random.randint(0,9000000)
					#print('RESULT: nonce  {}'.format(nonce))
					token = '{1} {0}'.format(token,nonce)
					#print('RESULT: token  {}'.format(token))
					#print('STATUS: generating 3way session key')
					#Generating key to encrypt the data
					pool = map(chr,range(97,123))+map(chr,range(65,91))+map(chr,range(48,57))
					random.shuffle(pool)
					threewaykey = ''.join(pool[0:32])
					#print('RESULT: session key  {}'.format(threewaykey))
					#print('STATUS: encrypting server threeway session key...')
					#encrypting the threeway session key
					pubkey = open(registeredclients[clientname],'r').read()
					rsakey = RSA.importKey(pubkey)
					rsakey = PKCS1_v1_5.new(rsakey)
					Ethreewaykey = base64.b64encode(rsakey.encrypt(threewaykey)) #Encrypted three way key
					#print('RESULT: Encrypted session key: {}'.format(Ethreewaykey))
					#print('STATUS: encrypting token with session key...')
					#encrypting the actual (token, nonce) combination
					etoken = base64.b64encode(self.security.encrypt(token,'AES',threewaykey,AES.MODE_CBC)),
					#print('RESULT: encrypted token: {}'.format(etoken))
					#print('STATUS: appending etoken to ethreewaykey')
					authtoken = '{1} {0}'.format(etoken, Ethreewaykey)
					#print('RESULT: appended token and key {}'.format(authtoken))
					#print('STATUS: sending result to server')
					self.send(authtoken)
					print('STATUS: sent authtoken')
					
					#
					# Last step.
					# Getting response from client and comparing nonces and tokens
					#
				
					print('STATUS: waiting for client response...')
					#Retrieve response from client
					cresponse = self.connection.recv(1024).strip()
					#print('STATUS: client has responded. Now decoding response..')
					#print('RESULT: client response is {}'.format(cresponse))
					#breaking up response to E_s(k) and E_aes(token||nonce), that is, to encrypted key and encrypted (token,nonce) pair
					vals = cresponse.split()
					EClientthreewaykey = base64.b64decode(vals[0])
					Etokennoncepair = base64.b64decode(''.join(vals[1:]))
					
					#print('RESULT: Ethreewaykey {}'.format(EClientthreewaykey))
					#print('RESULT: Etokennoncepair {}'.format(Etokennoncepair))
					#print ('STATUS: decrypting client created 3way key..')
					#decrypint client created threeway session key
					spriv = keyconfig.getConfigItem(Key.OwnPrivate)
					privkey = open(spriv,'r').read()
					prsakey = RSA.importKey(privkey)
					prsakey = PKCS1_v1_5.new(prsakey)
					Clientthreewaykey = prsakey.decrypt(EClientthreewaykey,-1)
					#print('RESULT: clientcreated 3way session key is {}'.format(Clientthreewaykey))
			
					#decrypting (token,nonce) pair using the client created threeway session key
					#print('STATUS: decrypting token,nonce pair with key')
					tokennoncepair = self.security.decrypt(Etokennoncepair,'AES',Clientthreewaykey,AES.MODE_CBC)
					tokennoncelist = tokennoncepair.split()
					#print('RESULT: (token,nonce) list: {}'.format(tokennoncelist))
					tokenX = ' '.join(tokennoncelist[:])
					if (Clientthreewaykey==-1):
						self.connection.close()
						raise Exception('Decryption of client token failed.')
					else:
						#comparing cached nonce and token with client's response
						#print('X is last one')
						#print('STATUS: comparing {0} and {1}'.format(token,tokenX))
						self.authenticated = token==tokenX
						if (self.authenticated):
							print('entity authentication successful.')
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
				fileitems = data.split('\t')
				print('file items are : {}'.format(fileitems))
				print('-------------------------------------')
				ID = fileitems[0]
				Edetails = fileitems[1]
				signedHash = '\t'.join(fileitems[2:])
				print('ID: {}'.format(ID))
				print('Edatails: {}'.format(Edetails))
				print('signedHash: {}'.format(signedHash))
				#decrypting file details
				details = self.security.decrypt(Edetails,'AES','thisisakey',AES.MODE_CBC)
				#extracting hash from signed hash by decrypting with public key
				pubkey = open(registeredclients[clientname],'rb').read()
				rsakey = RSA.importKey(pubkey)
				rsakey = PKCS1_v1_5.new(rsakey)
				Hash = rsakey.decrypt(signedHash,-1)
				#check if decryption is succesful
				if (Hash!=-1):
					HashX = self.security.hash('{0} {1}'.format(ID,details),'sha512')
					if (Hash==HashX):
						f = open('{0}/{1}.nqo'.format(dbdatadir,ID),'w+')
						f.write(data)
						f.close()
						self.send('FILERECIEVED')
						print('file saved.')
					else:
						self.send('FILECHANGED')
						print('file changed')
				else:
					self.send('FILECHANGED')
					print('file changed')
			else:
				#connection lost
				print('{} has disconnected from server.'.format(self.address))
				break

class server():
	sockt = None
	def __init__(self,address):
		#loading or creating (if not exists) db store for the files
		if (os.path.exists(dbdatadir)==False):
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
	
