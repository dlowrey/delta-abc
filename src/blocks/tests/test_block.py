"""
Test the main features of the Block class,
including creating, adding transactions, mining,
and verifying the validity of a block.
"""
from datetime import datetime
from time import time
import unittest
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
    def tearDown(self):
        pass


    
    def test_create_block(self):
        block = Block()
        actual = block.add_transaction(self.tnx)
        expected = {'faketransactionid': self.tnx}
        print(dict(block))
        self.assertDictEqual(actual, expected)
