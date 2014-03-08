#
# Zola Mahlaza
# 8 March 2014
#
import re
import smtpd
import hashlib
import keyczar.keyczar
def main():
	sec = Security()
	print(sec.hash("hello", 'sha256'))

#
# Security utility
#
class Security():
	#
	# Method for computing
	# a hash using a provided algorithm
	#
	def hash(self,data, hashAlgo):
		digester = None
		if (hashAlgo=='md5'):
			digester = hashlib.md5()
			digester.update(data)
			return digester.digest()
		elif (hashAlgo.startswith('sha')):
			regexWorker = re.compile("([a-zA-Z]+)([0-9]+)")
			groups = regexWorker.match(hashAlgo)
			num = int(groups.group(2))
			if (num==1):
				return hashlib.sha1(data).hexdigest()
			elif (num==224):
				return hashlib.sha224(data).hexdigest()
			elif (num==256):
				return hashlib.sha256(data).hexdigest()
			elif (num==384):
				return hashlib.sha384(data).hexdigest()
			elif (num==512):
				return hashlib.sha512(data).hexdigest()
			else:
				raise Exception('Hashing algorithm '+hashAlgo+' not recognized.')
		else:
			raise Exception('Hashing algorithm '+hashAlgo+' not recognized.')
	#
	#Method for encrypting data
	#using a specified public key
	#
	def encrypt(data, pathToKeys):
		crypter = keyczar.Crypter.Read();
        	return crypter.Encrypt(data);
if __name__=='__main__':
	main()
