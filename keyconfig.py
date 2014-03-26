import pickle
import os
import sys
import traceback
class Key():
	OwnPrivate = 0
	OwnPublic = 1
	ServerPublic = 2
	EmailKey = 3
	EmailCert = 4
class KeyConfig():
	keydir = os.getcwd()
	keys = {}
	keyfile =None
	#loading the pickle file
	def __init__(self, creator): # creator is eaither client or server
		self.keyfile = '{0}/keys/{1}/keys.pkl'.format(keydir,creator)
		#checking if key dir exists first
		if (os.path.isfile(self.keyfile)==False):
			#create file and save config
			print('--Key Configuration Menu---')
			response = 0
			try:
				while(response!=2):
					response = input('1. Enter all key configurations\n2.Done!\n:')
					if (response==1):
						self.saveKey(Key.OwnPublic,'{0}/{1}'.format(self.keydir, raw_input('Own public key:')))
						self.saveKey(Key.OwnPrivate,'{0}/{1}'.format(self.keydir,raw_input('Own private key:')))
						self.saveKey(Key.ServerPublic,'{0}/{1}'.format(self.keydir, raw_input('Server public key:')))
						self.saveKey(Key.EmailKey,'{0}/{1}'.format(self.keydir, raw_input('email key:')))
						self.saveKey(Key.EmailCert,'{0}/{1}'.format(self.keydir, raw_input('email certificate:')))
						self.save()
			except Exception:
				traceback.print_exc(file=sys.stdout)
				sys.exit(1)
		config = open(self.keyfile,'rb')
		self.keys = pickle.load(config)
		config.close()
	def getKey(self,KeyOption):
		if (KeyOption==Key.OwnPrivate):
			return self.keys['ownprivate']
		elif (KeyOption==Key.OwnPublic):
			return self.keys['ownpublic']
		elif (KeyOption==Key.ServerPublic):
			return self.keys['serverpub']
		elif (KeyOption==Key.EmailKey):
			return self.keys['emailkey']
		elif (KeyOption==Key.EmailCert):
			return self.keys['emailcert']
		return 1
	def saveKey(self,KeyOption,KeyPath):
		if (KeyOption==Key.OwnPrivate):
			self.keys['ownprivate'] = KeyPath
		elif (KeyOption==Key.OwnPublic):
			self.keys['ownpublic'] = KeyPath		
		elif (KeyOption==Key.ServerPublic):
			self.keys['serverpub'] = KeyPath
		elif (KeyOption==Key.EmailKey):
			self.keys['emailkey'] = KeyPath
		elif (KeyOption==Key.EmailCert):
			self.keys['emailcert'] = KeyPath
		return 1

	def save(self):
		config = open(self.keyfile,'wb')
		pickle.dump(self.keys,config)
		config.close()
