#
# Zola Mahlaza
# 8 March 2014
#
import shelve
import pickle
import os
import ServerSocket
class server(ServerSocket.BaseRequestHandler):
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
			#load the stored files
			files = pickle.load(open('files.pkl','r'))
			#loading stored keys
			keystore = shelve.open('keystore.ks')
	def handle(self):
		print('')
if __name__=='__main__':
	finalserver = None
	#reading server config
	#try:
	config = pickle.load('config.pkl')
	socket_type = config['socket_type']
	if (socket_type=='udp'):
		finalserver = ServerSocket.UDPServer((localhost,7777),server)
	else:
		finalserver = ServerSocket.TCPServer((localhost, 7777),server)
	if (finalserver!=None):
		finalserver.serve_forever()
	else:
		raise Exception('Cannot start server. Try setting up config.pkl')
	
