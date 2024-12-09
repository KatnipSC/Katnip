"""
Main parsing logic for the code
"""

import json
import os
import tempfile
import shutil
import zipfile
import copy

import command_manager
import error_handler

class project():
    def __init__(self, filename):
        # self.stacks and self.stack_height are used to space out the stacks and position comments
        self.stacks = 0
        self.stack_height = 25
        self.stack_spacing = 600 # The x-tiling spacing between stacks

        self.CUR_ID = 0 # Used to make unqiue id's
        self.variables = dict() # List of all variables
        self.lists = dict() # List of all lists
        self.broadcasts = dict() # List of all broadcast
        tmpdir = tempfile.mkdtemp()
        with zipfile.ZipFile(filename, "r") as zip_ref:
            zip_ref.extractall(tmpdir)
        with open(os.path.join(tmpdir, "project.json")) as f:
            self.data = json.loads(f.read())
        self.origin = filename
        shutil.rmtree(tmpdir)
    
    def _extract(self, string: str):
        """
        Extracts name and arguments from a string (a line containing a function).

        Parameters:
        - string (str): The string of the line containing the relavent function

        Returns:
        - pieces (dict): A dictionary containing the name and arguments of the function
            - ["name"] (str): The name of the function
            - ["args"] (list): A list of arguments for the function
        """

        pieces = {}
        pieces["name"] = string.split("(")[0]

        args_string = string[string.find("(") + 1 : string.rfind(")")]
        args = []
        current_arg = []
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
        return pieces
    
    def _remove_whitespace(self, text: str):
        """
        Removes whitespace from the text, ignoring any whitespace inside quotes (strings)

        Parameters:
        - text (str): The text to remove whitespace from

        Returns:
        - str: The text with whitespace removed, ignoring quotes
        """
        depth = 1
        return_text = ''
        for letter in text:
            if letter == '"':
                depth *= -1
            if letter == ' ' and depth == 1:
                continue
            else:
                return_text += letter
        return return_text

    def _is_num(self, value: str):
        """
        Checks if a given value is a valid number. (only allows characters in "-.0123456789")

        Parameters:
        - value (str): The value to check

        Returns:
        - bool: True if the value is a valid number, False otherwise
        """

        if len(value) == 0:
            return False
        for character in value:
            if not character in "-.0123456789":
                return False
        return True

    def _generate_id(self, arg=None):
        """
        Generates a unique ID. This can be for anything needing an ID.

        Parameters:
        - arg (str | None): optional, is added to the unique ID's name to denote certain aspects.
            (e.g. "var" or "broadcast", etc.)

        Returns:
        - str: The unique ID
        """

        self.CUR_ID += 1
        if arg:
            return f"scratchtext-{arg}-{self.CUR_ID}"
        else:
            return f"scratchtext-{self.CUR_ID}"
       
    def _read_variable(self, name: str):
        """
        Returns the id of a variable. Creates the variable if it does not exist.

        Parameters:
        - name (str): The name of the variable

        Returns:
        - str: The id of the variable
        """

        if not name in self.variables:
            self.variables[name] = self._generate_id(arg="var")
        return self.variables[name]
    
    def _read_list(self, name: str):
        """
        Returns the id of a list. Creates the list if it does not exist.

        Parameters:
        - name (str): The name of the list

        Returns:
        - str: The id of the list
        """

        if not name in self.lists:
            self.lists[name] = self._generate_id(arg="list")
        return self.lists[name]
    
    def _read_broadcast(self, name: str):
        """
        Returns the id of a broadcast. Creates the broadcast if it does not exist.

        Parameters:
        - name (str): The name of the broadcast

        Returns:
        - str: The id of the broadcast
        """

        if not name in self.broadcasts:
            self.broadcasts[name] = self._generate_id(arg="broadcast")
        return self.broadcasts[name]
    
    def _create_comment(self, comment: str, block_id: str):
        """
        Returns the id of a comment. Creates the comment if it does not exist

        Parameters:
        - comment (str): The comment to add
        - block_id (str): The id of the block that the comment is attached to

        Returns:
        - str: The id of the comment
        """

        comment_id = self._generate_id(arg="comment")
        self.target["comments"][comment_id] = {
            "blockId": block_id,
            "x": self.stacks * self.stack_spacing + 200,
            "y": self.stack_height,
            "width": 200,
            "height": 200,
            "minimized": True,
            "text": comment
        }
        return comment_id
    
    def _extract_comment(self, text: str):
        """
        Seperates the comment from the line of code and returns a tuple containing both.

        Parameters:
        - text (str): The line of code containing a comment

        Returns:
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
    
    def add_sprite_scripts(self, target: str, program: str):
        """
        Adds sprite scripts to the specified target, parsing through program.

        Parameters:
        - target (str): The name of the target (e.g. "S1" or "Sprite1")
        - program (str | list): The program to parse and add to the target
        """

        # Parse through the program
        for existing_target in self.data["targets"]:
            if existing_target["name"] == target:
                self.target = existing_target
                self._parse(program.split("\n"))

        # Add relavent variables
        for target in self.data["targets"]:
            if target["isStage"]: # Only add these for stage (all variables are global so they go in stage)
                # Process the generated variables
                if "variables" not in target:
                    target["variables"] = dict()
                for variable in self.variables:
                    variable_id = self.variables[variable]
                    target["variables"][variable_id] = [variable, "0"]

                # Process the generated lists
                if "lists" not in target:
                    target["lists"] = dict()
                for list_name in self.lists:
                    list_id = self.lists[list_name]
                    target["lists"][list_id] = [list_name,[]]

                # Process the generated broadcasts
                if "broadcasts" not in target:
                    target["broadcasts"] = dict()
                for broadcast_name in self.broadcasts:
                    broadcast_id = self.broadcasts[broadcast_name]
                    target["broadcasts"][broadcast_id] = broadcast_name
       
    def _parse(self, lines: list, substack=False):
        """
        Parses the given lines and adds them to self.target (current target)
            Will return a string ID of the topmost block if it is a substack for provessing substacks

        Parameters:
        - lines (list): The list of lines to parse
        - substack (bool): Whether this is a substack (used for parsing nested c blocks)

        Returns:
        - top_id (str | None): The ID of the topmost block [IF] it is a substack for processing substacks
        """

        print(lines)
        prev_block = []
        line_num = 0 # We are using a while loop with counter instead of for loop to account for c blocks with blocks inside "substack"
        top_id = ""
        while line_num < len(lines):
            # Check if line is a comment line
            if lines[line_num].startswith("#"): # I use ".startswith" instead of "in" bc i want to create comments attached to blocks later
                line_num += 1
                continue

            # Check if there is an empty line
            if lines[line_num] == "":
                line_num += 1
                continue

            # Exiting hat block
            if not substack:
                if "}" in lines[line_num]:
                    prev_block = []
                    line_num += 1
                    self.stacks += 1 # Increase number of stacks
                    self.stack_height = 25 # Reset stack height
                    continue

            # Setup line counter and line value
            line = lines[line_num]
            print(line)

            # Remove comments (if they exist)
            line, comment = self._extract_comment(line) # Will return (line, None) if a comment is not found

            # Parse line
            token_list = self._remove_whitespace(line) # remove whitespace

            # Split string into name and arguments
            token_list = self._extract(token_list)

            if len(token_list["args"]) > 0: # Might have no arguments
                # Parse the arguments
                func_args = token_list["args"]
                func_args = self._simplify_args(func_args, line_num)
            else:
                # Make empty argument list
                func_args = []

            heights = {
                "hat": 7,
                "reporter": 0, # Look in "_simplify_args" to see/edit this value. It is applied there bc there reporters in reporters are processed
                "stack": 48,
                "extension_stack": 56,
                "c": 48,
                "c_end": 32,
                "cap": 48
            }

            # Define type of block being processed
            token_type = command_manager.read_by_name(token_list["name"])
            if token_type:
                if "pen" in token_type["opcode"] and token_type["type"] == "stack": # For some odd reason, extension stack blocks are longer than regular stack blocks 😖
                    self.stack_height += heights["extension_stack"]
                else:
                    self.stack_height += heights[token_type["type"]]
                token_type = token_type["type"]
            else:
                print()
                error_handler.add_error(f"Invalid command '{token_list['name']}'", lines[line_num], line_num+1)
                error_handler.throw_errors()

            # Create the block
            if token_type == "c": # C-blocks need to parse their substack blocks
                substack_blocks = []
                line_num += 1 # Adjust for currently being processed c-block

                bracket_depth = 0 # Track the depth of the scanner
                # Collect lines for parsing the substack
                while (line_num < len(lines) and lines[line_num].strip()) and not ("}" in lines[line_num] and bracket_depth == 0):
                    if "{" in lines[line_num]:
                        bracket_depth += 1
                    elif "}" in lines[line_num]:
                        bracket_depth -= 1
                    substack_blocks.append(lines[line_num])
                    line_num += 1

                # Check if it is end of file without running into a closing }
                if line_num == len(lines) and not "}" in lines[line_num-1]:
                    error_handler.add_error("Unexpected end of code block. Expected '}'",lines[line_num-1], line_num)
                    error_handler.throw_errors()

                # Parse the substack into blocks
                substack_prev_block = prev_block  # Save current state of prev_block
                prev_block = []  # Reset for substack parsing
                substack_top_block = self._parse(substack_blocks, substack=True)  # Top block of the substack
                prev_block = substack_prev_block  # Restore prev_block

                # Add the substack block as an argument to the func_args
                if substack_top_block:
                    func_args.append(["substack", substack_top_block])

                # Create the c-block
                new_block = self._create_block(token_list["name"], func_args, prev_block, comment)

                # Update the substack_top_block to have the parent be the c-block
                self.target["blocks"][substack_top_block]["parent"] = new_block[0]

                # Increase height by end of c-block
                self.stack_height += heights["c_end"]

            else: # Normal parse. Any block that isnt a c-block will be processed this way
                new_block = self._create_block(token_list["name"], func_args, prev_block, comment)

            if prev_block:
                prev_block[1]["next"] = new_block[0] # Update the previous block's "next" attribute
            elif not substack:
                new_block[1]["topLevel"] = True # Update the current block's "topLevel" attribute to be top-level if it has no parents

            # Save the block, and update the previous block
            self.target["blocks"][new_block[0]] = new_block[1]
            if line_num == 0 and substack: # Log if it is the top of the stack and is part of a substack
                top_id = new_block[0]
            prev_block = new_block

            # Update line_num
            line_num += 1

        if substack:
            return top_id # Return the top block of the substack

    def _simplify_args(self, args: list | str, line_num: int, itr = 0):
        """
        Simplifies the arguments, parsing through recursively.

        Parameters:
        - args (list | str): The list of arguments to simplify
        - line_num (int): The line number for error handling
        - itr (int): Internal counter for recursion of reporters

        Returns:
        - return_args (list): The simplified list of arguments (2D array)
            List of [type, relavent_data] for each argument
        """

        if itr == 0: # first recursion
            self.itr = 0

        if args == "": # No argument blocks
            return []
        if isinstance(args, str):
            args = [args]
        
        args = [arg for arg in args if not arg == ""]
        return_args = [] # 2d list of arguments [type, relavent_data]

        for arg in args:
            if arg.startswith("$"):
                var_name = arg[1:]
                return_args.append(["variable", [var_name, self._read_variable(var_name)]])
            elif arg.startswith("@"):
                list_name = arg[1:]
                return_args.append(["list", [list_name, self._read_list(list_name)]])
            elif arg.startswith('"'):
                return_args.append(["str", arg[1:-1]])
            elif self._is_num(arg):
                return_args.append(["num", arg])
            elif "(" in arg and ")" in arg:
                if itr == 0: # Increase the stack height bc a reporter in a reporter increases the width of a c-block
                    self.stack_height += 4 # First recursion level is always slightly more than the next
                elif itr > self.itr: # Recursion depth has not been reached before
                    self.stack_height += 1.5 # Increase the stack height slightly less for the later recursion levels
                # Create a new stack block with its relavent data
                func_pieces = self._extract(arg)
                simplified_args = self._simplify_args(func_pieces["args"], line_num, itr + 1)
                func = self._create_block(func_pieces["name"], simplified_args)
                self.target["blocks"][func[0]] = func[1]

                return_args.append(["reporter", func]) # Return the block
            else:
                error_handler.add_error("Invalid argument type",arg,line_num+1)

        error_handler.throw_errors() # Will automatically check for any errors, and will raise all found errors
        return return_args

    def _create_block(self, name, args, prev=None, comment=None):
        """
        Creates a new block given its name and arguments

        Parameters:
        - name (str): The name of the block
        - args (list): The arguments for the block
        - prev (list): The previous block (if any)
            - [0]: The previous block's id
            - [1]: The previous block's data
        - comment (str | None): The comment for the block
        
        Returns:
        - block_id (str): The ID of the block
        - block (dict): The created block
            - ["opcode"]: The opcode of the block
            - ["parent"]: The ID of the parent block
            - ["next"]: The ID of the next block
            - ["inputs"]: The inputs for the block
            - ["fields"]: The fields for the block
            - ["shadow"]: A boolean indicating if the block is a shadow block
            - ["topLevel"]: A boolean indicating if the block is top-level
            - ["x"]: The x-coordinate of the block
            - ["y"]: The y-coordinate of the block
        """
        # Create a new ID for the block
        block_id = self._generate_id()

        # Get data about block (input parameters)
        #print("getting data about block:", name)
        data = command_manager.read_by_name(name)
        print("getting block:", name)

        # Create block template
        block = {
            "opcode": data["opcode"],
            "parent": None,
            "next": None,
            "inputs": {},
            "fields": {},
            "shadow": False,
            "topLevel": False
        }

        # Check if a comment exists, if it does, add it
        if comment:
            block["comment"] = self._create_comment(comment, block_id)

        # If block is not a reporter, create x and y coordinates for it
        if data["type"] == "hat":
            block["x"] = self.stacks * self.stack_spacing
            block["y"] = 25

        # If its a menu block, it needs a shadow flag
        if "menu" in name:
            block["shadow"] = True

        # Set parent block
        if prev:
            block["parent"] = prev[0]
       
        fill_args = data["inputs"]
        fill_args = fill_args.split(",") if not fill_args == "" else []

        # Define data setup types (not used, just for reference below)
        types = {
            "substack": [2,"id"],
            "variable": [3,[12,"name","id"],[10,""]],
            "str/num": [1, [10, "value"]],
            "reporter": [3, "id", [10,""]]
        }

        # Check for correct number of arguments
        if len(fill_args) != len(args):
            error_handler.add_error(f"Invalid number of arguments. '{name}' expects [{len(fill_args)}] arguments, but got [{len(args)}]", args, -1)
            error_handler.throw_errors()

        # Input args
        for fill_arg, arg in zip(fill_args, args):
            # Figure out if arguments are for inputs or fields
            if fill_arg.startswith("i."):
                arg_type = "input"
            elif fill_arg.startswith("f."):
                arg_type = "field"
            fill_arg = fill_arg[2:] # Remove leading type for argument (e.g. i.arg --> arg, or f.arg --> arg)

            # Remove hints. This will hopefully be used when we get a gui for autocompletion
            boolean = "[bool]" in fill_arg
            if boolean:
                if arg[0] == "reporter":
                    fill_arg = fill_arg[:fill_arg.find("[")]+fill_arg[fill_arg.find("]")+1:]
                else:
                    error_handler.add_error(f"Invalid input argument type. Expected 'boolean', got '{arg[0]}'", fill_arg, -1)
                    error_handler.throw_errors()

            # Handle menu items. These are not written directly, but instead are generated based on the arguments from their parents
            if "(" in fill_arg and arg[0] == "str": # parse menu items
                    arg[0] = "menu" # set the type to menu
                    menu = self._create_block(fill_arg[fill_arg.find("(")+1:fill_arg.find(")")],[["str", str(arg[1])]],[block_id, block])
                    arg[1] = menu[0] # provide the menu's opcode to the parent block
                    self.target["blocks"][menu[0]] = menu[1] # add the block to the block list
                    fill_arg = fill_arg[:fill_arg.find("(")]+fill_arg[fill_arg.find(")")+1:] # remove the menu data

            # Preprocess the argument, checking if it is a broadcast argument. If it is, chang ethe arg[0] type to broadcast
            if (arg[0] == "str" or arg[0] == "num") and "broadcast" in fill_arg:
                arg[0] = "broadcast"

            # Pen extention blocks do not use all caps arguments for some reason 😖
            if not ("menu" in name and "pen_" in data["opcode"]):
                fill_arg = fill_arg.upper()

            
            # Handle input arguments, correctly adding them to the block json data
            if arg_type == "input": # i. --> argument goes into inputs
                match arg[0]:
                    case "str":
                        block["inputs"][fill_arg] = [1, [10, arg[1]]]
                    case "num":
                        block["inputs"][fill_arg] = [1, [10, arg[1]]]
                    case "variable":
                        block["inputs"][fill_arg] = [3, [12, arg[1][0], arg[1][1]], [10, "❤️"]]
                    case "list":
                        block["inputs"][fill_arg] = [3, [13, arg[1][0], arg[1][1]], [10, "❤️"]]
                    case "reporter":
                        self.target["blocks"][arg[1][0]]["parent"] = block_id
                        block["inputs"][fill_arg] = [3, arg[1][0], [10, "❤️"]] if not boolean else [2, arg[1][0]]
                    case "substack":
                        block["inputs"][fill_arg] = [2, arg[1]]
                    case "menu":
                        block["inputs"][fill_arg] = [1, arg[1]]
                    case "broadcast":
                        block["inputs"][fill_arg] = [1, [11, arg[1], self._read_broadcast(arg[1])]]
            elif arg_type == "field": # f. --> argument goes into fields
                match arg[0]:
                    case "str":
                        block["fields"][fill_arg] = [arg[1], None]
                    case "num":
                        block["fields"][fill_arg] = [arg[1], None]
                    case "variable":
                        block["fields"][fill_arg] = arg[1]
                    case "list":
                        block["fields"][fill_arg] = arg[1]
                    case "broadcast":
                        block["fields"][fill_arg] = [arg[1], self._read_broadcast(arg[1])]

        print(block_id, block)
        return block_id, block
    
    def write(self, filename):
        """
        Writes the current project data to a file. Creates the SB3 file

        Parameters:
        - filename (str): The name of the SB3 file to write to
        """
        # Load old contents
        tmpdir = tempfile.mkdtemp()
        with zipfile.ZipFile(self.origin, "r") as zip_ref:
            zip_ref.extractall(tmpdir)

        # Replace project.json
        with open(os.path.join(tmpdir, "project.json"), "w") as f:
            f.write(json.dumps(self.data))

        zip_ref = zipfile.ZipFile(filename, "w")
        for content_file in os.listdir(tmpdir):
            zip_ref.write(os.path.join(tmpdir, content_file), arcname=content_file)
        zip_ref.close()

        with open("generated_projects\\project.json", "w") as f:
            f.write(json.dumps(self.data))
        shutil.rmtree(tmpdir)