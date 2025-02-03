"""File for parsing lengths of characters in 'helvetica Neue font'"""

widths = {'a': 7, 'b': 7, 'c': 7, 'd': 7, 'e': 7, 'f': 4, 'g': 7, 'h': 7, 'i': 3, 'j': 4, 'k': 7, 'l': 3, 'm': 10, 'n': 7, 'o': 7, 'p': 7, 'q': 7, 'r': 4, 's': 6, 't': 4, 'u': 7, 'v': 6, 'w': 9, 'x': 7, 'y': 6, 'z': 6, 'A': 9, 'B': 8, 'C': 9, 'D': 8, 'E': 7, 'F': 7, 'G': 9, 'H': 9, 'I': 3, 'J': 6, 'K': 9, 'L': 7, 'M': 10, 'N': 9, 'O': 9, 'P': 8, 'Q': 9, 'R': 8, 'S': 8, 'T': 7, 'U': 9, 'V': 8, 'W': 11, 'X': 8, 'Y': 8, 'Z': 8, '0': 7, '1': 7, '2': 7, '3': 7, '4': 7, '5': 7, '6': 7, '7': 7, '8': 7, '9': 7, '!': 3, '"': 5, '#': 7, '$': 7, '%': 12, '&': 8, "'": 3, '(': 4, ')': 4, '*': 4, '+': 7, ',': 3, '-': 5, '.': 3, '/': 6, ':': 3, ';': 3, '<': 7, '=': 7, '>': 7, '?': 7, '@': 10, '[': 4, '\\': 6, ']': 3, '^': 7, '_': 6, '`': 4, '{': 4, '|': 3, '}': 4, '~': 7, ' ': 3}

def get_width(text):
    """
    Returns the width of the text in pixels
    
    ### Parameters:
    - text (str): The text to measure
    
    ### Returns:
    - int: The width of the text in pixels
    """
    return sum(widths.get(char, 0) for char in text)
