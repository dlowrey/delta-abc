"""
Test the main features of the Block class,
including creating, adding transactions, mining,
and verifying the validity of a block.
"""
from datetime import datetime
from time import time
from collections import OrderedDict
import unittest
import json
from src.blocks.block import Block


class TestBlocks(unittest.TestCase):

    def setUp(self):
        # mock a transaction
        self.tnx = {
                'transaction_id': 'faketransactionid',
                'unlock': {},  # don't care
                'input_count': 0,  # dont't care
                'inputs': [],  # don't care
                'output_count': 0,  # don't care
                'outputs': [],  # don't care
                }
        # mock a block object
        timestamp = datetime.fromtimestamp(time()).strftime('%Y-%m-%d %H:%M:%S')
        self.block = {
                'block_id': 'fakeblockid',
                'previous_block_id': 'fakepreviousblockid',
                'timestampe': timestamp,
                'data' : {'faketransactionid': self.tnx}
                }
        # save the config file
        with open('data/node_info.json', 'r') as f:
            self.config_save = f.read()

    def tearDown(self):
        # reset the config file
        with open('data/node_info.json', 'w') as f:
            f.write(self.config_save)

    
    def test_create_block(self):
        block = Block()
        actual = block.add_transaction(self.tnx)
        expected = {'faketransactionid': self.tnx}
        self.assertDictEqual(actual, expected)

    def test_mine_block(self):
        block = Block()
        block.add_transaction(self.tnx)
        actual = block.mine()
        actual['timestamp'] = ''
        expected = {
                "previous_block_id": "",
                "data": {
                    "faketransactionid": {
                        "input_count": 0,
                        "output_count": 0,
                        "transaction_id": "faketransactionid",
                        "outputs": [],
                        "unlock": {},
                        "inputs": []
                        }
                    },
                "version": 0,
                "mining_proof": 813349,
                "timestamp": "",
                "block_id": "46e3c57efe9a1af7ba27c024cb22dcc88c214b74890cbc5cbf24a938c3395ae3"
                }
        self.maxDiff = None
        self.assertDictEqual(actual, expected)
