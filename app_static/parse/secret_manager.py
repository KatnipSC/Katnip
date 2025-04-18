"""
File containing the get_key function to retrieve secrets from secrets.txt
"""
import os

def get_key(key):
    """
    Retrieves a secret key from a local file.

    Args:
      key: The name of the key to retrieve
    
    Returns:
      str: The value of the specified key, or None if not found in the file.
    """
    with open(os.path.join('app_static', 'references', 'secrets.txt'),'r') as file:
        for line in file:
            if line.startswith(key):
                return line.split('=',1)[1].replace("\n", "")
    return None