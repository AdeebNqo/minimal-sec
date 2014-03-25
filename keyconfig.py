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
	#loading the pickle file
	def init(self):
		config = open('{}/keys/keys.pkl'.format(self.keydir),'r')
		self.keys = pickle.load(config)
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
		return None
	def saveKey(self,Key,KeyPath)
	def save(self):
		print('saving keys')
