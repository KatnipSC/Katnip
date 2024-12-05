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

    def _is_num(self, value):
        for character in value:
            if not character in ["-",".","0","1","2","3","4","5","6","7","8","9"]:
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
       
    def _parse(self, lines):
        prev_block = []
        for line_num, line in enumerate(lines):
            token_list = line.replace(" ","") # remove whitespace
            token_type = ""

            token_type = "c" if "{" in token_list else "func"

            # Create details for the block
            func_name = token_list.split("(")[0]

            if len(token_list.split("(")) > 1: # Potentially might have no arguments. Len 1 --> name, no arguments
                # Parse the arguments
                func_args = token_list.split("(")[1][:-1]
                func_args = self._simplify_args(func_args, line_num)

            # Create the block
            new_block = self._create_block(func_name, func_args, prev_block)

            if prev_block:
                prev_block[1]["next"] = new_block[0] # Update the previous block's "next" attribute
            else:
                new_block[1]["topLevel"] = True # Update the current block's "topLevel" attribute to be top-level if it has no parents

            # Save the block, and update the previous block
            self.target["blocks"][new_block[0]] = new_block[1]
            prev_block = new_block

    def _simplify_args(self, args, line_num):
        args = args.split(",")
        return_args = [] # 2d list of arguments [type, relavent_data]
        invalid_args = []

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
                func_name = arg.split("(")[0]
                simplified_args = self._simplify_args(arg.split("(")[1][:-1], line_num)
                func = self._create_block(func_name, simplified_args)

                return_args.append(["reporter", func]) # Return the block
            else:
                print(f"❌ - Invalid argument type for argument [{arg}] on line [{line_num}]\n")
                invalid_args.append(arg)

        if invalid_args:
            raise ValueError(f"[{len(invalid_args)}] invalid arguments found. See above for details.")
        else:
            return return_args

    def _create_block(self, name, args, prev=None):
        # Create a new ID for the block
        block_id = self._generate_id()

        # Get data about block (input parameters)
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
        fill_args = fill_args.split(",")

        # Input args
        for fill_arg, arg in zip(fill_args, args):
            if fill_arg.startswith("i."):
                block["inputs"][fill_arg[2:].upper()] = arg
            elif fill_arg.startswith("f."):
                block["fields"][fill_arg[2:].upper()] = arg

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