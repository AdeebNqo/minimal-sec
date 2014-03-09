#
# Zola Mahlaza
# 09 March 2014
#
import socket
class client(object):
	sockt = None
	host = None
	port = 0
	def __init__(self, host, port):
		self.host = host
		self.port = port
		self.sockt = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	def connect(self):
		self.sockt.connect((self.host, self.port))
	def disconnect(self):
		self.sockt.close()
	def send(self,data):
		self.sockt.send(data)
if __name__=='__main__':
	client = client('localhost', 7777)
	client.connect()
	client.send('hello')
	client.disconnect()
