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
        
    def _tokenize(self):
        print("tbd")

    def _create_block(self, opcode, args):
        # Create a new ID for the block
        block_id = self._generate_id()

        # Create block template
        block = {
            "opcode": opcode,
            "parent": None,
            "next": None,
            "inputs": {},
            "fields": {},
            "shadow": False,
            "topLevel": False,
            "x": 0,
            "y": 0
        }

        # Get input parameters
        data = command_manager.read_by_opcode(opcode)
        fill_args = data["inputs"]
        fill_args = fill_args.split(",")

        # Input args
        for fill_arg, arg in zip(fill_args, args):
            if fill_arg.startswith("i."):
                block["inputs"][fill_arg[2:].upper()] = arg
            elif fill_arg.startswith("f."):
                block["fields"][fill_arg[2:].upper()] = arg

        return block_id, block