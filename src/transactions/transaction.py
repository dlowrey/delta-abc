"""
Class for handling the creation of Transaction objects from
scratch (by adding outputs) or from a network received json
transaction (passed in as a dict). Hanldes the signing and
verifying
"""
from base64 import b64encode
from hashlib import sha256


class Transaction(object):

    """
    Represents a single Transaction object

    A transaction object contains inputs and outputs, authorization mechanisms,
    as well as information about itself such as the transaction's id, and
    the block id that it belongs to (if any).

    Format (returned when a complete transaction object is casted to dict()):
        {
            transaction_id: string
            unlock: json object
            input_count: int
            inputs: array
            output_count: int
            outputs: array
        }

        Inputs:
            Inputs verify that the sender owns the currency the system is
            about to send. Inputs do this by their structure, they are
            refrences (by transaction_id, block_id, output_index)
            to a previous transaction output (that will be used in this
            new transaction) that exists in the blockchain.

            Format:
                {
                    transaction_id: string
                    block_id: string
                    output_index: int
                    amount: float
                }

        Outputs:
            Outputs signify who the transaction is going to and how much
            currency is in the transaction. Outputs contain the receivers
            address and the amount sent to that address, as well as if
            the output has been spent or not (as an input in another
            transaction).

            The total amount of cryptocurrency in the outputs must be equal
            to the total amount in the inputs. I.e., all inputs must be
            used up. This means that when sending a transaction, any
            unused input amount will automatically be added as another
            output addressed to the sender (a refund of unused currency).

            Format:
                {
                    receiver_address: string
                    amount: float
                    spent: bool
                }

        Unlock:
            The unlock portion of a transaction contains the sender's
            public key and an ECDSA signature created with the sender's
            private key. These are used to verify the validity of the
            transaction, as well as protect all other non-unlock fields from
            being tampered with.

            Format:
                {
                    sender_public_key: string
                    signature: string
                }
        """

    def __init__(self, **kwargs):
        """
        Create a Transaction object.
        A new Transaction object can be created by passing in a dict of
        values for a pre-existing complete transaction, or by building one from
        the ground up by not providing any parameters.
        """
        self.transaction_id = kwargs.pop('transaction_id', None)
        self.unlock = {}
        self.inputs = []
        self.input_count = 0
        self.outputs = []
        self.output_count = 0

        # If there is a transaction_id, we must have gotten
        # a complete transaction passed in, and need to get all
        # of its values.
        if self.transaction_id:
            self.unlock = kwargs.pop('unlock')
            self.inputs = kwargs.pop('inputs')
            self.input_count = kwargs.pop('input_count')
            self.outputs = kwargs.pop('outputs')
            self.output_count = kwargs.pop('output_count')

    def add_output(self, sender_address, receiver_address, amount, inputs):
        """
        Add a new output (and corresponding inputs).
        The supporting input's must be fetched from the blockchain data
        files.

        Args:
            sender_address: the sender's address (for any refunds)
            receiver_address: the receiving address of the cryptocurrency
            amount: the amount to send to the receiving address

        Returns:
            a list of output objects (dicts) that were added
        """
        total = inputs[0]
        t_inputs = inputs[1]
        # add the inputs
        self.inputs += t_inputs
        self.input_count += len(t_inputs)

        # add the output
        self.outputs.append({'receiver_address': receiver_address,
                             'amount': amount})
        self.output_count += 1

        # If there is still currency left over in the inputs,
        # refund the sender by adding an output addressed to
        # the sender's address
        if total > amount:
            self.outputs.append({'receiver_address': sender_address,
                                 'amount': total - amount})
            self.output_count += 1

        return self.outputs

    def finalize(self, sender_private_key, sender_public_key):
        """
        Sign (and finalize/complete) a transaction object.
        A complete transaction object gets signed using elliptic curve
        digital signature algorithms (ECDSA), completing the unlocking portion
        of the transaction.

        Args:
            sender_private_key: this node's ECDSA capable private key
            sender_public_key: this node's ECDSA capable public key that is
                               mathematically related to the private key
        Returns:
            The final transaction's transaction_id
        """
        if not self.transaction_id:  # Do not re-sign a finalized transaction
            signing_key = sender_private_key
            message = self.get_message()
            signature = signing_key.sign(message, hashfunc=sha256)
            # For the Key object's and Signature objects (byte strings) to
            # be JSON serialized they must be encoded with base64, and then
            # decoded into normal strings.
            self.unlock['signature'] = b64encode(signature).decode()
            self.unlock['sender_public_key'] = b64encode(
                sender_public_key.to_string()
                ).decode()
        return self.transaction_id

    def get_message(self):
        """
        Compose a byte string message over the data in this transaction.
        The message contains all sensitive data that needs to be protected by
        the unlocking portion. The unlocking portion is not included, because
        once signed the data will protect it.
        """
        payload = dict(self)
        payload['unlock'] = {}  # leave out unlock portion (if any)
        if not self.transaction_id:
            self.__set_transaction_id()  # create transaction id
        payload['transaction_id'] = self.transaction_id
        return bytes(str(payload), encoding='utf-8')

    def get_transaction_id(self):
        """ Return the transaction_id of a finalized transaction """
        return self.transaction_id

    def __set_transaction_id(self):
        """
        Set the transaction id for a completed transaction.
        The transaction is a sha256 hash over all of the transaction data,
        including the unlock portion.
        """
        payload = str(dict(self))
        self.transaction_id = sha256(
            bytes(payload, encoding='utf-8')
            ).hexdigest()

    def __iter__(self):
        """
        """

        yield 'transaction_id', self.transaction_id,
        yield 'unlock', self.unlock,
        yield 'input_count', self.input_count,
        yield 'inputs', self.inputs,
        yield 'output_count', self.output_count,
        yield 'outputs', self.outputs
