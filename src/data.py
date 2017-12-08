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
    # check if we can cover the amount
    #available = usrconfig.get_balance()
    available = 69
    if available < amount:
        return -1, None
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
                f.write("{}\n".format(t_input))
        return total, inputs
    except FileNotFoundError as e:
        print(e)
        return -1, None
            

