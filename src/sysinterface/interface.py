"""
A module that allows basic blockchain functionality
through simple functions that carry out more complicated
techniques.

To be uesd by a user-facing interface or command line client
"""
import os
from ecdsa import SigningKey, VerifyingKey, NIST256p
from src.transactions.transaction import Transaction
from src.blocks.block import Block
from src.data-access import access, files


def send_transaction(receiver_address, amount):
    """
    Send a transaction.
    """
    sender_address = access.get_address()
    private_key = access.get_private_key()
    public_key = access.get_public_key()

    new_tnx = Transaction()
    try:
        new_tnx.add_output(sender_address, receiver_address, amount)
        new_tnx.finalize(private_key, public_key)
        access.save_transaction(new_tnx)
        network.send_transaction(new_tnx)
        return 'Sent:\namount: {}\nto: {}\nfrom: {}'.format(
                amount, receiver_address, sender_address)
    except ValueError as e:
        access.logit(e)
        return e

def start_mining():
    """
    Begin mining a new block with received or created 
    transactions
    """

    new_block = Block()
    # get transactions waiting to be put in a block
    waiting_transactions = access.get_waiting_transactoins()
    for tnx in waiting_transactions:
        new_block.add_transaction(tnx)

    block_dict = block.mine()
    block_id = access.save_block(block)
    # save any transactions addressed to this node
    my_tnx_count, my_total = access.save_my_outputs(block)

    response = 'Saved block {}'.format(block_id)
    if my_tnx_count:
        # update the balance for this node
        old_balance = access.get_balance()
        new_balance = old_balance + my_total
        access.set_balance(new_balance)
        response += ' Your new balance is {}'.format(new_balance)

    return response

def save_transaction(tnx_dict):
    tnx = Tnx(**tnx_dict)
    success = access.save_transaction(tnx)
    if success:
        return 'Transaction succesfully saved.'
    else:
        return 'Invalid transaction was not saved.'


def reset():
    a = input("Are you sure you want to reset the system?\n"
              "All data and keys will be lost. (y/n): ")
    if a == "y":
        files.reset_all()
        return "System successfully reset"
