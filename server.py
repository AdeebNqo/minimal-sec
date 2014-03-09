#
# Zola Mahlaza
# 8 March 2014
#
import shelve
import pickle
import os
import SocketServer
class server():
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
#
# Class to handle tcp connections
#
class tcpHandler(SocketServer.BaseRequestHandler):
	def handle(self):
		print('tcp')
#
# Class to handle udp connections
#
class udpHandler(SocketServer.BaseRequestHandler):
	def handle(self):
		print('udp')
if __name__=='__main__':
	finalserver = None
	sockettype = None
	#reading server config
	#try:
	try:
		config = pickle.load('config.pkl')
		sockettype = config['socket_type']
	except AttributeError:
		pass
	if (sockettype=='udp'):
		finalserver = SocketServer.UDPServer(('localhost',7777),udpHandler)
	else:
		finalserver = SocketServer.TCPServer(('localhost', 7777),tcpHandler)
	if (finalserver!=None):
		finalserver.serve_forever()
	else:
		raise Exception('Cannot start server. Try setting up config.pkl')
	
