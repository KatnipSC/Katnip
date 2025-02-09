"""Tools file for knp processing"""

import functools
import inspect

def _content_aware_replace(text, selection, replacement):
        """
        Checks if the line contains a specific character.
        It will make sure that the character is not within a string.

        ### Parameters:
        - text (str): The text to check
        - selection (str): The selection to check for
        - replacement (str): The replacement for the selection

        ### Returns:
        - replacement (str): The text with the selection replaced
        """

        noCommentText = _extract_comment(text)[0]
        selectionLen = len(selection)
        occurences = [] # Track occurences of selection

        depth = 1
        for idx, char in enumerate(noCommentText):
            if char == '"' and not noCommentText[idx-1] == "\\":
                depth *= -1
            if char == selection[0] and depth == 1:
                if noCommentText[idx:idx+len(selection)] == selection:
                    occurences.append(idx)
        
        # Replace the selection
        occurences.reverse() # Reverse the list so that the indexes don't change
        for occurence in occurences:
            text = text[:occurence] + replacement + text[occurence+selectionLen:]

        return text
    
def _content_aware_split(text, selection):
    """
    Splits the text by the selection, but only if the selection is not within a string.

    ### Parameters:
    - text (str): The text to split
    - selection (str): The selection to split by

    ### Returns:
    - split (list): The split text
    """

    selectionLen = len(selection)
    occurences = []
    
    depth = 1
    prev_end = 0
    for idx, char in enumerate(text):
        if char == '"' and not text[idx-1] == "\\":
            depth *= -1
        if char == selection[0] and depth == 1:
            if text[idx:idx+len(selection)] == selection:
                occurences.append((prev_end, idx))
                prev_end = idx + selectionLen
    
    if occurences:
        return [text[i:j] for i, j in occurences]
    else:
        return [text]
                
def _content_aware_check(text, char):
    """
    Checks if the text contains a specific character.
    It will make sure that the character is not within a string.

    ### Parameters:
    - text (str): The text to check for the character
    - char (str): The character to look for

    ### Returns:
    - bool: True if the character is found in the text, False otherwise
    """

    text = _extract_comment(text)[0]

    depth = 1
    for idx, letter in enumerate(text):
        if letter == '"' and not text[idx-1] == "\\":
            depth *= -1
        if letter == char and depth == 1:
            return True
    return False
    
def _extract(string: str):
    """
    Extracts name and arguments from a string (a line containing a function).

    ### Parameters:
    - string (str): The string of the line containing the relavent function

    ### Returns:
    - pieces (dict): A dictionary containing the name and arguments of the function
        - ["name"] (str): The name of the function
        - ["args"] (list): A list of arguments for the function
        - ["after"] (str): The string after the function
    """

    pieces = {}
    pieces["name"] = string.split("(")[0]

    args_string = string[string.find("(") + 1 : string.rfind(")")]
    args = []
    current_arg: list[str] = []
    depth = 0  # To track nested parentheses

    for char in args_string:
        if char == "," and depth == 0:
            # If not within parentheses, this is a separator
            args.append("".join(current_arg).strip())
            current_arg = []
        else:
            if char == "(":
                depth += 1
            elif char == ")":
                depth -= 1
            current_arg.append(char)

    # Add the last argument if it exists
    if current_arg:
        args.append("".join(current_arg).strip())

    # Filter out empty arguments
    pieces["args"] = [arg for arg in args if arg]
    
    # Add any leftover text
    if ")" in string:
        pieces["after"] = string[string.rfind(")") + 1 :]
    else:
        pieces["after"] = ""
    
    return pieces

def _extract_comment(text: str):
    """
    Seperates the comment from the line of code and returns a tuple containing both.

    ### Parameters:
    - text (str): The line of code containing a comment

    ### Returns:
    - line (tuple): The two split pieces of the line:
        - code (str): The line of code
        - comment (str): The comment
    """

    comment_start = -1
    depth = 1
    for idx, letter in enumerate(text):
        if letter == '"':
            depth *= -1
        if letter == '#' and depth == 1:
            comment_start = idx
            break
    
    if comment_start == -1:
        return text, None
    else:
        return text[:comment_start], text[comment_start+1:].strip()

def _is_num(value: str):
    """
    Checks if a given value is a valid number. (only allows characters in "-.0123456789")

    ### Parameters:
    - value (str): The value to check

    ### Returns:
    - bool: True if the value is a valid number, False otherwise
    """

    if len(value) == 0:
        return False
    for character in value:
        if not character in "-.0123456789xe^": # x and e and ^ are for scientific notation
            return False
    return True

def enforce_types(func):
    """
    A decorator that enforces type hints for function arguments and return values.
    
    ### Parameters:
    - func (callable): The function whose type hints should be enforced.
    
    ### Returns:
    - callable: A wrapped function that checks argument and return types at runtime.
    
    ### Raises:
    - TypeError: If an argument or return value does not match its type hint.
    """
    
    signature = inspect.signature(func)
    hints = func.__annotations__
    
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        bound_args = signature.bind(*args, **kwargs)
        bound_args.apply_defaults()
        
        # Check argument types
        for param, arg in bound_args.arguments.items():
            if param in hints and not isinstance(arg, hints[param]):
                raise TypeError(f"Argument '{param}' must be of type {hints[param].__name__}, got {type(arg).__name__}")
        
        result = func(*args, **kwargs)
        
        # Check return type
        if 'return' in hints and not isinstance(result, hints['return']):
            raise TypeError(f"Return value must be of type {hints['return'].__name__}, got {type(result).__name__}")
        
        return result
    
    return wrapper