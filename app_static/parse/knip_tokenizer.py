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
        Tokenizes the arguments of a function into a dictionary and adds them to self.tokens.
        
        Args:
          args (list): List of arguments to tokenize
        """
        
        # Log arguments being tokenized
        self.error_handler.log(f"🔨⛓️‍💥 - Tokenizing arguments: {args}")
        
        operator_tiers = [
            # {"!": "op.not"},  # Note: ! will be processed within identification of arguments
            # because it only affects the right token
            {"^": "op.pow"}, 
            {"*": "op.multiply", "/": "op.divide", "%": "op.mod"},
            {"+": "op.add", "-": "op.subtract"},
            {"<": "op.lt", ">": "op.gt", "<=": "op.lte", ">=": "op.gte"}, 
            {"==": "op.equals", "!=": "op.nequals"},
            {"&&": "op.and"},
            {"||": "op.or"}
        ]
        
        operators_raw = [op for tier in operator_tiers for op in tier.keys()]
        operators_raw_dict = {op: path for tier in operator_tiers for op, path in tier.items()}
        operator_tiers.reverse()
        
        for arg in args:
            # Check to see if the argument is an operator
            if arg in operators_raw:
                self.tokens.append({
                    "name": "function",
                    "value": operators_raw_dict[arg]
                })
                continue
            
            arg_value: Union[str, dict] = ""
            arg_type = ""
            arg_name = "argument"
            
            def _add_token():
                """Adds a token to the tokens list."""
                self.tokens.append({
                    "name": arg_name, 
                    "type": arg_type,
                    "value": arg_value
                })
            
            # Handle operators and split the argument if necessary
            was_simplified = False
            for tier in operator_tiers:
                instances: list[tuple[int, int]] = []  # Instances of operator found in the current tier
                
                for symbol, path in tier.items(): 
                    instances.extend((idx, len(symbol)) for idx in tools._get_occurences(arg, symbol)) 
                
                sub_args = []
                if instances:
                    for index in sorted(instances, key=lambda x: x[0], reverse=True): 
                        sub_args.append(arg[index[0] + index[1]:]) 
                        sub_args.append(arg[index[0]:index[0] + index[1]]) 
                        arg = arg[:index[0]] 
                    sub_args.append(arg) 
                
                # Process arguments
                if sub_args:
                    self.error_handler.log(f"🧩🔣 - Argument operators found: '{sub_args[1]}'")
                    self._tokenize_args(sub_args[::-1]) 
                    was_simplified = True 
                    break
            
            if was_simplified: 
                continue
            
            # Tokenize types of arguments
            if self._is_reporter(arg):
                func_pieces = tools._extract(arg)
                arg_value = func_pieces["name"]
                arg_name = "reporter"
                _add_token()
                
                # Tokenize the arguments of the reporter
                self.tokens.append({"name": "lparen", "type": None, "value": "("}) 
                self._tokenize_args(func_pieces["args"])
                self.tokens.append({"name": "rparen", "type": None, "value": ")"}) 
            elif arg.startswith("(") and arg.endswith(")"):
                grouped_arg = arg[1:-1]
                self._tokenize_args([grouped_arg])
            elif arg.startswith("$"):
                arg_value = arg[1:]
                arg_type = "variable"
                _add_token()
            elif arg.startswith("@l:"):
                arg_value = arg[3:]
                arg_type = "list"
                _add_token()
            elif arg.startswith("@d:"):
                arg_value = arg[3:]
                arg_type = "dictionary"
                _add_token()
            elif arg.startswith("a."):
                arg_value = arg[2:]
                arg_type = "functionArgument"
                _add_token()
            elif arg.startswith('"'):
                arg_value = arg[1:-1]
                arg_type = "string"
                _add_token()
            elif tools._is_num(arg):
                arg_value = arg
                arg_type = "number"
                _add_token()
            elif "[" in arg and "]" in arg:
                arg_value = {"argument": arg.split("[")[0], "type": arg.split('[')[1][:-1]}
                arg_type = "argumentDefinition"
                _add_token()
            elif tools._content_aware_check(arg, "="):
                arg_value = {"kwarg": arg.split("=")[0], "value": arg.split("=")[1]}
                arg_type = "kwarg"
                _add_token()
            else:
                self.error_handler.add_error("Invalid argument type", arg, self.line)
        
        self.error_handler.throw_errors()  # Check for and raise any found errors
    
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