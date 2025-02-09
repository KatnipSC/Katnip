# Custom modules
import command_manager
import error_handler
import knp_tools as tools

class parser:
    """Parses tokens of KNIP files"""
    
    def __init__(self, project_id):
        """Initializes the parser."""
        
        self.project_id = project_id
        self.line = 1
        self.code = ""
        self.ast = [] # List of stacks
        
        # Token management
        self.tokens = []
        self.cur_token = 0
        
        self.error_handler = error_handler.error_handler(project_id)
    
    @tools.enforce_types
    def _capture_tokens(self, startValue: str, endValue: str) -> list:
        """
        Captures tokens from self.tokens between tokens with name==startValue and name==endValue.
        """
        
        captured_tokens = []
        depth = 0  # track nested delimiters
        while self.cur_token + 1 < len(self.tokens):
            self.cur_token += 1
            arg_token = self.tokens[self.cur_token]
            
            if arg_token["name"] == startValue:
                depth += 1
                if depth != 1:
                    captured_tokens.append(arg_token)
                continue
            elif arg_token["name"] == endValue:
                depth -= 1
                if depth == 0:
                    break
                captured_tokens.append(arg_token)
                continue
            else:
                captured_tokens.append(arg_token)
                
        return captured_tokens
    
    @tools.enforce_types
    def _INTERNAL_process_token(self, tokens: list) -> list:
        """
        Processes the given tokens in isolation, returning a list of processed tokens.
        
        ### Parameters:
        - tokens (list): List of tokens to process
        
        ### Returns:
        - processed_tokens (list): List of processed tokens
        """
        
        processed_args = []
        # Save the current tokens and pointer
        temp_tokens = self.tokens
        temp_cur_token = self.cur_token
        
        # Switch to the provided token list
        self.tokens = tokens
        self.cur_token = -1
        
        while self.cur_token + 1 < len(tokens):
            self.cur_token += 1
            processed_token = self._process_token()
            if processed_token:
                processed_args.append(processed_token)
            
        # Restore previous state
        self.tokens = temp_tokens
        self.cur_token = temp_cur_token
        
        return processed_args
        
    def _process_token(self):
        """
        Processes the current token.
        """
        
        token = self.tokens[self.cur_token]
        
        match token["name"]:
            case "newline":
                self.line += 1
                return None
            case "function" | "reporter" | "hat":
                # Look up command info
                token_data = command_manager.get_command(token["value"])
                if not token_data:
                    self.error_handler.add_error(
                        f"Command not-found: '{token['value']}'", self.code[self.line], self.line
                    )
                    self.error_handler.throw_errors()
                    
                opcode = token_data["opcode"]
                cmd_type = token_data["type"]
                args_list = token_data["args"]
                
                # For hat commands, it does NOT capture parenthesis arguments
                # instead, it captures the following curly block as a new "stack"
                if cmd_type == "hat":
                    hat_stack = []
                    # Check that a curly block follows
                    if (self.cur_token + 1 < len(self.tokens) and 
                        self.tokens[self.cur_token + 1]["name"] == "lcurly"):
                        hat_tokens = self._capture_tokens("lcurly", "rcurly")
                        # Process the tokens inside the hat block as a new AST (stack)
                        hat_stack = self._INTERNAL_process_token(hat_tokens)
                    # Return the hat token with its stack attached
                    return {"opcode": opcode, "type": cmd_type, "args": {}, "stack": hat_stack}
                else:
                    # For function and reporter commands, capture parenthesis arguments
                    arg_tokens = self._capture_tokens("lparen", "rparen")
                    arg_tokens = self._INTERNAL_process_token(arg_tokens)
                    all_args = dict(zip(args_list, arg_tokens))
                    
                    # Check for substacks (curly tokens) after the argument list
                    if (self.cur_token + 1 < len(self.tokens) and self.tokens[self.cur_token + 1]["name"] == "lcurly"):
                        if "i.substack" in token_data['args']:
                            substack_tokens = self._capture_tokens("lcurly", "rcurly")
                            substack_tokens = self._INTERNAL_process_token(substack_tokens)
                            all_args["substack"] = substack_tokens
                            
                            if "i.substack2" in token_data["args"]:
                                substack2_tokens = self._capture_tokens("lcurly", "rcurly")
                                substack2_tokens = self._INTERNAL_process_token(substack2_tokens)
                                all_args["substack2"] = substack2_tokens
                        else:
                            self.error_handler.add_error(
                                f"🧩⁉️ - '{token['value']}' received substack blocks, but does not expect any. "
                                f"Expected arguments: {token_data['args']}",
                                self.code[self.line], self.line
                            )
                            self.error_handler.throw_errors()
                    
                    if len(all_args) != len(args_list):
                        missing_arguments = [arg for arg in args_list if not all_args.get(arg)]
                        extraneous_arguments = [arg for arg in all_args if not arg in args_list]
                        print(missing_arguments, extraneous_arguments)
                        self.error_handler.add_error(
                            f"🔢❌ - Wrong number of arguments. '{token['value']}' expects "
                            f"[{len(args_list)}] arguments, but got [{len(all_args)}]",
                            self.code[self.line], self.line
                        )
                        self.error_handler.throw_errors()
                        
                    return {"opcode": opcode, "type": cmd_type, "args": all_args}
            case "argument":
                return token
    
    def parse(self, tokens, code):
        """
        Parses the given KNP tokens.
        
        AST comprises of list of "stacks" containing blocks
        """
        
        self.tokens = tokens
        self.cur_token = -1
        self.code = tools._content_aware_split(code, "\n")
        self.line = 1
        
        while self.cur_token + 1 < len(tokens):
            self.cur_token += 1
            token = tokens[self.cur_token]
            
            # Handle newlines
            if token.get("name") == "newline":
                self.line += 1
                continue
            
            processed_token = self._process_token()
            if processed_token:
                self.ast.append(processed_token)
            
        return self.ast

# with open("app_static\\generated_projects\\0\\log_0.txt", "w") as f:
#     f.write("")
    
# new_parser = parser(0)
# new_tokenizer = knp_tokenizer.tokenizer(0)
# with open("app_static\\scripts\\illegal.knp", "r") as f:
#     code = f.read()
#     ptokens = new_tokenizer.tokenize(code)
#     print(new_parser.parse(ptokens, code))
#     f.close()
