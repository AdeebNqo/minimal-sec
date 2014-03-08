#
# Zola Mahlaza
# 8 March 2014
#
import re
import smtpd
import hashlib
from Crypto.Cipher import AES
from Crypto.Cipher import Blowfish
def main():
	sec = Security()
	print(sec.encrypt('asasasasasasasas','AES','aaaaaaaaaaaaaaaa'))

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
	def encrypt(self,data, EncryptAlgo, key):
		if (EncryptAlgo=='AES'):
			aesEncrypter = AES.new(key)
			return aesEncrypter.encrypt(data)
		elif (EncryptAlgo=='Blowfish'):
			blowfishEncrypter = Blowfish.new(key)
			return blowfishEncrypter.encrypt(data)
		elif (EncryptAlgo=='DES'):
			desEncrypter = DES.new(key)
			return desEncrypter(data)
		else:
			raise Exception('Could not encrypt data.'+DecryptAlgo+' is not supported')
	#
	# Method for decrypting 
	#
	def decrypt(self,data, DecryptAlgo, key):
		if (DecryptAlgo=='AES'):
			aesDecrypter = AES.new(key)
			return aesDecrypter.decrypt(data)
		elif (DecryptAlgo=='Blowfish');
			blowfishDecrypter = Blowfish.new(key)
			return blowfishDecrypter.decrypt(data)
		elif (DecryptAlgo=='DES'):
			desDecrypter = DES.new(key)
			return desDecrypter.decrypter(data)
		else:
			raise Exception('Could not decrypt data.'+DecryptAlgo+' is not supported')
if __name__=='__main__':
	main()
