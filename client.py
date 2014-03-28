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
from Crypto.Signature import PKCS1_v1_5 as pkc
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
from Crypto.Hash import SHA
import readline #for capturing key combinations in email sending

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
		print('STATUS: connecting....')
		self.sockt.connect((self.host, self.port))
		self.sockt.setblocking(1)
		authServers = self.keyconfig.getConfigItem(Key.OtherParties) #retrieving all authorized servers
		#identifying server to which client is connecting
		for server in authServers:
			if (server.address==self.sockt.getpeername()[0]):
				self.serverpublickeylocation=server.publickey
				self.serveremailcertlocation=server.emailcert 	
		print('STATUS: connection established')
		print('STATUS: initiating 3 way handshake...')
		#initiate three-way handshake
		self.send('CONNECT {}'.format(self.username))
		response = self.sockt.recv(1024).strip()
		#print('RESULT: server response is {}'.format(response))
		if (response=='101 CONNECT FAILED'):
			raise Exception('Connection failed 101. Client not recognized')
		else:
			#Here lies dragons --- taking response from server and desembling it
			authtokensplit = response.split()
			Ethreewaykey = base64.b64decode(authtokensplit[0])
			#print('RESULT: Ethreewaykey {}'.format(authtokensplit[0]))
			Etoken = base64.b64decode(''.join(authtokensplit[1:]))
			#print('RESULT: Etoken {}'.format(''.join(authtokensplit[1:])))
			#print('STATUS: decrypting server gen 3way session key...')
			#Decrypting the threeway session key so that i can extract the token and nonce
			privkey = open(self.privatekeylocation,'rb').read()
			rsakey = RSA.importKey(privkey)
			rsakey = PKCS1_v1_5.new(rsakey)
			threewaykey = rsakey.decrypt(Ethreewaykey, -1)
			#print('RESULT: threeway key: {}'.format(threewaykey))
			if (threewaykey!=-1):
				#if the threeway session key has been successfully decrypted
				#print('STATUS: decrypting (token,nonce) pair...')
				#decrypting the (token,nonce) with the threeway session key
				tokenpair = self.security.decrypt(Etoken,'AES',threewaykey,AES.MODE_CBC)
				#print('RESULT: tokennoncepair is : {}'.format(tokenpair))
				#print('STATUS: generating another 3way session key...')
				#generating another random key for encrypting the token nonce pair
				pool = map(chr,range(97,123))+map(chr,range(65,91))+map(chr,range(48,57))
				random.shuffle(pool)
				Clientthreewaykey = ''.join(pool[0:32])
				#print('RESULT: Clientthreewaykey {}'.format(Clientthreewaykey))
				#print('STATUS: encrypting (token,nonce) pair...')
				#encrypting (token,nonce) pair with random key -- AES
				Etokenpair = self.security.encrypt(tokenpair,'AES',Clientthreewaykey,AES.MODE_CBC)
				Etokenpair = base64.b64encode(Etokenpair)
				#print('RESULT: Encrypted token pair: {}'.format(Etokenpair))
				#print('STATUS: encrypting client gen 3way session key...')
				#encrypting client generated threeway session key with server public keys
				pubkey = open(self.serverpublickeylocation).read()
				prsakey = RSA.importKey(pubkey)
				prsakey = PKCS1_v1_5.new(prsakey)
				EClientthreewaykey = base64.b64encode(prsakey.encrypt(Clientthreewaykey))
				#print('RESULT: Encryptedthreewaykey {}'.format(EClientthreewaykey))
				#print('STATUS: Encrypted client gen threeway key: {}'.format(EClientthreewaykey))
				#sending  E_s(k)||E_aes(token||nonce) to server
				cresponse = '{0} {1}'.format(EClientthreewaykey,Etokenpair)
				#print('STATUS: sending {} to the server'.format(cresponse))
				self.send(cresponse)
				print('STATUS: done sending...')
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
		#Compiuting hash of id and details
		hashX = SHA.new('{0} {1}'.format(ID,DETAILS))
		#Signing hash of id and details with owners private key
		privkey = open(self.privatekeylocation,'rb').read()
		rsakey = RSA.importKey(privkey)
		signer = pkc.new(rsakey)
		signedHash = signer.sign(hashX)
		self.send('{0}\t{1}\t{2}'.format(ID ,base64.b64encode(self.security.encrypt(DETAILS,'AES', 'thisisalocalmasterkey', AES.MODE_CBC)),signedHash))
		response = self.sockt.recv(1024)
		if (response=='FILERECIEVED'):
			print('file stored safely...')
		elif (response=='FILECHANGED'):
			print('File has been corrupted. Server received altered file.')
		print('server says {}'.format(response))
	
	def disconnect(self):
		self.sockt.close()
	def send(self,data):
		self.sockt.sendall(data)
	def sendEmail(self):
		readline.parse_and_bind('C-k: "@\n"')
		print('--\temail menu\t--')
		to = raw_input('Recipient: ')
		From = raw_input('Sender: ')
		ccList = []
		ccCode = 2
		while(ccCode!=1):
			ccCode = raw_input('CC someone?\n1.Yes <Return for no>')
			if (ccCode==1):
				ccList.append(raw_input('CC address:'))
			else:
				break
		subject = raw_input('email subject: ')
		emailbody = []
		line ="@"
		print('Email body (Ctrl-K for line break, ignore generated @ symbol):')
		while(line and line[-1]=='@'):
			line = raw_input('')
			if line.endswith('@'):
				emailbody.append(line[:-1])
			else:
				emailbody.append(line)
		data = '\n'.join(emailbody)
		#
		#step 1 : signing email
		#
		
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
		server.sendmail(erom,to,out.read())
		print('closing email server connection...')
		server.quit()
	def retrieveFile(self,ID):
		self.send('FILERETRIEVE')
		print('sending id..')
		self.send(ID)
		print('waiting for edetails...')
		#wait for encrypted details of file
		edetails = self.sockt.recv(3000)
	def interface(self):
		inputv = ''			
		while (inputv!='q'):
			inputv = input('--\tMenu\t--\n1. Send File\n2. Send email.\n3.Get file details.\n4.Exit\n')
			if (inputv==1):
				inputv = input("Location of file:")
				File = open(inputv,'r')
				self.send('FILESEND')
				self.sendFile(File)
			elif(inputv==2):
				self.sendEmail()
			elif (inputv==3):
				self.retrieveFile(raw_input('ID:'))
			elif (inputv==4):
				self.disconnect()
				print('shutting down...')
				sys.exit(0)
		
if __name__=='__main__':
	client = client('localhost', 7778)
	client.connect()
	client.interface()
	client.disconnect()
