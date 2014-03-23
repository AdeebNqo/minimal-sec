#
# Zola Mahlaza
# 09 March 2014
#
import socket
import pickle
import select
import base64
import sys
from Crypto.PublicKey import RSA
from Crypto.Cipher import PKCS1_v1_5
from security import security
from Crypto.Cipher import AES
from Crypto import Random
from M2Crypto import BIO, Rand, SMIME

blocksize = 16 #Block size for the encryption

class client(object):
	sockt = None
	host = None
	port = 0
	publickeyLocation = None
	privatekeyLocation = None
	username = 'client001'
	security = None
	def __init__(self, host, port):
		self.security = security()
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
	def sendFile(self,File):
		line = File.readline()
		dashpos = line.find('-') #Dash position
		ID = line[0:dashpos].replace('ID','')
		print('id is {}'.format(ID))
		DETAILS = line[dashpos+1:]
		iv = Random.new().read(AES.block_size);
		self.send('{0}{1}{2}'.format('ID'.format(ID),base64.b64encode(self.security.encrypt(DETAILS,'AES', 'thisisakey', AES.MODE_CBC, iv)),self.security.hash('{0}{1}'.format(ID,DETAILS),'sha224')))
	def disconnect(self):
		self.sockt.close()
	def send(self,data):
		self.sockt.sendall(data)
	def savekeyConfig(self, publickey, privatekey):
		config = {}
		config['publickey'] = publickey
		config['privatekey'] = privatekey
		pickle.dump(config, open('./data/client_config.pkl','w'))
	def sendEmail(self,To, From, data):
		print('--\temail menu\t--')
		emailbuffer = BIO.MemoryBuffer(data) #creating a buffer with the email data

		# Instantiate an SMIME object; set it up; sign the buffer.
		s = SMIME.SMIME()
		s.load_key('keys/email/comodoEmailcert.pem', 'keys/email/comodoEmailcert.pem')
		p7 = s.sign(emailbuffer)
		print(p7)
	def interface(self):
		inputv = ''			
		while (inputv!='q'):
			inputv = input('--\tMenu\t--\n1. Send File\n2. Send email.\n')
			if (inputv==1):
				inputv = input("Location of file:")
				File = open(inputv,'r')
				self.sendFile(File)
			elif(inputv==2):
				data = raw_input("Enter sample msg:")
				To = raw_input("email receipeint:")
				From = raw_input("email sender")
				self.sendEmail(To,From, data)
				
		
if __name__=='__main__':
	client = client('localhost', 7778)
	client.connect()
	client.interface()
	client.disconnect()
