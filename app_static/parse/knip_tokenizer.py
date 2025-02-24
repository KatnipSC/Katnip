"""
This file is responsible for tokenizing the input code.

Responsibilities include:
- Tokenizing the input code
- Indentifying token type
- Basic deconstruction of the code
"""

# Custom modules
import error_handler
import knip_tools as tools

class tokenizer:
    """Tokenizes KNIP file contents"""
    
    def __init__(self, project_id: int):
        """
        Initializes the tokenizer.
        
        ### Parameters:
        - project_id (int): ID of the project being tokenized
        """
        
        self.project_id = project_id
        self.tokens = []
        self.line = 0
        self.code = ""
        
        self.error_handler = error_handler.error_handler(project_id)

    def _is_reporter(self, arg: str) -> bool:
        """
        Checks if the argument is a reporter.
        
        ### Parameters:
        - arg (str): The argument to check
        
        ### Returns:
        - bool: True if the argument is a reporter, False otherwise
        """
        return "(" in arg and ")" in arg and not arg.startswith("(")

    def _tokenize_args(self, args: list):
        """
        Tokenizes the arguments of a function into a dictionary
        Adds them to self.tokens

        ### Parameters:
        - args (list): List of arguments to tokenize
        """
        
        operator_tiers = [{"!": "op.not"},
                          {"^": "op.pow"}, # Note: ^ is not a valid operator in knip
                          {"*": "op.multiply", "/": "op.divide", "%": "op.mod"},
                          {"+": "op.add", "-": "op.subtract"},
                          {"<": "op.lt", ">": "op.gt", "<=": "op.lte", ">=": "op.gte"}, # Note: <= and >= are not valid operators in knip
                          {"==": "op.equals", "!=": "op.neq"}, # Note: != is not a valid operator in knip
                          {"&": "op.and"},
                          {"||": "op.or"}]

        for arg in args:
            # Find argument details
            argValue = ""
            argType = ""
            argName = "argument"
            
            def _add_token():
                """
                Adds a token to the tokens list
                """
                self.tokens.append({
                        "name": argName, 
                        "type": argType,
                        "value": argValue
                    })
            
            # NOTE: duplicated instances of operators makes this fail
            # NOTE: left to right handling is not implemented. precedence is still by tier order
            # Split argument into parts if it contains operator symbols
            for tier in operator_tiers:
                for symbol, path in tier.items():
                    if tools._content_aware_check(arg, symbol): # If the symbol is in the argument
                        arg1, arg2 = arg.split(symbol) # Split the argument into two parts
                        
                        # Process argument
                        self._tokenize_args([arg1])
                        self.tokens.append({
                            "name": "function",
                            "value": path
                        })
                        self._tokenize_args([arg2])
                        return

            # Parse argument
            if self._is_reporter(arg):
                # Cut up the reporter
                func_pieces = tools._extract(arg)
                argValue = func_pieces["name"]
                argName = "reporter"
                _add_token()
                
                # Tokenize the arguments of the reporter
                self.tokens.append({"name": "lparen", "type": None, "value": "("}) # Add the left parenthesis
                self._tokenize_args(func_pieces["args"])
                self.tokens.append({"name": "rparen", "type": None, "value": ")"}) # Add the right parenthesis
            elif arg.startswith("(") and arg.endswith(")"):
                # Handle grouped argument
                grouped_arg = arg[1:-1]
                self._tokenize_args([grouped_arg])
            elif arg.startswith("$"):
                argValue = arg[1:]
                argType = "variable"
                _add_token()
            elif arg.startswith("@l:"):
                argValue = arg[3:]
                argType = "list"
                _add_token()
            elif arg.startswith("@d:"):
                argValue = arg[3:]
                argType = "dictionary"
                _add_token()
            elif arg.startswith("a."):
                argValue = arg[2:]
                argType = "functionArgument"
                _add_token()
            elif arg.startswith('"'):
                argValue = arg[1:-1]
                argType = "string"
                _add_token()
            elif tools._is_num(arg):
                argValue = arg
                argType = "number"
                _add_token()
            elif "[" in arg and "]" in arg:
                argValue = {"argument": arg.split("[")[0], "type": arg.split('[')[1][:-1]}
                argType = "argumentDefinition"
                _add_token()
            elif tools._content_aware_check(arg, "="):
                argValue = {"kwarg": arg.split("=")[0], "value": arg.split("=")[1]}
                argType = "kwarg"
                _add_token()
            else:
                self.error_handler.add_error("Invalid argument type", arg, self.line)

        self.error_handler.throw_errors() # Will automatically check for any errors, and will raise all found errors
    
    @tools.enforce_types
    def _identify_function(self, name: str) -> dict | None:
        """
        Identifies the function type based on the function name
        I.e. turning fn.name into ["functionCall", name]
        
        ### Parameters:
        - name (str): The name of the function
        
        ### Returns:
        - function (dict): The function metadata
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
        Tokenizes the given line of KNP code.
        Adds the tokens to self.tokens
        
        ### Parameters:
        - line (str): Line of KNP code to tokenize
        """
        
        # Remove leading and trailing whitespace
        line = line.strip()
        line = tools._content_aware_replace(line, " ", "") # Remove whitespace internally
        
        # Skip empty lines, and lines that are comments
        if not line or line[0].startswith("#"):
            return
        
        # Extract comment from line
        line, comment = tools._extract_comment(line)
        
        # Extract function name and arguments
        pieces = tools._extract(line)
        
        # Add function to list
        self.tokens.append(self._identify_function(pieces["name"]))
        
        if pieces["name"] in ["{", "}"]:
            return
        
        # Parse arguments if exist
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
            returnType = ""
            if "{" in pieces["after"]:
                returnType = pieces["after"].split("->")[1].split("{")[0].strip()
            else:
                returnType = pieces["after"].split("->")[1].strip()
                
            self.tokens.append({
                "name": "funcType",
                "type": returnType,
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
        Tokenizes the given KNP code
        
        ### Parameters:
        - code (str): The KNP code to tokenize
        
        ### Returns:
        - tokens (list): List of tokens
        """
        
        # Set up tokens
        self.tokens.clear()
        self.code = code
        
        # Split code into lines
        lines = tools._content_aware_replace(code, selection=";\n", replacement="\n") # Remove any lines with a ; right before a newline; without this, it would mess up line #
        lines = tools._content_aware_replace(lines, selection=";", replacement="\n").split("\n") # Replace ; split lines with \n to standardize; then split by \n
        
        # Tokenize each line
        for idx, line in enumerate(lines):
            self.line = idx
            self._tokenize_line(line)
            self.tokens.append({
                "name": "newline",
                "value": "\n"
            })
        
        return self.tokens
    
new_tokenizer = tokenizer(0)
with open("app_static\\scripts\\newComp.knip", "r") as f:
    code = f.read()
    print(new_tokenizer.tokenize(code))
    f.close()