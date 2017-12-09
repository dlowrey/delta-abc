from src.transactions.transaction import Transaction
from ecdsa import SigningKey, NIST256p
import unittest
import json
import os

class TestTransactions(unittest.TestCase):

    def setUp(self):
        """
        Set up an unspent transaction output
        file to test a new Transaction with
        """
        self.sender_private_key = SigningKey.generate(curve=NIST256p)
        self.sender_public_key = self.sender_private_key.get_verifying_key()

        with open('blockchain/unspent_outputs.json', 'w') as f:
            out = {
                    "transaction_id": "faketransactionid",
                    "block_id": "fakeblockid",
                    "output_index": 1,
                    "amount": 25.0
                  }
            f.write("{}\n".format(json.dumps(out)))
    
    def tearDown(self):
        """
        Remove the unspent transaction output file
        used.
        """
        
        os.remove('blockchain/unspent_outputs.json')
    
    def test_add_transaction_output(self):
        tnx = Transaction()
        actual = tnx.add_output("senderaddress", "receiveraddress", 10)

        expected = [{'amount': 10, 'receiver_address': 'receiveraddress'},
                {'amount': 15.0, 'receiver_address': 'senderaddress'}]
        self.assertListEqual(expected, actual)

    def test_finialize_transaction(self):
        tnx = Transaction()
        tnx.add_output("senderaddress", "receiveraddress", 10)
        actual_tnx_id = tnx.finalize(self.sender_private_key, self.sender_public_key)
        not_expected = None
        self.assertNotEqual(not_expected, actual_tnx_id)
        

