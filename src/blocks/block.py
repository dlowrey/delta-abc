"""
Class for handling the creation of Block objects from
scratch (by adding data, i.e. transactions), or from a network
received json block (passed in as a dict). Handles the mining and
verification of blocks.
"""
from hashlib import sha256
from datetime import datetime
from collections import OrderedDict
from time import time
from src import data_access


class Block(object):

    def __init__(self, **kwargs):
        """
        Create a Block object.
        A new Block object can be created by passing in a dict of values
        from a pre-existing block, or by building one from the ground
        up by not providing any parameters.
        """
        self.block_id = kwargs.pop('block_id', None)
        self.previous_block_id = kwargs.pop('previous_block_id', None)
        self.timestamp = kwargs.pop('timestamp', None)
        self.data = kwargs.pop('data', dict())
        self.ordered_data = None
        self.version = kwargs.pop('version', 0)
        self.mining_proof = kwargs.pop('mining_proof', None)
        self.difficulty = data_access.get_mining_difficulty(self.version)
        if not self.previous_block_id:
            self.previous_block_id = data_access.get_previous_block_id()

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
            nonce = 0
            target_hash = ''
            goal = ''.zfill(self.difficulty)
            # Continuously hash and change nonce until the difficulty goal
            # is satisified (Proof of work)
            while not target_hash.startswith(goal):
                target_hash = self.__compose_hash(nonce)
                nonce += 1
            # Fill out the remining values to complete the block
            self.__set_block_id()
            self.mining_proof = nonce
            self.timestamp = datetime.fromtimestamp(time()).strftime(
                    '%Y-%m-%d %H:%M:%S')
            # Newly mined block added to the blockchain, update this node's
            # latest block id
            data_access.set_previous_block_id(self.block_id)
        return dict(self)

    def verify(self):
        """
        Verify the authenticity of a new block.
        Verify the block by checking to see if the proof of work has
        been accomplished. Check the mining proof against a target
        difficulty

        Returns:
            Boolean (True if authentic)
        """
        goal = ''.zfill(self.difficulty)
        target_hash = sha256(self.__compose_hash(self.mining_proof))
        # Check to see if the block's nonce satisfies the target difficulty
        authentic = target_hash.startswith(goal)
        if authentic:
            data_access.set_previous_block_id(self.block_id)

        return authentic

    def add_transaction(self, tnx):
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
        payload += str(nonce)
        block_hash = sha256(bytes(payload, encoding='utf-8')).hexdigest()
        return block_hash

    def __set_block_id(self):
        """
        Set the block id for a completed block.
        """
        payload = self.__get_mining_data()
        self.block_id = sha256(bytes(payload, encoding='utf-8')).hexdigest()
    
    def __order_data(self):
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
                t = sorted(t.items(), key=lambda k: k[0])
                data[t_id] = t
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
        # Python dicts are unordered, and to be consistent with
        # our hash values for this block we need order, so we sort
        # the dict data by key, and get a list of tuples
        ordered_data = self.__order_data()
        return "{0}{1}{2}".format(
                self.previous_block_id,
                ordered_data,  
                self.version
                )

    def __iter__(self):
        """
        Override the __iter__ function so that
        we can call dict(Block) and get a dict object
        back that represents the Block object passed
        """
        yield 'block_id', self.block_id
        yield 'previous_block_id', self.previous_block_id
        yield 'timestamp', self.timestamp
        yield 'data', self.data
        yield 'version', self.version
        yield 'mining_proof', self.mining_proof


        
        
