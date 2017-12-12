"""
Functions that allow acess to persisted data such as
the block chain files and other info stored in the /data/
directory
"""
import json


def get_inputs(amount):
    """
    Get transaction inputs to cover a specified amount.
    Transaction inputs are retrieved from a file of JSON objects
    that represent unspent transaction outputs that were addressed
    to this node's address.

    Args:
        amount: the minimum amount the found inputs should cover

    Returns:
        A tuple (total, inputs) where:
            total: the amount this input will cover
            inputs: an array containging the needed inputs
    """
    total = 0
    inputs = []
    available = get_balance()
    if available >= amount:
        try:
            # Read in all unspent transaction outputs and
            # add as many needed to cover the specified amount
            total = 0
            inputs = []
            with open('data/unspent_outputs.json', 'r+') as f:
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
    with open('data/blockchain/block{}.json'.format(block_id), 'r+') as f:
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


def get_mining_difficulty(version):
    """
    Get the version's mining difficulty from the info file
    
    Returns:
        the version's difficulty as an int
    """
    with open('data/node_info.json') as f:
        info = json.load(f)
    return info['versions'][version]['difficulty']


def get_previous_block_id():
    """
    Get the last block's id on the block chain

    Returns:
        block id as a string
    """
    with open('data/node_info.json', 'r') as f:
        info = json.load(f)
    return info['previous_block_id']


def set_previous_block_id(new_id):
    """
    Set the previous_block_id in the info file.
    This is the ID of the latest block on the blockchain.

    Returns:
        the info dict
    """
    with open('data/node_info.json', 'r+') as f:
        info = json.load(f)
        info['previous_block_id'] = new_id
        f.truncate(0)
        f.seek(0)
        json.dump(info, f)
    return info


def get_balance():
    """
    Get this node's balance from it's info file.

    Returns:
        A float representing how much cryptocurrency this
        node has addressed to it in the blockchain.
    """
    with open('data/node_info.json', 'r') as f:
        info = json.load(f)
    return info['wallet']['balance']


def set_balance(new_balance):
    """
    Set this node's balance in it's info file.

    Returns:
        the info (dict) corresponding to this node
    """
    with open('data/node_info.json', 'r+') as f:
        info = json.load(f)
        info['wallet']['balance'] = new_balance
        f.truncate(0)
        f.seek(0)
        json.dump(info, f)
    return info


def get_current_version():
    """
    Get the version that the network is
    currently running on.
    
    Returns:
        the current version number
    """
    with open('data/node_info.json', 'r') as f:
        info = json.loads(f.read())
    return info['current_version']
