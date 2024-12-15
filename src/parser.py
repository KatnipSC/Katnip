"""
Main parsing logic for the code
"""

import json
import os
import tempfile
import shutil
import zipfile
import copy
from PIL import ImageFont

import command_manager
import error_handler

class project():
    def __init__(self, filename):
        # self.stacks and self.stack_height are used to space out the stacks and position comments
        self.stacks = 0
        self.stack_height = 0
        self.stack_width = 0
        self.stack_spacing = 600 # The x-tiling spacing between stacks
        self.comment_offset = 25 # The offset between the block + comment
        self.line = 0 # For tracking line numbers for error messages

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
    
    def _create_comment(self, comment: str, block_id: str, height=None):
        """
        Returns the id of a comment. Creates the comment if it does not exist

        Parameters:
        - comment (str): The comment to add
        - block_id (str): The id of the block that the comment is attached to
        - height (int | None): The y-position of the comment, defaults to self.stack_height

        Returns:
        - str: The id of the comment
        """

        offset = 15 # There is an offset between the middle of the block, and where the comment connects to the block
        comment_id = self._generate_id(arg="comment")
        #print("Current width:", self.stack_width)
        self.target["comments"][comment_id] = {
            "blockId": block_id,
            "x": self.stacks * self.stack_spacing + self.stack_width + self.comment_offset,
            "y": height-offset if height else self.stack_height-offset,
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
        
    def _check_else(self, line):
        """
        Checks if the line has an else statement in it.
        It will set self.else_clause to the resulting boolean argument (true/false)

        Parameters:
        - line (str): The line of code to check for an else statement

        Returns:
        - bool: True if the line contains an else statement, False otherwise
        """

        line = self._extract_comment(line)[0]

        depth = 1
        for idx, letter in enumerate(line):
            if letter == '"':
                depth *= -1
            if letter == 'e' and depth == 1:
                if line[idx:idx+4] == "else":
                    return True
        return False

    def _check_char(self, line, char):
        """
        Checks if the line contains a specific character.

        Parameters:
        - line (str): The line of code to check for the character
        - char (str): The character to look for

        Returns:
        - bool: True if the character is found in the line, False otherwise
        """

        line = self._extract_comment(line)[0]

        depth = 1
        for letter in line:
            if letter == '"':
                depth *= -1
            if letter == char and depth == 1:
                return True
        return False
    
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
                self.line = 0 # Set line num to 0 (reset line counter)
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
       
    def _parse(self, lines: list, substack=False, depth=0):
        """
        Parses the given lines and adds them to self.target (current target)
            Will return a string ID of the topmost block if it is a substack for provessing substacks

        Parameters:
        - lines (list): The list of lines to parse
        - substack (bool): Whether this is a substack (used for parsing nested c blocks)
        - depth (int): The current depth of the parsing (used for indented c blocks)

        Returns:
        - top_id (str | None): The ID of the topmost block [IF] it is a substack for processing substacks
        """

        # print(lines)
        prev_block = []
        line_num = 0 # We are using a while loop with counter instead of for loop to account for c blocks with blocks inside "substack"
        top_id = ""
        top_idx = -1
        while line_num < len(lines):
            self.line += 1

            # Check if line is a comment line
            if self._remove_whitespace(lines[line_num]).startswith("#"): # I use ".startswith" instead of "in" bc of comments on the same line as code
                line_num += 1
                continue

            # Check if there is an empty line
            if lines[line_num] == "":
                line_num += 1
                continue

            if top_idx == -1: # Any blank lines or comment only lines are all skipped over if it has reached this line
                top_idx = line_num # Set the "true" top to be the current line for determining which line should return it's ID

            # Exiting hat block
            if not substack:
                if self._check_char(lines[line_num], "}"):
                    prev_block = []
                    line_num += 1
                    self.stacks += 1 # Increase number of stacks
                    self.stack_height = 0 # Reset stack height
                    continue

            if self._extract_comment(lines[line_num])[0].strip() == "}":
                line_num += 1
                continue

            # Setup line counter and line value
            line = lines[line_num]
            cur_line = line_num
            #print(line)

            # Remove comments (if they exist)
            line, comment = self._extract_comment(line) # Will return (line, None) if a comment is not found

            # Parse line
            token_list = self._remove_whitespace(line) # remove whitespace

            heights = {
                "hat": 48,
                "reporter": 0, # Look in "_simplify_args" to see/edit this value. It is applied there bc there reporters in reporters are processed
                "stack": 48,
                "extension_stack": 56,
                "c": 48,
                "c_end": 32,
                "cap": 48
            }

            # Split string into name and arguments
            token_list = self._extract(token_list)

            # Define type of block being processed
            token_type = command_manager.read_by_name(token_list["name"])

            if token_type: # Check if it found command for the name
                # Pseudo implementation for width of blocks. Can't do much better without spending 100s of hours documenting the widths based on comment positions auto-generated by scratch
                self.stack_width = 300 + depth * 20

                # Set self.argument_limit to the maximum depth of arguments it can take before expanding vertically
                self.argument_limit = 0 # Will start increasing when argument depth is great than the argument limit (0 --> skip 1st, 1 --> skip 2nd, etc.)

                # Check for pen extension stacks
                if "pen" in token_type["opcode"] and token_type["type"] == "stack": # For some odd reason, extension stack blocks are longer than regular stack blocks 😖
                    self.argument_limit =  1 # Will start increasing when argument depth is great than the argument limit (0 --> skip 1st, 1 --> skip 2nd, etc.)
                    token_type["type"] = "extension_stack"

                self.stack_height += heights[token_type["type"]] / 2 # Add first half of the block (midway down the block for comment)
                token_type = token_type["type"]
            else:
                error_handler.add_error(f"Invalid command '{token_list['name']}'", lines[line_num], self.line)
                error_handler.throw_errors()

            # Get current stack height before adding inside tokens (to help c-blocks find where their comments should go)
            current_stack_height = self.stack_height # Get height BEFORE parsing arguments, so we can later add half of the height

            if len(token_list["args"]) > 0: # Might have no arguments
                # Parse the arguments
                func_args = token_list["args"]
                func_args = self._simplify_args(func_args, line_num)
                if token_type == "extension_stack":
                    arg_height = self.itr - 1 # Extension stacks can handle 2 layers of arguments before expanding
                    arg_height = arg_height if arg_height >= 0 else 0 # Make sure no negitive heights. If self.itr is 0, we don't want -1
                else:
                    arg_height = self.itr

                # Add half the arguments height to the current stack height
                current_stack_height += (arg_height * 8) / 2
            else:
                # Make empty argument list
                func_args = []

            # Get current stack width after parsing the arguments, to now allow any other parsing to proceed
            current_stack_width = self.stack_width

            # Add second half of the block
            self.stack_height += heights[token_type] / 2
            error_handler.log("On line: " + line)
            # Create the block
            if token_type == "c": # C-blocks need to parse their substack blocks
                substack_blocks = []
                # line_num += 1 # Adjust for currently being processed c-block

                bracket_depth = 1  # To count brackets for closing braces in substack blocks (we set to 1 for openning braces skipped over)

                # Collect lines for parsing the substack
                while line_num + 1 < len(lines): # Repeat while line_num is within line number, current line is not blank, and not(ending thingy in current line, and bracket depth = 0 e.g. ending of current look)
                    # Get next line
                    line_num += 1
                    self.line += 1

                    # Update depth
                    if self._check_char(lines[line_num], "{"):
                        bracket_depth += 1
                    if self._check_char(lines[line_num], "}"):
                        bracket_depth -= 1

                    error_handler.log(f"Processing line {line_num}: {lines[line_num]} (bracket depth: {bracket_depth}), {self._check_char(lines[line_num], "}")}")

                    # Check for else block
                    if self._check_else(lines[line_num]): # Else condition found
                        if bracket_depth == 1:
                            substack_blocks.append("else")
                        else:
                            substack_blocks.append(lines[line_num])
                    elif not (bracket_depth == 0 and self._check_char(lines[line_num], "}")): # Regular line that doesn't have a closing }
                        substack_blocks.append(lines[line_num])
                    elif line_num+1 == len(lines): # Last line found
                        break
                    elif self._check_else(lines[line_num+1]): # If it does have a closing }, but there is an else statement next, continue
                        continue
                    else: # Closing } found
                        break

                error_handler.log("HERES MY HAUL: " + str(substack_blocks))
                # Check if it is end of file without running into a closing }
                if line_num == len(lines) and not "}" in lines[line_num-1]:
                    error_handler.add_error("Unexpected end of code block. Expected '}'",lines[line_num-1], self.line)
                    error_handler.throw_errors()

                # Parse the substack into blocks
                substack_prev_block = prev_block  # Save current state of prev_block
                prev_block = []  # Reset for substack parsing
                substack2_top_block = ""
                if "else" in substack_blocks: # "else" will only exist for the current layer
                    else_location = substack_blocks.index("else") # Get the location of the else block
                    error_handler.log("!!! Else " + str(substack_blocks[:else_location]) + str(substack_blocks[else_location+1:]))
                    substack_top_block = self._parse(substack_blocks[:else_location], substack=True, depth=depth+1)  # Top block of the substack1
                    prev_block = []  # Reset for next substack parsing
                    self.stack_height += heights["c_end"] # Increment stack height for middle block of "if-else" block
                    substack2_top_block = self._parse(substack_blocks[else_location+1:], substack=True, depth=depth+1)  # Top block of the substack1
                else:
                    substack_top_block = self._parse(substack_blocks, substack=True, depth=depth+1)  # Top block of the substack1
                prev_block = substack_prev_block  # Restore prev_block

                # Add the substack block as an argument to the func_args
                func_args.append(["substack", substack_top_block])
                if substack2_top_block:
                    token_list["name"] = "ifelse"
                    func_args.append(["substack", substack2_top_block])

                # Set the width to the previously stored width
                self.stack_width = current_stack_width

                # Create the c-block
                error_handler.log(token_list["name"])
                new_block = self._create_block(token_list["name"], func_args, prev_block, [comment, current_stack_height - 5]) # Reduce by a little bit to account for a weird offset

                # Update the substack_top_block to have the parent be the c-block
                self.target["blocks"][substack_top_block]["parent"] = new_block[0]

                # Increase height by end of c-block
                self.stack_height += heights["c_end"]

            else: # Normal parse. Any block that isnt a c-block will be processed this way
                new_block = self._create_block(token_list["name"], func_args, prev_block, [comment, current_stack_height])
            
            if prev_block:
                prev_block[1]["next"] = new_block[0] # Update the previous block's "next" attribute
            elif not substack:
                new_block[1]["topLevel"] = True # Update the current block's "topLevel" attribute to be top-level if it has no parents

            # Save the block, and update the previous block
            self.target["blocks"][new_block[0]] = new_block[1]
            if cur_line == top_idx and substack: # Log if it is the top of the stack and is part of a substack
                top_id = new_block[0]
            prev_block = new_block

            # Update line_num
            line_num += 1
            self.line += 1

        if substack:
            error_handler.log("Substack: " + top_id + str(lines[0]))
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
            self.itr = 0 if self.argument_limit == 0 else 1 # Make sure that extension_stack blocks start with 1 iteration forwards, because they can handle 1 extra depth without changing height

        if args == "": # No argument blocks
            return []
        if isinstance(args, str):
            args = [args]
        
        args = [arg for arg in args if not arg == ""]
        return_args = [] # 2d list of arguments [type, relavent_data]

        def _check_width(arg_width, extra=0):
            """
            Checks if the width of the argument is greater than a threshold.
            If it is, then adds some width to the stack width.
            """
            arg_width += extra
            if arg_width > 14:
                self.stack_width += arg_width * 1.4 - 14

        for arg in args:
            # Find width of argument using helvitica neue font. If it exceeds a threshold, then add some width
            font = ImageFont.truetype("references\HelveticaNeue.ttf", 12)
            width = font.getbbox(arg)
            width = width[2] - width[0]

            # Parse argument
            if arg.startswith("$"):
                _check_width(width, 10)
                var_name = arg[1:]
                return_args.append(["variable", [var_name, self._read_variable(var_name)]])
                if itr <= self.argument_limit: # Increase the stack height if it is greater than the limit
                    self.stack_height += 0 # First recursion level is always 0 for stack, for ext_stack it is always 0 for the first two
                elif itr > self.itr: # Recursion depth has not been reached before
                    error_handler.log("Increasing stack height: " + arg + " at depth: " + str(itr) + " with limit: " + str(self.itr))
                    self.itr += 1
                    self.stack_height += 8 # Increase the stack height
            elif arg.startswith("@"):
                _check_width(width, 10)
                list_name = arg[1:]
                return_args.append(["list", [list_name, self._read_list(list_name)]])
            elif arg.startswith('"'):
                _check_width(width)
                return_args.append(["str", arg[1:-1]])
            elif self._is_num(arg):
                _check_width(width)
                return_args.append(["num", arg])
            elif "(" in arg and ")" in arg:
                self.stack_width += 100 # Increase width of stack
                if itr <= self.argument_limit: # Increase the stack height if it is greater than the limit
                    self.stack_height += 0 # First recursion level is always 0 for stack, for ext_stack it is always 0 for the first two
                elif itr > self.itr: # Recursion depth has not been reached before
                    error_handler.log("Increasing stack height: " + arg + " at depth: " + str(itr))
                    self.itr += 1
                    self.stack_height += 8 # Increase the stack height
                # Create a new stack block with its relavent data
                func_pieces = self._extract(arg)
                simplified_args = self._simplify_args(func_pieces["args"], line_num, itr + 1)
                func = self._create_block(func_pieces["name"], simplified_args)
                self.target["blocks"][func[0]] = func[1]

                return_args.append(["reporter", func]) # Return the block
            else:
                error_handler.add_error("Invalid argument type",arg,self.line)

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
        - comment (list | None): The comment for the block
            - [0]: The comment for the block
            - [1]: The height at which to place the block
        
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
            if comment[0]:
                block["comment"] = self._create_comment(comment[0], block_id, comment[1])

        # If block is not a reporter, create x and y coordinates for it
        if data["type"] == "hat":
            block["x"] = self.stacks * self.stack_spacing
            block["y"] = 0

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
            error_handler.add_error(f"Invalid number of arguments. '{name}' expects [{len(fill_args)}] arguments, but got [{len(args)}]", args, self.line)
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
                    error_handler.add_error(f"Invalid input argument type. Expected 'boolean', got '{arg[0]}'", fill_arg, self.line)
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

        #print(block_id, block)
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