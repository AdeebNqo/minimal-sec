#
# Zola Mahlaza
# 12 March 2014
# Security utility methods
#
import hashlib
from Crypto.Cipher import AES
from Crypto.Cipher import Blowfish
import re
class security():
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
	#-symetric encryption-
	#
	def encrypt(self,data, EncryptAlgo, key, mode):
		data = self.pad(data)
		key = self.hash(key,'sha512')
		iv = Random.new().read(AES.block_size)
		if (EncryptAlgo=='AES'):
			aesEncrypter = AES.new(key,mode,iv)
			return aesEncrypter.encrypt(data)
		elif (EncryptAlgo=='Blowfish'):
			blowfishEncrypter = Blowfish.new(key)
			return blowfishEncrypter.encrypt(data)
		elif (EncryptAlgo=='DES'):
			desEncrypter = DES.new(key)
			return desEncrypter.encrypt(data)
		else:
			raise Exception('Could not encrypt data.'+DecryptAlgo+' is not supported')
	#
	# Method for decrypting 
	#
	def decrypt(self,data, DecryptAlgo, key, mode):
		key = self.hash(key,'sha512')
		iv = Random.new().read(AES.block_size)
		if (DecryptAlgo=='AES'):
			aesDecrypter = AES.new(key,mode,iv)
			return self.unpad(aesDecrypter.decrypt(data))
		elif (DecryptAlgo=='Blowfish'):
			blowfishDecrypter = Blowfish.new(key)
			return self.unpad(blowfishDecrypter.decrypt(data))
		elif (DecryptAlgo=='DES'):
			desDecrypter = DES.new(key)
			return self.unpad(desDecrypter.decrypter(data))
		else:
			raise Exception('Could not decrypt data.'+DecryptAlgo+' is not supported')
	#
	# Method for padding the text for encryption
	#
	def pad(self,data):
		rem = length = 16 - (len(data) % 16)
		for i in range(rem):
			data=data+str(rem)
		return data
	#
	# Method for unpadding text after decryption
	#
	def unpad(self,data):
		return data
