import pickle
import os
import sys
import traceback

#
# Copyright 2014 Zola Mahlaza
# Maintains configuration for finding all keys for the program
#
# "It always takes longer than you expect, even when you take into account Hofstadter's Law."
# -  Hofstadter's Law
#

class OtherParty():
	emailkey = None
	publickey = None
	def setemailkey(self,emailkey):
		self.emailkey = emailkey
	def setpublickey(self,publickey):
		self.publickey = publickey
class ClientParty(OtherParty):
	username = None
	def __init__(self,username):
		self.username = username
		super().__init__()
class ServerParty(OtherParty):
	address = None
	def __init__(self,address):
		self.address = address
		super().__init__()
class Key():
	OwnPrivate = 0
	OwnPublic = 1
	EmailKey = 2
	EmailCert = 3
	OtherParties = 4
class KeyConfig():
	currdir = os.getcwd()
	conf = {}
	keyfile ='{}/keys/keys.pkl'.format(keydir)
	#loading the pickle file
	def __init__(self,creatorType): #creatorType is the type of controller: client or server
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
						self.saveKey(Key.EmailKey,'{0}/{1}'.format(self.keydir, raw_input('email key:')))
						self.saveKey(Key.EmailCert,'{0}/{1}'.format(self.keydir, raw_input('email certificate:')))
						if (creator=='client'):
							print('doing stuff for client')
						elif (creator=='server'):
							print('doing stuff for server')
						self.save()
			except Exception:
				traceback.print_exc(file=sys.stdout)
				sys.exit(1)
		configfile = open(self.keyfile,'rb')
		self.keys = pickle.load(configfile)
		config.close()
	def getConfigItem(self,KeyOption):
		if (KeyOption==Key.OwnPrivate):
			return self.config['ownprivate']
		elif (KeyOption==Key.OwnPublic):
			return self.config['ownpublic']
		elif (KeyOption==Key.EmailKey):
			return self.config['emailkey']
		elif (KeyOption==Key.EmailCert):
			return self.config['emailcert']
		elif (KeyOption==Key.OtherParties):
			return self.config['otherparties']
		return 1
	def saveKey(self,KeyOption,KeyPath):
		if (KeyOption==Key.OwnPrivate):
			self.config['ownprivate'] = KeyPath
			return 1
		elif (KeyOption==Key.OwnPublic):
			self.config['ownpublic'] = KeyPath		
			return 1
		elif (KeyOption==Key.EmailKey):
			self.config['emailkey'] = KeyPath
			return 1
		elif (KeyOption==Key.EmailCert):
			self.config['emailcert'] = KeyPath
			return 1
		return 0
	def saveOtherParty(self,otherParty):
		self.config['otherparties'].append(otherParty)
		return 0
	def save(self):
		configfile = open(self.keyfile,'wb')
		pickle.dump(self.config,configfile)
		config.close()
