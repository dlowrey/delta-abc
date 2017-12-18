import json
from src import files


def get_mining_difficulty(version):
    """
    Get the version's mining difficulty from the info file

    Returns:
        the version's difficulty as an int
    """
    with open(files.INFO_FILE) as f:
        info = json.load(f)
    return info['versions'][version]['difficulty']


def get_previous_block_id():
    """
    Get the last block's id on the block chain

    Returns:
        block id as a string
    """
    with open(files.INFO_FILE, 'r') as f:
        info = json.load(f)
    return info['previous_block_id']


def get_current_version():
    """
    Get the version that the network is
    currently running on.

    Returns:
        the current version number
    """
    with open(files.INFO_FILE, 'r') as f:
        info = json.load(f)
    return info['current_version']
