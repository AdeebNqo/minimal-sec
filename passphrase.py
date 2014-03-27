#
# Zola Mahlaza (AdeebNqo)
# 26 March 2014
#
# Passphrase generator, wrapper for python faker https://github.com/joke2k/faker
#
# "The best thing about a boolean is even if you are wrong, you are only off by a bit."
# -Anonymous
#
import random
from faker import Factory
locale = [
	#'de_DE',
	#'cs_CZ',
	#'dk_DK',
	#'el_GR',
	'en_CA',
	'en_GB',
	'en_US'
	#'es_ES',
	#'es_MX',
	#'fa_IR',
	#'fi_FI',
	#'fr_FR',
	#'it_IT',
	#'ko_KR',
	#'pl_PL',
	#'pt_BR'
	]
lang = locale[random.randint(0,len(locale)-1)]
fake = Factory.create(lang)
categories = [
	'name','company','address'
	]
def getpassphrase():
	choice = categories[random.randint(0,2)]
	if (choice=='name'):
		return fake.name()
	elif (choice=='company'):
		return fake.company()
	elif (choice=='address'):
		return fake.address()
	return None
