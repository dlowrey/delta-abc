"""
Test the main features of the Block class,
including creating, adding transactions, mining,
and verifying the validity of a block.
"""
from datetime import datetime
from time import time
from collections import OrderedDict
import unittest
import os
import json
from src.blocks.block import Block


class TestBlocks(unittest.TestCase):

    def setUp(self):
        # mock a transaction
        self.tnx = {
                'transaction_id': 'faketransactionid',
                'unlock': {
                    'public_key':'test', 
                    'signature': 'testsig'
                    },
                'input_count': 0,  # dont't care
                'inputs': [],  # don't care
                'output_count': 0,  # don't care
                'outputs': [],  # don't care
                }
                
        # mock a block object
        block_id = '9dccd2b72bf3e49b12bca7d6d5cbc144be5fea17a230f4fefe342639e71a3608'
        self.block = {
                'block_id': block_id,
                'previous_block_id': '',
                'timestamp': '',
                'data' : {'faketransactionid': self.tnx},
                'version': 0,
                'mining_proof': 944944,
                }

        # save the config file
        with open('data/node_info.json', 'r') as f:
            self.config_save = f.read()

    def tearDown(self):
        # reset the config file
        with open('data/node_info.json', 'w') as f:
            f.write(self.config_save)

    
    def test_create_block(self):
        """
        Test creating a new block and adding a single
        transaction object to it
        """
        block = Block()
        actual = block.add_transaction(self.tnx)
        expected = {'faketransactionid': self.tnx}
        self.assertDictEqual(actual, expected)

    def test_mine_block(self):
        """
        Test the mining process on a newly created block
        """
        block = Block()
        block.add_transaction(self.tnx)
        actual = block.mine()
        actual['timestamp'] = ''  # the timestamp will always be different
        expected = self.block
        self.maxDiff = None
        self.assertDictEqual(actual, expected)

    def test_verify_block(self):
        """
        Test the verification of a complete block to see
        if the proof of work was really done
        """
        block = Block(**self.block)
        auth = block.verify()
        self.assertTrue(auth)

    def test_verify_invalid_block(self):
        """
        Test the verificaiton of a complete block
        when the proof of work was not done
        """
        self.block['mining_proof'] = 0
        block = Block(**self.block)
        auth = block.verify()
        self.assertFalse(auth)

        

