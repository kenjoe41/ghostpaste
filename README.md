===============================================
ghostpaste - upload code or text to ghostbi.com
===============================================


examples
========
* post a public paste on Ghostbin:
  ``cat doge | ghostpaste``   or
  ``ghostpaste -f file.py``

* post a password protected paste:
  ``cat doge | ghostpaste -p``
  ``ghostpaste -f file.py -p``

* post a paste that expires on Ghostbin:
  ``cat doge | ghostpaste -e 1m``
  ``ghostpaste -f file.py -e 1m``

* post a paste that is password protcted and it expires:
  ``cat doge | gister -pe 5s``

usage
=====

.. code:: console

usage: ghostpaste [-h] [-f FILENAME] [-e EXPIRE] [-p]

Upload code/text files to Ghostbin.

optional arguments:
  -h, --help            show this help message and exit
  -f FILENAME, --file FILENAME
                        Input code/text file to upload
  -e EXPIRE, --expire EXPIRE
                        Time to take before the text expires e.g '30µs',
                        '10s', '1h', '15d'
  -p, --passwd          Password for cases of encryption.

install
=======
* ``pip install ghostpaste`` or clone the repo and ``python setup.py install``

supported languages - languages.json
====================================
This file is provided and it contains a list of supported languages that ghostbin has syntax highlighting for. If it isn't in the specified folder, it is downloaded and stored in the specified folder.
The json might be alittle jumbled but a custom parser has been written to pass it, though it needs improvement. Prolly when i get time.

Ghostbin API
============
API: https://ghostbin.com/paste/p3qcy
