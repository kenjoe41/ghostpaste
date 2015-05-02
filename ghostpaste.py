#!/usr/bin/python
# -*- coding: utf-8 -*-

#get expire time and verify commandline format given

from __future__ import print_function
import getpass, os, json, argparse, sys
import requests
from linguist.libs.file_blob import FileBlob
requests.packages.urllib3.disable_warnings()


def is_valid_file(parser,arg):
	"""verify the validity of the given file. Never trust the End-User"""
	if not os.path.exists(arg):
       		parser.error("File %s not found"%arg)
	else:
	       	return arg

def read_file(infilename):
	try:
		with open(infilename, 'rb') as f:
			content = f.read()
			#content size here
			return content
	except IOError as err:
		print("Error reading file: %s"%str(err), file=sys.stderr)
		sys.exit()

def download_file(url):
	filename = url.split('/')[-1]

	print ("Downloading \"%s\" file." % filename)
	r = requests.get(url, stream=True, verify=False)
	with open(filename, 'wb') as f:
		for chunk in r.iter_content(chunk_size=1024): 
			if chunk:
				f.write(chunk)
				f.flush()
	print('File downloading...Done.')
	return filename

def getID(code_file):
	"""Get the language ID of the input file language"""
	json_file = 'languages.json'
	
	if os.path.exists(json_file):
		pass
	else:
		json_file = download_file('https://ghostbin.com/languages.json')

	lang = detect_lang(code_file)

	json_data = json.load(file(json_file))#don't think i need this though
	ID = ''
	for  i in range(len(json_data)):
		temp = len(json_data[i]['languages'])
		for j in range(temp):	
			if json_data[i]['languages'][j]['name'].lower() == lang.lower():
				ID = json_data[i]['languages'][j]['id']
				print('Gotten language ID from \'languages.json\': {0}'.format(ID))
				return ID
def detect_lang(path):
	"""Detect the language used in the given file."""
	blob = FileBlob(path, os.getcwd())
	if blob.is_text:
		print('Programming language of the file detected: {0}'.format(blob.language.name))
		return blob.language.name
	else:#images, binary and what-have-you won't be pasted
		print('File not a text file. Exiting...')
		sys.exit()

def main():
	parser = argparse.ArgumentParser(description='Upload code/text files to Ghostbin.')
	parser.add_argument("-f", "--file", dest="filename", required=True,
    		help="Input code/text file to upload",
    		metavar="FILENAME",type=lambda x:is_valid_file(parser,x))
	parser.add_argument("-e", "--expire", required=False, 
		help="Time to take before the text expires e.g '30µs', '10s', '1h', '15d'")#lambda func to verify time format
	parser.add_argument("-p", "--passwd", required=False, action='store_true', 
		default=False, help="Password for cases of encryption.")
	
	args = parser.parse_args()

	agent = 'Mozilla/5.0 (Windows; U; MSIE 7.0; Windows NT 6.0; en-US)'
	headers = {'content-type': 'application/x-www-form-urlencoded', 'User-Agent': agent}
	params = {}

	if os.stat(args.filename).st_size > 1*1024*1024: #1MB
		return print ("Sorry, file too large. Can't continue")

	if args.passwd:
		passwd = getpass.getpass('Password to encrypt code: ')
		param['passwd'] = passwd
	if args.expire:
		params['expire'] = args.expire
	ID = getID(args.filename)
	if ID is not '':
		params['lang'] = ID

	text = read_file(args.filename)
	params['text'] = text

	host = 'ghostbin.com'
	post_url = '/paste/new'
	url = 'https://'+host+post_url#Use https to allow encryption and authentication. API restriction

	print('Uploading file: \'{0}\''.format(args.filename))
	r = requests.post(url, params=params, headers=headers, verify=False)

	if r.status_code == requests.codes.ok:
	#Everything went fine, print paste URL and Session cookie
		print ('File Uploaded to URL: {0}'.format(r.url))
	else:
		print('Something went wrong: {0}. Try again'.format(r.status_code))
if __name__ == "__main__":
	main()
