"""
Functions for throwing neat and descriptive errors
"""
# Standard Library
from typing import Optional, List, TypedDict
import os

# Third Party

# Local

class CmdError(Exception):
    """
    Raised when an invalid command is encountered
    """

    def __init__(self, message):
        super().__init__(message)
        self.message = message

class Error_handler:
    """
    Handles errors and error functions related to them
    """
    
    def __init__(self, id):
        self.id = id
        self.errors = []
        
    def add_error(self, reason: str, relavent_code: str, line_num: int):
        """
        Adds a new error to the global list of errors, formatting it to look nice and consistent
        
        Args:
          reason (str): The reason for the error (what is the error)
          relavent_code (str): The code snippet where the error occurred
          line_num (int): The line number where the error occurred, -1 if not applicable
        """

        if not line_num == -1:
            self.errors.append(f"❌ - {reason} in code '{relavent_code.strip()}' on line [{line_num}]")
        else:
            self.errors.append(f"❌ - {reason} in code '{relavent_code.strip()}'")

    def throw_errors(self):
        """
        Executes a few things:
          Logs all the errors found in the global list
          Raises an exception if any errors were found
        """
        
        if self.errors:
            for error in self.errors:
                self.log(error)
            total_errors = len(self.errors)
            self.errors.clear()

            self.log(f"🛑 - [{total_errors}] invalid commands found. See above for details.")
            raise CmdError(f"[{total_errors}] invalid commands found. See log for details.")
        
    def log(self, message: str):
        """
        Logs a message to the "logs.txt file"
        
        Args:
          message (str): The message to log
        """
        
        with open(os.path.join('app_static', 'generated_projects', str(self.id), f"log_{self.id}.txt"), "a", encoding="utf-8") as f:
            f.write(f"{message}\n")
            f.close()