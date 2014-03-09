#	
# Zola Mahlaza
# 8 March 2014
#
import shelve
import pickle
import os
import SocketServer
class server(SocketServer.TCPServer):
	files = []
	keytore =[]
	def __init__(self,address, handler):
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
		SocketServer.TCPServer.__init__(self, address, handler)
class serverhandler(SocketServer.BaseRequestHandler):
	def handle(self):
		print('{} just connected'.format(self.client_address[0]))
		data = self.request.recv(1024).strip()
		print('{} says'.format(self.client_address[0]))
		print(data)
		
if __name__=='__main__':
	#ToDo: read server config
	finalserver = server(('localhost', 7777),serverhandler)
	finalserver.serve_forever()
