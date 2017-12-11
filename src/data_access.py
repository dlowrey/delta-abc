import json


def get_inputs(amount):
    """
    Get transaction inputs up to a specified amount

    Args:
        amount: the minimum amount the found inputs should cover
                if possible
    Returns:
        t_amount: the amount this input will cover
        t_input: a dictionary with the data for a new input object
    """
    total = 0
    inputs = []
    # check if we can cover the amount
    available = get_balance()
    if available >= amount:
        try:
            total = 0
            inputs = []
            with open('data/unspent_outputs.json', 'r+') as f:
                all_inputs = [json.loads(i) for i in f.readlines()]
                # gather neede inputs
                for t_input in all_inputs:
                    total += t_input['amount']
                    inputs.append(t_input)
                    if total >= amount:
                        break
                # clear file
                f.truncate(0)
                # write-back unused inputs
                all_inputs = [i for i in all_inputs if i not in inputs]
                for t_input in all_inputs:
                    f.write('{}\n'.format(t_input))
        except FileNotFoundError as err:
            print(err)

        # update balance
        set_balance(available-total)
    return total, inputs


def find_output(transaction_id, block_id, output_index):
    """
    Find a refrenced transaction output in the blockchain.

    Args:
        trasnsaction_id: the transaction id of the refrenced transaction output
        block_id: the block_id that the transaction is in
        output_index: the index of the refrenced output in the transaction

    Returns:
        The transaction output object if any was found, otherwise None

    """
    with open('data/blockchain/block{}.json'.format(block_id), 'r+') as f:
        block = json.loads(f.read())
        try:
            block_data = block['data']
            target_tnx = block_data[transaction_id]
            outputs = target_tnx['outputs']
            target_output = outputs[output_index]
            # mark as spent
            target_output['spent'] = True
            # update block file
            f.truncate(0)
            f.write(json.dumps(block))
        except (KeyError, IndexError) as err:
            target_output = None
    return target_output


def get_balance():
    """
    Get this node's address from it's info file
    """
    with open('data/node_info.json', 'r') as f:
        info = json.loads(f.read())
    return info['wallet']['balance']


def set_balance(new_balance):
    with open('data/node_info.json', 'r+') as f:
        info = json.loads(f.read())
        info['wallet']['balance'] = new_balance
    return info

