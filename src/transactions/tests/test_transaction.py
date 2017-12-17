"""
Test the main features of the Transaction class,
including creating, adding outputs, finalizing (signing),
verifying, recieving from network.
"""
from base64 import b64encode
import unittest
import json
import os
from src.persistence import files, access
from src.transactions.transaction import Transaction, verify
from ecdsa import SigningKey, NIST256p


class TestTransactions(unittest.TestCase):

    def setUp(self):
        """
        Set up an unspent transaction output
        file to test a new Transaction with
        """
        # mock up some signing keys to use
        self.sender_private_key = SigningKey.generate(curve=NIST256p)
        self.sender_public_key = self.sender_private_key.get_verifying_key()
        strpubkey = b64encode(self.sender_public_key.to_string()).decode()

        # mock an unspent output to use as an input for creating
        # new transactions
        self.unspent_output = {
            'transaction_id': 'faketransactionid',
            'block_id': 'testblock',
            'output_index': 0,
            'amount': 25.0
            }

        # mock a transactoin to use in a mocked block
        self.tnx = {
            'transaction_id': 'faketransactionid',
            'unlock': {},  # don't care now
            'input_count': 0,  # don't care now
            'inputs': [],  # don't care now
            'output_count': 1,
            'outputs': [{
                'receiver_address': strpubkey,
                'amount': 25.0,
                'spent_transaction_id': '',
                }]
            }

        # mock a block to use when verifying a new transaction
        self.block = {
            'block_id': 'testblock',
            'mining_proof': 0,  # don't care
            'previous_block_id': 'previousblockid',  # don't care
            'timestamp': 'today',  # don't care
            'data': {'faketransactionid': self.tnx}
            }

        # give a balance of 25 for testing
        with open(files.INFO_FILE, 'r+') as f:
            self.saved_info = f.read()
            info = json.loads(self.saved_info)
            f.truncate(0)
            f.seek(0)
            info['wallet']['balance'] = 25
            json.dump(info, f)

        # write the unspent output to it's file
        with open(files.UNSPENT_OUTPUTS, 'w') as f:
            f.write('{}\n'.format(json.dumps(self.unspent_output)))

        # write the block to its file
        with open(files.BLOCKCHAIN_DIR + 'testblock.json', 'w') as f:
            json.dump(self.block, f)

    def tearDown(self):
        """
        Remove the unspent transaction output file
        used.
        """
        # remove any data we used
        os.remove(files.UNSPENT_OUTPUTS)
        os.remove(files.BLOCKCHAIN_DIR + 'testblock.json')
        # set info back to original
        with open(files.INFO_FILE, 'w') as f:
            f.write(self.saved_info)

    def test_add_transaction_output(self):
        """
        Test adding a single output to a new transaction
        """
        tnx = Transaction()
        actual = tnx.add_output(
                'senderaddress',
                'receiveraddress',
                10,
                access.get_inputs(10)
                )

        expected = [{'amount': 10, 'receiver_address': 'receiveraddress'},
                    {'amount': 15.0, 'receiver_address': 'senderaddress'}]
        self.assertListEqual(expected, actual)

    def test_insufficient_funds(self):
        """
        Test adding an output with an amount more than the
        sender currently owns
        """
        with self.assertRaises(ValueError):
            tnx = Transaction()
            actual = tnx.add_output(
                    'senderaddress',
                    'receiveraddress',
                    10,
                    access.get_inputs(100)
                    )

    def test_finialize_transaction(self):
        """
        Test finalizing a transaction
        (completing and signing it)
        """
        tnx = Transaction()
        actual = tnx.add_output(
                'senderaddress',
                'receiveraddress',
                10,
                access.get_inputs(10)
                )
        actual_tnx_id = tnx.finalize(self.sender_private_key,
                                     self.sender_public_key)
        not_expected = None
        self.assertNotEqual(not_expected, actual_tnx_id)

    def test_verify_transaction(self):
        """
        Test verifying a valid transaction
        """
        tnx = Transaction()
        actual = tnx.add_output(
                'senderaddress',
                'receiveraddress',
                10,
                access.get_inputs(10)
                )
        tnx.finalize(self.sender_private_key, self.sender_public_key)

        auth, offender = verify(tnx)
        self.assertTrue(auth)

    def test_verify_invalid_transaction(self):
        """
        Test attempting to verify a transaction with an invalid
        output
        """
        tnx = Transaction()
        actual = tnx.add_output(
                'senderaddress',
                'receiveraddress',
                20,
                access.get_inputs(20)
                )
        tnx.finalize(self.sender_private_key, self.sender_public_key)

        # mess with transaction
        # this will invalidate the signature
        tnx.outputs[0]['receiver_address'] = 'evilmyaddress'

        auth, offender = verify(tnx)
        self.assertFalse(auth)
        self.assertIsNone(offender)

    def test_receive_network_transaction(self):
        """
        Test the Transaction Object constructor on recieving
        a derefrenced dict of transaction data
        """
        tnx = Transaction(**self.tnx)
        self.assertDictEqual(self.tnx, dict(tnx))
