#get expire time and verify commandline format given
#get language ID from /languages.json

import getpass, os, json
import requests
from __future__ import print_function
import linguist


def is_valid_file(parser,arg):
	"""verify the validity of the given file. Never trust the End-User"""
	if not os.path.exists(arg):
       		parser.error("File %s not found"%arg)
    	else:
        	return arg

def read_file(infilename):
    try:
        infile = open(infilename, 'r')
        content = infile.read()
	#content size here
        infile.close()
        return content
    except IOError as err:
	print("Error reading file: %s"%str(err), file=sys.stderr)

def download_file(url):
	filename = url.split('/')[-1]

	print "Downloading %s file." % filename
	r = requests.get(url, stream=True)
	with open(filename, 'wb') as f:
		for chunk in r.iter_content(chunk_size=1024): 
			if chunk:
				f.write(chunk)
				f.flush()
	return filename

def getID(code_file):
	"""Get the language ID of the input file language"""
	json_file = './languages.json'
	lang = (detect_lang(code_file) if detect_lang(code_file) is not None)
	
	if os.path.exists(json_file):
		pass
	else:
		json_file = download_file('https://ghostbin.com/languages.json')

	data = json.load(read_file(json_file))#don't think i need this though
	ID = data.read().split(lang + "\",\"id\":\"")[1]#doesn't take care of alt_id yet, squeeze HTH/Spacecow
	return ID
def detect_lang(path):
	"""Detect the language used in the given file."""
	blob = FileBlob(path, os.getcwd())
	if blob.is_text:
		return blob.language.name
	else:#images, binary and what-have-you won't be pasted
		return None

def main(argc, argv):
	parser = argparse.ArgumentParser(description='Upload code/text files to Ghostbin.')
	parser.add_argument("-f", "--file", dest="filename", required=True,
    		help="Input code/text file to upload",
    		metavar="FILENAME",type=lambda x:is_valid_file(parser,x))
	parser.add_argument("-e", "--expire", required=False, 
		help="Time to take before the text expires e.g '30µs', '10s', '1h', '15d'")#lambda func to verify time format
	parser.add_argument("-p", "--passwd", required=False, action='store_true', 
		default=False, help="Password for cases of encryption.")
	
	args = parser.parse_args()

	headers = {'content-type': 'application/x-www-form-urlencoded', 'User-Agent': agent}	

	if os.stat(args.filename).st_size > 1*1024*1024: #1MB
		return print "Sorry, file too large. Can't continue"

	if args.passwd:
		passwd = getpass.getpass('Password to encrypt code: ')
		headers['passwd'] = passwd
	if args.expire:
		headers['expire'] = args.expire
	headers['lang'] = getID(args.filename)

	text = read_file(args.filename)

	host = 'ghostbin.com'
	post_url = '/paste/new'
	url = 'https://'+host+post_url#Use https to allow encryption and authentication. API restriction
	agent = 'Mozilla/5.0 (Windows; U; MSIE 7.0; Windows NT 6.0; en-US)'

	r = requests.post(url, data=text, headers=headers)
	if r.status_code == requests.codes.ok:
	#Everything went fine, print paste URL and Session cookie

