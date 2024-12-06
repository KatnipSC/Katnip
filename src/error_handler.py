"""
Functions for throwing neat and descriptive errors
"""

errors = []
def add_error(reason: str, relavent_code: str, line_num: int):
    """
    Adds a new error to the global list of errors, formatting it to look nice and consistent
    
    Parameters:
    - reason (str): The reason for the error (what is the error)
    - relavent_code (str): The code snippet where the error occurred
    - line_num (int): The line number where the error occurred, -1 if not applicable
    """

    if not line_num == -1:
        errors.append(f"❌ - {reason} in code '{relavent_code}' on line [{line_num}]\n")
    else:
        errors.append(f"❌ - {reason} in code '{relavent_code}'")

def throw_errors():
    """
    Executes a few things:
    - Prints all the errors found in the global list
    - Raises an exception if any errors were found
    """
    
    if errors:
        for error in errors:
            print(error)
        total_errors = len(errors)
        errors.clear()

        raise Exception(f"[{total_errors}] invalid commands found. See above for details.")