"""
Functions for throwing neat and descriptive errors
"""
import os

class CmdError(Exception):
    """
    Raised when an invalid command is encountered
    """

    def __init__(self, message):
        super().__init__(message)
        self.message = message

errors = []
def add_error(reason: str, relavent_code: str, line_num: int):
    """
    Adds a new error to the global list of errors, formatting it to look nice and consistent
    
    ### Parameters:
    - reason (str): The reason for the error (what is the error)
    - relavent_code (str): The code snippet where the error occurred
    - line_num (int): The line number where the error occurred, -1 if not applicable
    """

    if not line_num == -1:
        errors.append(f"❌ - {reason} in code '{relavent_code}' on line [{line_num}]")
    else:
        errors.append(f"❌ - {reason} in code '{relavent_code}'")

def throw_errors(id):
    """
    Executes a few things:
    - Logs all the errors found in the global list
    - Raises an exception if any errors were found

    ### Parameters:
    - id (str): The id of the file to log into
    """
    
    if errors:
        for error in errors:
            log(id, error)
        total_errors = len(errors)
        errors.clear()

        log(id, f"🛑 - [{total_errors}] invalid commands found. See above for details.")
        raise CmdError(f"[{total_errors}] invalid commands found. See log for details.")
    
def log(id, message):
    """
    Logs a message to the "logs.txt file"
    
    ### Parameters:
    - id (str): The id of the file to log into
    - message (str): The message to log
    """
    
    with open(os.path.join('app_static', 'generated_projects', str(id), f"log_{id}.txt"), "a", encoding="utf-8") as f:
        f.write(f"{message}\n")
        f.close()