#
#
# Zola Mahlaza
# 09 March 2014
# 
# Client for sending encrypted files and emails
#
#   "Some people, when confronted with a problem, think "I know, I'll use regular expressions."
#   Now they have two problems."
#   -Jamie Zawinski
#
import random
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
from M2Crypto import BIO, Rand, SMIME, X509
from keyconfig import Key
from keyconfig import KeyConfig
import smtplib
from email.mime.text import MIMEText
from security import security
import subprocess

blocksize = 16 #Block size for the encryption

class client(object):
	sockt = None
	host = None
	port = 0
	privatekeylocation = None
	username = 'client001'
	security = None

	keyconfig = None
	serverpublickeylocation = None
	serveremailcertlocation = None
	def __init__(self, host, port):
		#accessing key configuration file
		self.keyconfig = KeyConfig('client')
		
		self.security = security()
		self.host = host
		self.port = port
		self.sockt = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		
		self.privatekeylocation = self.keyconfig.getConfigItem(Key.OwnPrivate)
		
	def connect(self):
		print('connecting....')
		self.sockt.connect((self.host, self.port))
		self.sockt.setblocking(1)
		authServers = self.keyconfig.getConfigItem(Key.OtherParties) #retrieving all authorized servers
		#identifying server to which client is connecting
		for server in authServers:
			if (server.address==self.sockt.getpeername()[0]):
				self.serverpublickeylocation=server.publickey
				self.serveremailcertlocation=server.emailcert 	
		print('connection established')
		print('initiating 3 way handshake...')
		#initiate three-way handshake
		self.send('CONNECT {}'.format(self.username))
		response = self.sockt.recv(1024).strip()
		print('server response is {}'.format(response))
		if (response=='101 CONNECT FAILED'):
			raise Exception('Connection failed 101. Client not recognized')
		else:
			#Here lies dragons --- taking response from server and desembling it
			vals = response.split()
			Ethreewaykey = base64.b64decode(vals[0])
			Etoken = base64.b64decode(vals[1])
			print('decrypting server gen 3way session key...')
			#Decrypting the threeway session key so that i can extract the token and nonce
			privkey = open(self.privatekeylocation,'rb').read()
			rsakey = RSA.importKey(privkey)
			rsakey = PKCS1_v1_5.new(rsakey)
			threewaykey = rsakey.decrypt(Ethreewaykey, -1)
			if (threewaykey!=-1):
				#if the threeway session key has been successfully decrypted
				print('decrypting sent token nonce pair...')
				#decrypting the (token,nonce) with the threeway session key
				tokenpair = self.security.decrypt(Etoken,'AES',threewaykey,AES.MODE_CBC)
				print('generating another 3way session key...')
				#generating another random key for encrypting the token nonce pair
				pool = map(chr,range(97,123))+map(chr,range(65,91))+map(chr,range(48,57))
				random.shuffle(pool)
				Clientthreewaykey = ''.join(pool[0:32])
				print('encrypting token pair...')
				#encrypting (token,nonce) pair with random key -- AES
				Etokenpair = self.security.encrypt(tokenpair,'AES',Clientthreewaykey,AES.MODE_CBC)
				Etokenpair = base64.b64encode(Etokenpair)
				print('encrypting client gen 3way session key...')
				#encrypting client generated threeway session key with server public keys
				pubkey = open(self.serverpublickeylocation).read()
				prsakey = RSA.importKey(pubkey)
				prsakey = PKCS1_v1_5.new(prsakey)
				EClientthreewaykey = base64.b64encode(prsakey.encrypt(Clientthreewaykey))
				#sending  E_s(k)||E_aes(token||nonce) to server
				cresponse = '{0} {1}'.format(EClientthreewaykey,Etokenpair)
				print('sending server response: {}'.format(cresponse))
				self.send(cresponse)
				print('done sending...')
			else:
				#could not decrypt server question thus cannot complete 3way handshake
				raise Exception('Could not decode server response. 3 way handshake failed.')
	def sendFile(self,File):
		line = File.readline()
		dashpos = line.find('-') #Dash position
		ID = line[0:dashpos].replace('ID','')
		print('id is {}'.format(ID))
		DETAILS = line[dashpos+1:]
		iv = Random.new().read(AES.block_size);
		self.send('{0} {1} {2}'.format(ID ,base64.b64encode(self.security.encrypt(DETAILS,'AES', 'thisisakey', AES.MODE_CBC, iv)),self.security.hash('{0}{1}'.format(ID,DETAILS),'sha512')))
		response = self.sockt.recv(1024)
		if (response=='FILERECIEVED'):
			print('file stored safely...')
		print('server says {}'.format(response))
	
	def disconnect(self):
		self.sockt.close()
	def send(self,data):
		self.sockt.sendall(data)
	def sendEmail(self):
		print('--\temail menu\t--')

		to = raw_input('recipient: ')
		From = raw_input('sender: ')
		ccList = []
		ccCode = 1
		while(ccCode!=1):
			ccCode = input('CC someone?\n1.Yes <Return if not>')
			if (ccCode==1):
				ccList.append(raw_input('cc address'))
		subject = raw_input('email subject: ')
		data = raw_input("msg:\n")
		#step 1 : signing email
		emailbuffer = BIO.MemoryBuffer(data) #creating a buffer with the email data

		# Instantiate an SMIME object; set it up; sign the buffer.
		smime = SMIME.SMIME()
		smime.load_key(self.keyconfig.getConfigItem(Key.EmailKey), self.keyconfig.getConfigItem(Key.EmailCert))
		p7 = smime.sign(emailbuffer)
	
		#step 2: encrypting email
		x509 = X509.load_cert(self.serveremailcertlocation)
		stack = X509.X509_Stack()
		stack.push(x509)
		smime.set_x509_stack(stack)

		smime.set_cipher(SMIME.Cipher('des_ede3_cbc'))
		tmp = BIO.MemoryBuffer()
		smime.write(tmp, p7, emailbuffer)
		p7 = smime.encrypt(tmp)
		
		out = BIO.MemoryBuffer()
		out.write('From: {}\n'.format(From))
		out.write('To: {}\n'.format(to))
		if (len(ccList)>0):
			ccline = 'Cc: '
			for i in range(len(ccList)):
				ccline=ccline+('{{0}} '.format(i))
			out.write(ccline % tuple(ccList))
		out.write('Subject: {}\n'.format(subject))
		smime.write(out,p7)
		print('connecting to email server...')
		server = smtplib.SMTP('smtp.gmail.com',587)
		server.ehlo()
                server.starttls()
		print('loging in...')
		#server.login(raw_input('Email server username:\n'),raw_input('Email server password:\n'))
		server.login('nishutch001','nishutch2014')
		print('sending email...')
		server.sendmail(From,to,out.read())
		print('closing email server connection...')
		server.quit()

	def interface(self):
		inputv = ''			
		while (inputv!='q'):
			inputv = input('--\tMenu\t--\n1. Send File\n2. Send email.\n')
			if (inputv==1):
				inputv = input("Location of file:")
				File = open(inputv,'r')
				self.send('FILESEND')
				self.sendFile(File)
			elif(inputv==2):
				self.sendEmail()
				
		
if __name__=='__main__':
	client = client('localhost', 7778)
	client.connect()
	client.interface()
	client.disconnect()
