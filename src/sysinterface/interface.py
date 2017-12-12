"""
A module that allows basic blockchain functionality
through simple functions that carry out more complicated
techniques.

To be uesd by a user-facing interface or command line client
"""
import os
from ecdsa import SigningKey, VerifyingKey, NIST256p
from src.transactions.transaction import Transaction
from src.blocks.block import Block
from src.data-access import access, files


def on_start(options=None):
    """
    Tasks to complete when the system starts up
    """

    check_keys()


def check_keys():
    """
    Check the info file for the existence of private/public keys.
    """
    rewrite = False
    with open(files.INFO_FILE, 'r+') as f:
        info = json.load(f)
        private_key = info['wallet']['private_key']
        public_key = info['wallet']['public_key']
        # Check for a private key
        if not private_key:
            rewrite = True
            a = input('Do you have a private key? (y/n): ')
            if a == 'y':
                private_key = input('Please input your private key: ')
            else:
                private_key = SigningKey.generate(curve=NIST256p).to_string() 
        # Check for a public key
        if not public_key:
            rewrite = True
            public_key = SigningKey.from_string(
                    private_key,
                    curve=NIST256p).get_verifying_key().to_string()
        # If the user was missing a private or public key, write the new ones
        if rewrite:
            info['wallet']['private_key'] = private_key
            info['wallet']['public_key'] = public_key
            f.truncate(0)
            f.seek(0)
            json.dump(info, f)

def on_stop():
    pass
