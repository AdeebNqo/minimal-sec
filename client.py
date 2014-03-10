#
# Zola Mahlaza
# 09 March 2014
#
import socket
import pickle
import select
from Crypto.PublicKey import RSA
from Crypto.Cipher import PKCS1_v1_5

class client(object):
	sockt = None
	host = None
	port = 0
	publickeyLocation = None
	privatekeyLocation = None
	username = 'client001'
	def __init__(self, host, port):
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
		print('connected!')
		#initiate three-way handshake
		self.send('CONNECT {}'.format(self.username))
		response = self.sockt.recv(1024)
		if (response.startswith('101')):
			raise Exception('Connection failed 101. Client not recognized')
		else:
			print('waiting for token...')
			#decode authtoken from server
			authtoken = self.sockt.recv(1024)
			print('recieved token, {}'.format(authtoken))
			privkey = open('{}/client/client'.format(privatekeyLocation),'r').read()
			rsakey = RSA.importKey(privkey)
			rsakey = PKCS1_v1_5.new(rsakey)
			token = rsakey.decrypt(authtoken)
			print(token)
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
	client = client('localhost', 7779)
	client.connect()
	client.send('hello')
	client.disconnect()
