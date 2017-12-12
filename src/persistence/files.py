"""
Module that contains functions necessary for the
creation of files needed for the system to run
"""
import json
import os


# Global file paths for easier maintenance
# Directories
DATA_DIR = 'data/'
BLOCKCHAIN_DIR = '{}{}'.format(DATA_DIR, 'blockchain/')
# Files
INFO_FILE = '{}{}'.format(DATA_DIR, 'info.json')
UNSPENT_OUTPUTS = '{}{}'.format(DATA_DIR, 'unspent_outputs.txt')


def create_data_dir():
    """ Create the data directory """
    os.mkdir(DATA_DIR)


def create_info_file():
    """ Create a blank info file """
    with open(INFO_FILE, 'w') as f:
        json.dump({
            'previous_block_id': '',
            'wallet': {
                'balance': 0.0,
                'private_key': '',
                'public_key': '',
                'address': ''
                },
            'current_version': '1.0',
            'versions': {
                '1.0': {'difficulty': 5}
                }
            }, f)


def create_blockchain_dir():
    os.mkdir(BLOCKCHAIN_DIR)


def create_unspent_outputs_file():
    open(UNSPENT_OUTPUTS, 'w').close()
