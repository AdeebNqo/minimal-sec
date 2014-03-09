#
# Zola Mahlaza
# 8 March 2014
#
import shelve
import pickle
import os
import SocketServer
class server(SocketServer.BaseRequestHandler):
	files = []
	keytore =[]
	def __init__(self):
		exists = False
		try:
			items = os.listdir('./data')
			tmpcount = 0
			for item in items:
				if (item=='keystore.ks' or item=='files.pkl'):
					tmpcount=tmpcount+1
					if (tmpcount==2):
						exists=True
						break
		except OSError:
			os.mkdir('./data')
		if (exists==False):
			#Creating the empty files
			open('./data/keystore.ks','w').close()
			open('./data/files.pkl','w').close()
		else:
			try:
				#load the stored files
				files = pickle.load(open('./data/files.pkl','r'))
				#loading stored keys
				keystore = shelve.open('keystore.ks')
			except EOFError:
				#the files are empty
				files = []
				keystore =[]
	def handle(self):
		self.data = self.rfile.readline().strip()
		print('{} says'.format(self.client_address[0]))
		print(data)
		
if __name__=='__main__':
	#ToDo: read server config
	finalserver = SocketServer.TCPServer(('localhost', 7777),server, 'tcp')
	
