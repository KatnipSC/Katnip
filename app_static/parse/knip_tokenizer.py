"""
This module is responsible for tokenizing the input code for the katnip programming language.
Responsibilities include:
- Tokenizing the input code (smart tokenization, where it can infer token type and usage based on surrounding tokens)
- Identifying token types
- Basic deconstruction of the code
"""

# Standard
import json

# Third Party
from typing import Union

# Local
import error_handler
import knip_tools as tools
from custom_types import Token

class Tokenizer:
    """🧩 - Tokenizes KNP file contents"""
    
    def __init__(self, project_id: int, settings: dict):
        """
        Initializes the tokenizer.
        
        Args:
          project_id (int): ID of the project being tokenized
          settings (dict): Settings dictionary for the compiler
        """
        
        self.project_id = project_id
        self.tokens: list[Token] = []
        self.line = 0
        self.code = ""
        
        self.error_handler = error_handler.Error_handler(project_id)
        self.settings = settings
        
    def _is_reporter(self, arg: str) -> bool:
        """
        Checks if the argument is a reporter.
        
        Args:
          arg (str): The argument to check
        
        Returns:
          bool: True if the argument is a reporter, False otherwise
        """
        return "(" in arg and ")" in arg and not arg.startswith("(")
    
    def _tokenize_args(self, args: list):
        """
        Tokenizes the arguments of a function into tokens and adds them to self.tokens.
        """
        self.error_handler.log(f"🔨⛓️‍💥 - Tokenizing arguments: {args}")

        # Operator precedence tiers (from highest to lowest, reversed below for easier parsing)
        operator_tiers = [
            {"^": "op.pow"}, 
            {"*": "op.multiply", "/": "op.divide", "%": "op.mod"},
            {"+": "op.add", "-": "op.subtract"},
            {"<": "op.lt", ">": "op.gt", "<=": "op.lte", ">=": "op.gte"}, 
            {"==": "op.equals", "!=": "op.nequals"},
            {"&&": "op.and"},
            {"||": "op.or"}
        ][::-1]

        operator_lookup = {op: fn for tier in operator_tiers for op, fn in tier.items()}

        def _add_token(name="argument", type_=None, value=""):
            self.tokens.append({"name": name, "type": type_, "value": value})

        for arg in args:
            if arg in operator_lookup:
                _add_token(name="function", value=operator_lookup[arg])
                continue

            # Try to simplify expression with operators
            for tier in operator_tiers:
                ops_found = [(i, op) for op in tier for i in tools._get_occurences(arg, op)]
                if ops_found:
                    ops_found.sort(reverse=True)  # Right-to-left for correct order
                    sub_args = []
                    for index, op in ops_found:
                        sub_args.append(arg[index+len(op):])
                        sub_args.append(op)
                        arg = arg[:index]
                    sub_args.append(arg)
                    self._tokenize_args(list(reversed(sub_args)))
                    break
            else:
                # No operator simplification: determine argument type
                if self._is_reporter(arg):
                    pieces = tools._extract(arg)
                    _add_token(name="reporter", value=pieces["name"])
                    self.tokens.append({"name": "lparen", "type": None, "value": "("})
                    self._tokenize_args(pieces["args"])
                    self.tokens.append({"name": "rparen", "type": None, "value": ")"})
                elif arg.startswith("(") and arg.endswith(")"):
                    self._tokenize_args([arg[1:-1]])
                elif arg.startswith("$"):
                    _add_token(type_="variable", value=arg[1:])
                elif arg.startswith("@l:"):
                    _add_token(type_="list", value=arg[3:])
                elif arg.startswith("@d:"):
                    _add_token(type_="dictionary", value=arg[3:])
                elif arg.startswith("a."):
                    _add_token(type_="functionArgument", value=arg[2:])
                elif arg.startswith('"') and arg.endswith('"'):
                    _add_token(type_="string", value=arg[1:-1])
                elif tools._is_num(arg):
                    _add_token(type_="number", value=arg)
                elif "[" in arg and "]" in arg:
                    base, t = arg.split("[", 1)
                    _add_token(type_="argumentDefinition", value={"argument": base, "type": t.rstrip("]")})
                elif tools._content_aware_check(arg, "="):
                    key, val = arg.split("=", 1)
                    _add_token(type_="kwarg", value={"kwarg": key, "value": val})
                else:
                    self.error_handler.add_error("Invalid argument type", arg, self.line)

        self.error_handler.throw_errors()

    
    @tools.enforce_types
    def _identify_function(self, name: str) -> dict | None:
        """
        Identifies the function type based on its name.
        
        Converts function names like "fn.name" into a specific format.
        
        Args:
          name (str): The name of the function
        
        Returns:
          function (dict): The function metadata or None
        """
        
        if name.startswith("fn."):
            return {
                "name": "functionCall",
                "value": name[3:]
            }
        elif name.startswith("func:"):
            return {
                "name": "functionDef",
                "value": name[5:]
            }
        elif name == "{":
            return {
                "name": "lcurly",
                "type": None,
                "value": "{"
            }
        elif name == "}":
            return {
                "name": "rcurly",
                "type": None,
                "value": "}"
            }
        else:
            return {
                "name": "function",
                "value": name
            }
    
    @tools.enforce_types
    def _tokenize_line(self, line: str):
        """
        Tokenizes the given line of KNP code and adds the tokens to self.tokens.
        
        Args:
          line (str): Line of KNP code to tokenize
        """
        
        # Remove leading and trailing whitespace
        line = line.strip()
        line = tools._content_aware_replace(line, " ", "")  # Remove whitespace internally
        
        # Skip empty lines and lines that are comments
        if not line or line[0].startswith("#"):
            return
        
        # Extract comment from line
        line, comment = tools._extract_comment(line)
        
        # Extract function name and arguments
        pieces = tools._extract(line)
        
        # Log line pieces
        self.error_handler.log(f"🧩🤔 - Cutting up line into pieces: {pieces}")
        
        # Add function to list
        self.tokens.append(self._identify_function(pieces["name"]))
        
        if pieces["name"] in ["{", "}"]:
            return
        
        # Parse arguments if they exist
        self.tokens.append({"name": "lparen", "type": None, "value": "("})
        if pieces["args"]:
            self._tokenize_args(pieces["args"])
        self.tokens.append({"name": "rparen", "type": None, "value": ")"})
            
        # Add comment token to list
        if comment:
            self.tokens.append({
                "name": "comment",
                "type": None,
                "value": comment
            })
            
        # Check for anything after the command
        if "->" in pieces["after"]:
            # Get return type
            return_type = ""
            if "{" in pieces["after"]:
                return_type = pieces["after"].split("->")[1].split("{")[0].strip()
            else:
                return_type = pieces["after"].split("->")[1].strip()
                
            self.tokens.append({
                "name": "funcType",
                "type": return_type,
                "value": "->"
            })
        
        if "{" in pieces["after"]:
            self.tokens.append({
                "name": "lcurly",
                "type": None,
                "value": "{"
            })
        elif "}" in pieces["after"]:
            self.tokens.append({
                "name": "rcurly",
                "type": None,
                "value": "}"
            })
    
    @tools.enforce_types
    def tokenize(self, code: str):
        """
        Tokenizes the given KNP code.
        
        Args:
          code (str): The KNP code to tokenize
        
        Returns:
          tokens (list): List of tokens generated from the code
        """
        
        # Set up tokens
        self.tokens.clear()
        self.code = code
        
        # Log start of tokenization
        self.error_handler.log("\n🧩 - Tokenizing code...")
        
        # Split code into lines
        lines = tools._content_aware_replace(code, selection=";\n", replacement="\n") 
        lines = tools._content_aware_replace(lines, selection=";", replacement="\n").split("\n")
        
        print(lines)
        
        # Tokenize each line
        for idx, line in enumerate(lines):
            self.line = idx
            self._tokenize_line(line)
            self.tokens.append({
                "name": "newline",
                "value": "\n"
            })
        
        return self.tokens

# Usage example
if __name__ == "__main__":
    with open(r"app_static\scripts\SETTINGS.json", "r") as f:
        loaded_settings = json.load(f)
    
    tokenizer_instance = Tokenizer(0, loaded_settings)
    
    with open("app_static\\scripts\\illegal.knip", "r") as f:
        code = f.read()
        print(tokenizer_instance.tokenize(code))