#
# Zola Mahlaza
# 09 March 2014
#
import socket
class client(object):
	sockt = None
	host = None
	port = 0
	def __init__(self, host, port, sockettype='tcp'):
		self.host = host
		self.port = port
		if (sockettype=='tcp'):
			self.sockt = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		else:
			self.sockt = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
	def connect(self):
		self.sockt.connect((self.host, self.port))
	def disconnect(self):
		self.sockt.close()
	def send(data):
		self.sockt.send(data)
if __name__=='__main__':
	client = client('localhost', 7777, 'tcp')
	client.connect()
	client.send('hello')
	client.disconnect()
