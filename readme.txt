Make sure to install python-twisted package with 'sudo apt-get install python-twisted'
Use Python 3.5

Will not run without id_rsa and id_rsa.pub private and public keyfiles in the same directory.
You can generate these with openssh-keygen.

Dependencies:

twisted[conch]
mysqlclient
requests
fs

MUST SET UP ONLY THESE LIBRARIES IN A VIRTUAL ENVIRONMENT _AND_ ACTIVATE THE VIRTUAL ENVIRONMENT WITH
source ./venv/bin/activate

before running python3.5 activehoneypot.py

If you don't do this you will get terrible errors and tears.