#!/usr/bin/python
# -*- coding: utf-8 -*-
# Copyright 2015 kenjoe41
#
#   Licensed under the Apache License, Version 2.0 (the "License");
#   you may not use this file except in compliance with the License.
#   You may obtain a copy of the License at
#
#       http://www.apache.org/licenses/LICENSE-2.0
#
#   Unless required by applicable law or agreed to in writing, software
#   distributed under the License is distributed on an "AS IS" BASIS,
#   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#   See the License for the specific language governing permissions and
#   limitations under the License.

from __future__ import print_function
import getpass, os, json, argparse, sys
import requests
from linguist.libs.file_blob import FileBlob
requests.packages.urllib3.disable_warnings()

json_file = 'languages.json'
ghostfolder = os.environ['HOME']+'/.ghostpaste'
if not os.path.isdir(ghostfolder):
	os.makedirs(ghostfolder)

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
			return content
	except IOError as err:
		print("Error reading file: %s"%str(err), file=sys.stderr)
		sys.exit()

def get_stdin():
    stdin_lines = []
    for line in sys.stdin:
        stdin_lines.append(line)
    return ''.join(stdin_lines)

def download_file(url):
	filename = url.split('/')[-1]

	print ("Downloading \"%s\" file." % filename)
	owd = os.getcwd()
	os.chdir(ghostfolder)
	r = requests.get(url, stream=True, verify=False)
	with open(filename, 'wb') as f:
		for chunk in r.iter_content(chunk_size=1024): 
			if chunk:
				f.write(chunk)
				f.flush()
	print('File downloading...Done.')
	os.chdir(owd)

def getID(code_file):
	"""Get the language ID of the input file language"""
	json_path = ghostfolder+'/'+json_file
	if os.path.exists(json_path):
		pass
	else:
		download_file('https://ghostbin.com/languages.json')

	lang = detect_lang(code_file)

	json_data = json.load(file(json_path))#don't think i need this though
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
	parser.add_argument("-f", "--file", dest="filename", required=False,
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
	
	text = ''
	if args.filename:
		text = read_file(args.filename)
	else:
		print("\nNo File specified, using STDIN. Press Ctr+D to exit:\n")
		text = get_stdin()

	try:
		if os.stat(args.filename).st_size > 1*1024*1024: #1MB
			return print ("Sorry, file too large. Can't continue")
	except TypeError:
		if len(text) > 1*1024*1024:
			return print ("Sorry, text too large. Can't continue")
	params['text'] = text
	
	if args.passwd:
		passwd = getpass.getpass('Password to encrypt code: ')
		params['password'] = passwd
	if args.expire:#TODO:get expire time and verify commandline format given
		params['expire'] = args.expire
	if args.filename:
		ID = getID(args.filename)
	else:
		ID = 'Text'
	if ID is not '':
		params['lang'] = ID

	host = 'ghostbin.com'
	post_url = '/paste/new'
	url = 'https://'+host+post_url#Use https to allow encryption and authentication. API restriction

	print('Uploading file: \'{0}\''.format(args.filename or 'STDIN TEXT'))
	r = requests.post(url, params=params, headers=headers, verify=False)

	if r.status_code == requests.codes.ok:
	#Everything went fine, print paste URL and Session cookie
		print ('File Uploaded to URL: {0}'.format(r.url))
	else:
		print('Something went wrong: {0}. Try again'.format(r.status_code))
if __name__ == "__main__":
	main()
