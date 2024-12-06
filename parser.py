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
        self.CUR_ID = 0
        self.variables = dict()
        tmpdir = tempfile.mkdtemp()
        with zipfile.ZipFile(filename, "r") as zip_ref:
            zip_ref.extractall(tmpdir)
        with open(os.path.join(tmpdir, "project.json")) as f:
            self.data = json.loads(f.read())
        self.origin = filename
        shutil.rmtree(tmpdir)
    
    def _extract(self, string):
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

    def _is_num(self, value):
        if len(value) == 0:
            return False
        for character in value:
            if not character in "-.0123456789":
                return False
        return True

    def _generate_id(self, arg=None):
        self.CUR_ID += 1
        if arg:
            return f"scratchtext-{arg}-{self.CUR_ID}"
        else:
            return f"scratchtext-{self.CUR_ID}"
       
    def _read_variable(self, name):
        if not name in self.variables:
            self.variables[name] = self._generate_id(arg="var")
        return self.variables[name]
    
    def add_sprite_scripts(self, target, program):
        if isinstance(program, str):
            program = program.replace(" ","").split("\n")

        # Parse through the program
        for existing_target in self.data["targets"]:
            if existing_target["name"] == target:
                self.target = existing_target
                self._parse(program)

        # Add relavent variables
        for target in self.data["targets"]:
            if target["isStage"]:
                if "variables" not in target:
                    target["variables"] = dict()
                for variable in self.variables:
                    variable_id = self.variables[variable]
                    target["variables"][variable_id] = [variable, "0"]
       
    def _parse(self, lines, substack=False):
        print(lines)
        prev_block = []
        line_num = 0 # We are using a while loop with counter instead of for loop to account for c blocks with blocks inside "substack"
        top_id = ""
        while line_num < len(lines):
            if not substack: # Exiting hat block
                if "}" in lines[line_num]:
                    prev_block = []
                    line_num += 1
                    continue

            # Setup line counter and line value
            line = lines[line_num]

            # Parse line
            token_list = line.replace(" ","") # remove whitespace

            # Split string into name and arguments
            token_list = self._extract(token_list)

            if len(token_list["args"]) > 0: # Might have no arguments
                # Parse the arguments
                func_args = token_list["args"]
                func_args = self._simplify_args(func_args, line_num)
            else:
                # Make empty argument list
                func_args = []

            # Define type of block being processed
            token_type = command_manager.read_by_name(token_list["name"])
            if token_type:
                token_type = token_type["type"]
            else:
                error_handler.add_error(f"Invalid command '{token_list['name']}'", lines[line_num], line_num+1)
                error_handler.throw_errors()

            # Create the block
            if token_type == "c": # C-blocks need to parse their substack blocks
                substack_blocks = []
                line_num += 1 # Adjust for currently being processed c-block

                bracket_depth = 0 # Track the depth of the scanner
                # Collect lines for parsing the substack
                while (line_num < len(lines) and lines[line_num].strip()) and not ("}" in lines[line_num] and bracket_depth == 0):
                    if "{" in line[line_num]:
                        bracket_depth += 1
                    elif "}" in line[line_num]:
                        bracket_depth -= 1
                    substack_blocks.append(lines[line_num])
                    line_num += 1
                if line_num + 1 < len(lines): # Add last closing bracket
                    substack_blocks.append(lines[line_num])

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
                new_block = self._create_block(token_list["name"], func_args, prev_block)

                # Update the substack_top_block to have the parent be the c-block
                self.target["blocks"][substack_top_block]["parent"] = new_block[0]

            else: # Normal parse. Any block that isnt a c-block will be processed this way
                new_block = self._create_block(token_list["name"], func_args, prev_block)

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

    def _simplify_args(self, args, line_num):
        if args == "": # No argument blocks
            return []
        
        args = [arg for arg in args if not arg == ""]
        return_args = [] # 2d list of arguments [type, relavent_data]

        for arg in args:
            if arg.startswith("$"):
                var_name = arg[1:]
                return_args.append(["variable", [var_name, self._read_variable(var_name)]])
            elif arg.startswith('"'):
                return_args.append(["str/num", arg[1:-1]])
            elif self._is_num(arg):
                return_args.append(["str/num", arg])
            elif "(" in arg and ")" in arg:
                # Create a new stack block with its relavent data
                func_pieces = self._extract(arg)
                simplified_args = self._simplify_args(func_pieces["args"], line_num)
                func = self._create_block(func_pieces["name"], simplified_args)
                self.target["blocks"][func[0]] = func[1]

                return_args.append(["reporter", func]) # Return the block
            else:
                error_handler.add_error("Invalid argument type",arg,line_num+1)

        error_handler.throw_errors() # Will automatically check for any errors, and will raise all found errors
        return return_args

    def _create_block(self, name, args, prev=None):
        # Create a new ID for the block
        block_id = self._generate_id()

        # Get data about block (input parameters)
        #print("getting data about block:", name)
        data = command_manager.read_by_name(name)

        # Create block template
        block = {
            "opcode": data["opcode"],
            "parent": None,
            "next": None,
            "inputs": {},
            "fields": {},
            "shadow": False,
            "topLevel": False,
            "x": 0,
            "y": 0
        }

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
            error_handler.add_error(f"Invalid number of arguments. '{name}' expects [{len(fill_args)}] arguments", args, -1)
            error_handler.throw_errors()

        # Input args
        for fill_arg, arg in zip(fill_args, args):
            if fill_arg.startswith("i."):
                boolean = "[bool]" in fill_arg
                if boolean:
                    fill_arg = fill_arg[:fill_arg.find("[")]+fill_arg[fill_arg.find("]")+1:]
                if arg[0] == "str/num":
                    block["inputs"][fill_arg[2:].upper()] = [1, [10, arg[1]]]
                elif arg[0] == "variable":
                    block["inputs"][fill_arg[2:].upper()] = [3, [12, arg[1][0], arg[1][1]], [10, "❤️"]]
                elif arg[0] == "reporter":
                    self.target["blocks"][arg[1][0]]["parent"] = block_id
                    block["inputs"][fill_arg[2:].upper()] = [3, arg[1][0], [10, "❤️"]] if not boolean else [2, arg[1][0]]
                elif arg[0] == "substack":
                    block["inputs"][fill_arg[2:].upper()] = [2, arg[1]]
            elif fill_arg.startswith("f."):
                if arg[0] == "str/num":
                    block["fields"][fill_arg[2:].upper()] = [arg[1], None]
                elif arg[0] == "variable":
                    block["fields"][fill_arg[2:].upper()] = arg[1]

        print(block_id, block)
        return block_id, block
    
    def write(self, filename):
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
        shutil.rmtree(tmpdir)