import pickle
import os
class Key():
	OwnPrivate = 0
	OwnPublic = 1
	ServerPub = 2
	EmailKey = 3
	EmailCert = 4
class KeyConfig():
	keydir = os.getcwd()
	keys = None
	keyfile ='{}/keys/keys.pkl'.format(self.keydir)
	#loading the pickle file
	def init(self):
		config = open(keyfile,'rb')
		self.keys = pickle.load(config)
		config.close()
	def get_keys(self,KeyOption):
		if (KeyOption==Key.OwnPrivate):
			return keys['ownprivate']
		elif (KeyOption==Key.OwnPub):
			return keys['ownpublic']
		elif (KeyOption==Key.ServerPub):
			return keys['serverpub']
		elif (KeyOption==Key.EmailKey):
			return keys['emailkey']
		elif (KeyOption==Key.EmailCert):
			return keys['emailcert']
		return 1
	def saveKey(self,Key,KeyPath):
		if (KeyOption==Key.OwnPrivate):
			keys['ownprivate'] = KeyPath
		elif (KeyOption==Key.OwnPub):
			keys['ownpublic'	] = KeyPath		
		elif (KeyOption==Key.ServerPub):
			keys['serverpub'] = KeyPath
		elif (KeyOption==Key.EmailKey):
			keys['emailkey'] = KeyPath
		elif (KeyOption==Key.EmailCert):
			keys['emailcert'] = KeyPath
		return 1

	def save(self):
		config = open(keyfile,'wb')
		pickle.dump(keys,config)
		config.close()
		print('saving keys')
