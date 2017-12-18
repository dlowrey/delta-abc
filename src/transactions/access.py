"""
File access for Transaction objects
"""
import json
from hashlib import sha256
from base64 import b64decode
from ecdsa import VerifyingKey, NIST256p
from ecdsa import BadSignatureError
from src import files


def get_inputs(amount):
    """
    Get transaction inputs to cover a specified amount.
    Transaction inputs are retrieved from a file of JSON objects
    that represent unspent transaction outputs that were addressed
    to this node's address.

    Args:
        amount: the minimum amount the found inputs should cover

    Returns:
        inputs: an array containging the needed inputs
    """
    total = 0
    inputs = []
    available = get_balance()
    if available < amount:
        raise ValueError('Insufficient Funds: {} < {}'.format(
            available, total))
    try:
        # Read in all unspent transaction outputs and
        # add as many needed to cover the specified amount
        total = 0
        inputs = []
        with open(files.UNSPENT_OUTPUTS, 'r+') as f:
            all_inputs = [json.loads(i) for i in f.readlines()]
            for t_input in all_inputs:
                total += t_input['amount']
                inputs.append(t_input)
                if total >= amount:
                    break
            # Erase the contents of the file and re-write the
            # unspent transaction outputs that were not used
            f.truncate(0)
            f.seek(0)
            all_inputs = [i for i in all_inputs if i not in inputs]
            for t_input in all_inputs:
                f.write('{}\n'.format(t_input))
    except FileNotFoundError as err:
        print(err)

    set_balance(available-total)  # update this node's balance
    return total, inputs


def find_output(transaction_id, block_id, output_index):
    """
    Find a refrenced transaction output that exists in the blockchain.
    Each node must verify that the output exists in it's own copy
    of the blockchain.

    Args:
        trasnsaction_id: the transaction id of the refrenced transaction output
        block_id: the block_id that the transaction is in
        output_index: the index of the refrenced output in the transaction

    Returns:
        The transaction output (dict) if any was found, otherwise None

    """
    # Read the specified block's file and check for a transaction
    # output that matches the parameters
    with open(files.BLOCKCHAIN_DIR + '{}.json'.format(block_id), 'r+') as f:
        block = json.load(f)
        try:
            block_data = block['data']
            target_tnx = block_data[transaction_id]
            outputs = target_tnx['outputs']
            target_output = outputs[output_index]
            # Update the block's file signifying that the transaction
            # is now spent
            target_output['spent'] = True
            f.truncate(0)
            f.seek(0)
            json.dump(block, f)
        except (KeyError, IndexError) as err:
            target_output = None
    return target_output


def verify(tnx):
    """
    Verify the authenticity of a transaction object.
    Verifying checks the unlocking signature against the transaction,
    which will only be authentic if nothing was tampered with. After this,
    each input is checked against the blockchain for existence and right
    of use by the sender.

    Returns:
        A tuple (boolean, dict) where the first is whether or not the
        transaction is valid, and the second is None unless the transaction
        was invalid by unrightful use of input, in which case it is the
        offending input.
    """
    authentic = True
    offender = None

    sender_address = tnx.unlock['sender_public_key']  # sender's address
    # The sender's public key was sent over as a string, we must
    # convert it back into a Key object. First it is converted from its
    # base64 encoding back into a byte string, and then from a byte string
    # into a Key object
    sender_byte_address = b64decode(sender_address.encode())
    verify_key = VerifyingKey.from_string(sender_byte_address,
                                          curve=NIST256p)
    # The same must be done for the signature, which was also
    # sent over as a string. COnvert from base64 encoding to byte string,
    # and from byte string to Signature object
    signature = b64decode(tnx.unlock['signature'].encode())
    # Re-build the message from scratch to expose any
    # invalid data in the transaction
    message = tnx.get_message()

    # The transaction's message (all protected data) is verified
    # using the sender's public key. Because the sender signed with
    # a private key and this public key is mathematically related to it,
    # we can use it to authenticate the transaction signature.
    try:
        verify_key.verify(signature, message, hashfunc=sha256)
    except BadSignatureError:
        # An invalid signature can mean that the transaction was
        # either tampered with, or the wrong public key was used.
        authentic = False

    if authentic:
        # Check that the sender has the rights to use all of the
        # inputs he uses in the transaction.
        for t_input in tnx.inputs:
            # find the refrenced output used as an input
            refrenced_output = find_output(
                t_input['transaction_id'],
                t_input['block_id'],
                t_input['output_index'])

            # make sure the refrenced output exists
            if not refrenced_output:
                authentic = False
                offender = t_input
                break
            # make sure refrenced output is addressed transaction's sender
            elif refrenced_output['receiver_address'] != sender_address:
                authentic = False
                offender = t_input
                break
            # make sure transaction output hasnt already been spent
            elif refrenced_output['spent_transaction_id']:
                authentic = False
                offender = t_input
                break

    return authentic, offender


def get_balance():
    """
    Get this node's balance from it's info file.

    Returns:
        A float representing how much cryptocurrency this
        node has addressed to it in the blockchain.
    """
    with open(files.INFO_FILE, 'r') as f:
        info = json.load(f)
    return info['wallet']['balance']


def set_balance(new_balance):
    """
    Set this node's balance in it's info file.

    Returns:
        the info (dict) corresponding to this node
    """
    with open(files.INFO_FILE, 'r+') as f:
        info = json.load(f)
        info['wallet']['balance'] = new_balance
        f.truncate(0)
        f.seek(0)
        json.dump(info, f)
    return info
