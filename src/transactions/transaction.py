from ecdsa import VerifyingKey, NIST256p
from ecdsa import BadSignatureError
from hashlib import sha256
from src.transactions import data

class Transaction(object):
    """ Represents a single Transaction object
        
        A transaction object contains inputs and outputs
        as well as information about itself such as the transaction's id, and
        the block id that it belongs to (if any)

        Format:
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
                address and the amount sent to that address.
                Outputs are protected from any modification by the unlocking
                section of inputs.

                The total amount of the outputs in a transaction must be equal
                to the total amount in the inputs. I.e., all inputs must be
                used up. This means that when sending a transaction, any
                unused input amount will automatically be added as another
                output addressed to the sender (a refund of unused currency).

                Format:
                    {
                        receiver_address: string
                        amount: float
                        spent_transaction_id: string
                    }
                
            Unlock:
                The unlock portion of a transaction contains the sender's
                public key and an ECDSA signature created with the sender's
                private key. These are used to verify the validity of the
                transaction.

                Format:
                    {
                        sender_public_key: string
                        signature: string
                    }
        """
    
    def __init__(self, **kwargs):
        self.transaction_id = kwargs.pop('transaction_id', None)

        self.unlock = {}
        self.inputs = []
        self.input_count = 0
        self.outputs = []
        self.output_count = 0

        if self.transaction_id:
            # Existing transaction object
            self.unlock = kwargs.pop('unlock')
            self.inputs = kwargs.pop('inputs')
            self.input_count = kwargs.pop('input_count')
            self.outputs = kwargs.pop('outpus')
            self.output_count = kwargs.pop('output_count')

    def add_output(self, sender_address, receiver_address, amount):
        """
        Create a new transaction output for `amount`
        addressed to `receiver_address`

        Args:
            sender_address: the sender's address for any refunds
            receiver_address: a recipient address that will be 
                              included in the output object
            amount: the amount of the output object

        Returns:
            a list of output objects for this transaction
        Raises: 
            A ValueError if insufficient funds were found
        """
        total, inputs = data.get_inputs(amount)

        # if not enough to make output
        if total < 0:
            raise ValueError("Insufficient Funds")
        else:
            self.inputs += inputs
            self.input_count += len(inputs)

            # add the output
            self.outputs.append({'receiver_address': receiver_address,
                                 'amount': amount})
            self.output_count += 1
            
            if total > amount:
                # refund the sender any overages
                self.outputs.append({'receiver_address': sender_address,
                                    'amount': total - amount})
                self.output_count +=1
                
            return self.outputs
                
            
    def finalize(self, sender_private_key, sender_public_key):
        """
        Sign a transaction object using ECDSA 
        The transaction object is presumed fully complete if it is 
        being signed, no more changes should be made.

        Args:
            sender_private_key: an ECDSA capable private key of this user
            sender_public_key: an ECDSA capable public key related to the
                               sender_private_key
        Returns:
            The transaction's transaction_id
        """
        # do not sign a received transaction
        if not self.transaction_id:
            signing_key = sender_private_key
            message = self.__compose_message()
            signature = signing_key.sign(message, hashfunc=sha256)
            # store in unlocking portion of transaction
            self.unlock['signature'] = signature
            self.unlock['sender_public_key'] = sender_public_key
        return self.transaction_id
    
    def verify(self):
        """
        Verify the validity of a received transaction.
        Check the signature against the transaction and the provided
        unlocking portion, and check each of the transaction's inputs
        against the block chain to assure they are being used by the 
        rightful owner and have not been spent previously.

        Returns:
            boolean, dict (authentic, offender) in the combiniations:
                True, None if the transaction was valid
                False, None if the signature was invalid
                False, {...} if a transaction input was invalid
            where dict is the offending input if any
        """
        authentic = True
        offender = None

        sender_public_key = self.unlock['sender_public_key']
        signature = self.unlock['signature']
        message = self.__compose_message()

        # create verifying key from sender's public key
        verifiy_key = VerifyingKey.from_string(sender_public_key,
                                               curve=NIST256p)
        try:
            verify_key.verify(signature, message, hashfunc=sha256)
        except BadSignatureError:
            # invalid, set authentic and offender and break
            authentic = False

        # if the signature was valid, check that all inputs actually
        # belong to the sender
        if authentic:
            for t_input in self.inputs:
                # find the refrenced output used as an input
                refrenced_output = data.find_output(t_input['transaction_id'],
                                             t_input['block_id'],
                                             t_input['output_index'])
                # make sure refrenced output is addressed transaction's sender
                if refrenced_output['address'] != sender_public_key:
                    authentic = False
                    offender = t_input
                    break
                # make sure transaction output hasnt already been spent
                elif refrenced_output['spent_transaction_id']:
                    authentic = False
                    offender = t_input
                    break

        return authentic, offender

    def __compose_message(self):
        """
        Compose a byte string message to sign or verify a transaction.
        The message is all of the transaciton data, including the 
        finalized transaction's ID.
        """
        payload = dict(self)
        if not self.transaction_id:
            self.__set_transaction_id()
        payload['transaction_id'] = self.transaction_id
        return bytes(str(payload), encoding='utf-8')

    def get_transaction_id(self):
        """ Return the transaction_id of a finalized transaction """
        return self.transaction_id

    def __set_transaction_id(self):
        """ Set the transaction id before finalizing the transaction """
        payload = str(dict(self))
        self.transaction_id  = sha256(bytes(payload, encoding='utf-8')).hexdigest()
        
    
        
    def __iter__(self):
        """
        Override the __iter__ function so that
        we can call dict(Transaction) and get a dict object
        back that represents the Transaction object passed.
        """
        yield 'unlock', self.unlock
        yield 'input_count', self.input_count
        yield 'inputs', self.inputs
        yield 'output_count', self.output_count
        yield 'outputs', self.outputs
