#
# Zola Mahlaza
# 09 March 2014
#
import socket
import pickle
import select
import base64
from Crypto.PublicKey import RSA
from Crypto.Cipher import PKCS1_v1_5
from main import Security

class client(object):
	sockt = None
	host = None
	port = 0
	publickeyLocation = None
	privatekeyLocation = None
	username = 'client001'
	security = None
	def __init__(self, host, port):
		security = Security()
		self.savekeyConfig('./keys','./keys')
		self.host = host
		self.port = port
		self.sockt = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		config = pickle.load(open('./data/client_config.pkl','rb'))
		self.publickeyLocation = config['publickey']
		self.privatekeyLocation = config['privatekey']
	def connect(self):
		print('connecting....')
		self.sockt.connect((self.host, self.port))
		self.sockt.setblocking(1)
		print('connection established')
		print('initiating 3 way handshake...')
		#initiate three-way handshake
		self.send('CONNECT {}'.format(self.username))
		response = self.sockt.recv(1024).strip()
		print('server response is {}'.format(response))
		if (response.startswith('101')):
			raise Exception('Connection failed 101. Client not recognized')
		else:
			#decrypting token
			authtoken = base64.b64decode(response)
			print('server responded with token: {}'.format(authtoken))
			privkey = open('{}/client/client'.format(self.privatekeyLocation),'r').read()
			rsakey = RSA.importKey(privkey)
			rsakey = PKCS1_v1_5.new(rsakey)
			token = rsakey.decrypt(authtoken, -1)
			print('the decrypted token is {} '.format(token))
			print('sending token back to server...')
			#encrypting with server public keys
			pubkey = open('{}/client/server.pub'.format(self.publickeyLocation)).read()
			prsakey = RSA.importKey(pubkey)
			prsakey = PKCS1_v1_5.new(prsakey)
			token = prsakey.encrypt(token)
			self.send(base64.b64encode(token))
			inputv = ''			
			while (inputv!='q'):
				inputv = input('location of folder to transfer:')
				File = open(inputv,'r')
				line = File.readline()
				ID = line[0:line.find('-')]
				
	def disconnect(self):
		self.sockt.close()
	def send(self,data):
		self.sockt.sendall(data)
	def savekeyConfig(self, publickey, privatekey):
		config = {}
		config['publickey'] = publickey
		config['privatekey'] = privatekey
		pickle.dump(config, open('./data/client_config.pkl','w'))
if __name__=='__main__':
	client = client('localhost', 7778)
	client.connect()
	#client.send('hello')
	client.disconnect()
