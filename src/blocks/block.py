"""
Class for handling the creation of Block objects from
scratch (by adding data, i.e. transactions), or from a network
received json block (passed in as a dict). Handles the mining and
verification of blocks.
"""
from hashlib import sha256
from datetime import datetime
from time import time
from src.persistence import access


class Block(object):

    def __init__(self, **kwargs):
        """
        Create a Block object.
        A new Block object can be created by passing in a dict of values
        from a pre-existing block, or by building one from the ground
        up by not providing any parameters.

        Format (returned when casting Block to a dict())
            {
                block_id: string,
                previous_block_id: string,
                timestamp: string,
                data: dict,
                version: string,
                mining_proof: int
            }

            block_id:
                a sha256 hash of the non-changing block data
                such as the previous_block_id, data (in ordered format),
                and version number.

            previous_block_id:
                the block_id of the block on the blockchain preceding this
                block

            data:
                a dict of transactions in the form {transaction_id: {...},}

            version:
                the version of the system when this block was mined
                contains information like difficulty

            mining_proof:
                a random integer that will result in the target difficulty for
                the version being met

        """
        self.block_id = kwargs.pop('block_id', None)
        self.previous_block_id = kwargs.pop(
                'previous_block_id',
                 access.get_previous_block_id())
        self.timestamp = kwargs.pop('timestamp', None)
        self.data = kwargs.pop('data', dict())
        self.version = kwargs.pop('version', access.get_current_version())
        self.mining_proof = kwargs.pop('mining_proof', None)
        self.difficulty = access.get_mining_difficulty(self.version)
        # Ordered data is assigned right before verifying/mining a block
        self.ordered_data = None

    def mine(self):
        """
        Mine a complete block.
        Verify the contents of this block in preparation for the
        blockchain by proof-of-work algorithm. The proof of work is
        sha256 hashing the block data with a random number (nonce) until
        it has enough pre-fixed zeros to satisfy the difficulty.

        Returns:
            Python dict representation of the newly mined block
        """
        if not self.mining_proof:  # do not mine an already mined block
            # Python dicts are unordered, and to be consistent with
            # our hash values for this block we need order, so we sort
            # the dict data by key, and get a list of tuples
            self.__set_order_data()
            nonce = 0
            target_hash = ''
            goal = ''.zfill(self.difficulty)

            # Continuously hash and change nonce until the difficulty goal
            # is satisified (Proof of work)
            while not target_hash.startswith(goal):
                nonce += 1
                target_hash = self.__compose_hash(nonce)

            # Now complete the block by filling out the remaining fields
            self.mining_proof = nonce
            self.timestamp = datetime.fromtimestamp(time()).strftime(
                    '%Y-%m-%d %H:%M:%S')
            self.__set_block_id()
        return dict(self)

    def verify(self):
        """
        Verify the authenticity of a new block.
        Verify the block by checking to see if the proof of work has
        been accomplished. Check the mining_proof against a target
        difficulty

        Returns:
            Boolean (True if authentic)
        """
        # Python dicts are unordered, and to be consistent with
        # our hash values for this block we need order, so we sort
        # the dict data by key, and get a list of tuples
        self.__set_order_data()
        goal = ''.zfill(self.difficulty)
        target_hash = self.__compose_hash(self.mining_proof)
        # Check to see if the block's nonce satisfies the target difficulty
        return target_hash.startswith(goal)

    def add_transaction(self, tnx):
        """
        Add a transaction object to this block.

        Returns:
            the newly added transaction object (dict)
        """
        transaction_id = tnx['transaction_id']
        self.data[transaction_id] = tnx
        return {transaction_id: self.data[transaction_id]}

    def __compose_hash(self, nonce):
        """
        Create a new hash based on the block data and a random number.
        This hash is checked against a target difficulty to see if the
        block has been successfully mined.

        Returns:
            The newly calculated block hash
        """

        payload = self.__get_mining_data()
        payload += str(nonce)  # add random number in
        block_hash = sha256(bytes(payload, encoding='utf-8')).hexdigest()
        return block_hash

    def __set_block_id(self):
        """
        Set the block id for a completed block.
        """
        payload = self.__get_mining_data()
        self.block_id = sha256(bytes(payload, encoding='utf-8')).hexdigest()

    def __set_order_data(self):
        """
        Order the block data to prepare for hashing.
        Block data (transactions) stored in python dicts do not maintain
        any order, and thus will produce different hash values at random.

        Returns:
            a list of tuples representing the ordered data
        """
        if not self.ordered_data:
            data = {}
            for t_id, t in self.data.items():
                # sort nested transaction dicts
                t['unlock'] = sorted(t['unlock'].items(), key=lambda k: k[0])
                # sort the transaction object
                t = sorted(t.items(), key=lambda k: k[0])
                # put in new dict of ordered transactions
                data[t_id] = t
            # sort the ordred transactions
            self.ordered_data = sorted(data.items(), key=lambda k: k[0])
        return self.ordered_data

    def __get_mining_data(self):
        """
        Get a string representation of the block data needed for the
        mining process.
        Only include data that is present before mining.

        Returns:
            a string of the data to be included in mining process
        """
        return "{0}{1}{2}".format(
                self.previous_block_id,
                self.ordered_data,  # data must be in consistent order
                self.version
                )

    def __iter__(self):
        """
        Override the __iter__ function so that
        we can call dict(Block) and get a dict object
        back that represents the Block object passed

        Yields:
            Each field of a Block object
        """
        yield 'block_id', self.block_id
        yield 'previous_block_id', self.previous_block_id
        yield 'timestamp', self.timestamp
        yield 'data', self.data
        yield 'version', self.version
        yield 'mining_proof', self.mining_proof

