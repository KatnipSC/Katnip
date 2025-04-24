"""
Main parsing logic for the code
"""

# File parsing
import json
import os
import tempfile
import shutil
import zipfile
import copy

# Asset details
from PIL import ImageFont, Image
import svgpathtools # type: ignore
import wave
from mutagen.mp3 import MP3

# Id's and md5ext fields
import base64
import hashlib
import uuid

# Custom packages
import command_manager
import error_handler
import hierarchy
import font_width

class project():
    def __init__(self):
        # Project specific setup
        self.id = uuid.uuid1() # Unique id for the project
        self.directory = tempfile.mkdtemp()
        os.makedirs(os.path.join("app_static", "generated_projects", str(self.id)))
        with open(os.path.join("app_static", "generated_projects", str(self.id), f"log_{self.id}.txt"), "w") as f: # Create log file
            f.write(f"Log file for project {self.id}\n")
            f.close()

        # Project block positioning
        self.stacks = 0
        self.stack_height = 0
        self.stack_width = 0
        self.stack_spacing = 600 # The x-tiling spacing between stacks
        self.comment_offset = 25 # The offset between the block + comment
        self.line = 0 # For tracking line numbers for error messages

        # Project json pieces
        self.procedures = {} # The list of custom procedures made within the project.
        self.curProc = "" # Currently evaluated procedure name for getting argument data
        self.procRequests = {} # Used to keep track of "orders" for proc data
        
        self.id_list = {} # The list to keep track of unique ID numbers for each type
        self.variables = dict() # List of all variables
        self.lists = dict() # List of all lists
        self.broadcasts = dict() # List of all broadcast
        self.monitors = list() # List of all monitors (variable/list monitors)

        # Project json setup
        self.data = {"targets": [],"monitors":[], "extensions": ["pen"], "meta": {"semver": "3.0.0", "vm": "5.0.40", "agent": "", "platform": {"name": "ScratchText", "url": "https://scratch.mit.edu/discuss/topic/769174/"}}} # TODO: change link to be the hosted ScratchText's website
        # Add stage to the project
        self.data["targets"].append({"isStage": True,
                                     "name": "Stage",
                                     "variables": {},
                                     "lists": {},
                                     "broadcasts": {},
                                     "blocks": {},
                                     "comments": {},
                                     "costumes": [],
                                     "sounds": [],
                                     "volume": 100,
                                     "layerOrder": 0,
                                     "tempo": 60,
                                     "videoTransparency": 50,
                                     "videoState": "on",
                                     "textToSpeechLanguage": None})
        
        self.sprite_template = {"isStage": False,
                                "name": "__placeholder__",
                                "variables": {},
                                "lists": {},
                                "broadcasts": {},
                                "blocks": {},
                                "comments": {},
                                "costumes": [],
                                "sounds": [],
                                "volume": 100,
                                "layerOrder": 1,
                                "visible": True,
                                "x": 0,
                                "y": 0,
                                "size": 100,
                                "direction": 90,
                                "draggable": False,
                                "rotationStyle": "all around"}
        
    def _extract(self, string: str):
        """
        Extracts name and arguments from a string (a line containing a function).

        ### Parameters:
        - string (str): The string of the line containing the relavent function

        ### Returns:
        - pieces (dict): A dictionary containing the name and arguments of the function
            - ["name"] (str): The name of the function
            - ["args"] (list): A list of arguments for the function
        """

        pieces = {}
        pieces["name"] = string.split("(")[0]

        args_string = string[string.find("(") + 1 : string.rfind(")")]
        args = []
        current_arg: list[str] = []
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

        ### Parameters:
        - text (str): The text to remove whitespace from

        ### Returns:
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

        ### Parameters:
        - value (str): The value to check

        ### Returns:
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

        ### Parameters:
        - arg (str | None): optional, is added to the unique ID's name to denote certain aspects.
            (e.g. "var" or "broadcast", etc.)

        ### Returns:
        - str: The unique ID
        """

        if not arg:
            arg = "block"
        if arg in self.id_list:
            self.id_list[arg] += 1
        else:
            self.id_list[arg] = 1
        
        my_id = self.id_list[arg]
        return f"{arg}-{my_id}"
       
    def _read_variable(self, name: str):
        """
        Returns the id of a variable. Creates the variable + monitor if it does not exist.

        ### Parameters:
        - name (str): The name of the variable

        ### Returns:
        - str: The id of the variable
        """

        if not name in self.variables:
            self.variables[name] = self._generate_id(arg="var")
            self.monitors.append({
                "id": self.variables[name],
                "mode": "default",
                "opcode": "data_variable",
                "params": {"VARIABLE": name},
                "spriteName": None,
                "value": 0,
                "x": 5,
                "y": 5 + len(self.monitors) * 27,
                "width": 0,
                "height": 0,
                "visible": False,
                "sliderMin": 0,
                "sliderMax": 100,
                "isDescrete": True
            })
        return self.variables[name]
    
    def _read_list(self, name: str):
        """
        Returns the id of a list. Creates the list if it does not exist.

        ### Parameters:
        - name (str): The name of the list

        ### Returns:
        - str: The id of the list
        """

        if not name in self.lists:
            self.lists[name] = self._generate_id(arg="list")
        return self.lists[name]
    
    def _read_broadcast(self, name: str):
        """
        Returns the id of a broadcast. Creates the broadcast if it does not exist.

        ### Parameters:
        - name (str): The name of the broadcast

        ### Returns:
        - str: The id of the broadcast
        """

        if not name in self.broadcasts:
            self.broadcasts[name] = self._generate_id(arg="broadcast")
        return self.broadcasts[name]
    
    def _read_procedure(self, name: str, args: list = [], warp: str = "false", definition: bool = False, call_args: dict = {}):
        """
        Returns the details of a custom procedure. Creates the procedure if it does not exist.

        Example call:
        _read_procedure("myProcedure", [{"name": "myArgument", "type": "bool"}, {"name": "anotherArgument", "type": "exp"}], warp="true", definition="true")
        or
        _read_procedure("myProcedure")
        
        ### Parameters:
        - name (str): The procedure name to be created/read
        - args (list): (optional) The arguments for the procedure containing dictionaries for arguments:
            - arg (dict): The arguments for the procedure
                - arg["name"]: The name for the argument
                - arg["type"]: The type of the argument (bool, or exp)
        - warp = "false": (optional) Whether the procedure is a warp procedure or not
        - definition (bool): (optional) Whether the procedure is being defined or not (allows func to be used before definition)
        - call_args (dict): (optional) The arguments for the procedure if a promise is required (i.e. procedure has not been defined yet)
            - call_args["id"] (str): (optional) The id for the procedure call block to update
            - call_args["arg_vals" (dict): (optional) The arguments for the procedure call block (if needed for a procedure promise)

        ### Returns:
        - details (dict): The details of the procedure
            - details["defined"]: Whether the procedure is defined or not
            - details["proccode"]: The code for the procedure
            - details["argumentids"]: The ids of the arguments for the procedure
            - details["argumentnames"]: The names of the arguments for the procedure
            - details["argumenttypes"]: The types of the arguments for the procedure
            - details["warp"]: Whether the procedure is a warp procedure or not
        """
        
        if definition:
            error_handler.log(self.id, f"🧱🌎 - Procedure '{name}' is being defined")
        else:
            error_handler.log(self.id, f"🧱🙏 - Procedure '{name}' is being read")

        if r"%d" in name or r"%s" in name:
            error_handler.add_error(f"⁉️🧩 - Invalid function name '{name}' because of string sequence '{'%d' if '%d' in name else '%s'}'",name,self.line)
            error_handler.throw_errors(self.id)

        if not name in self.procedures: # If procedure has not been documented yet:
            argumentids = [self._generate_id(arg="procArg") for _ in args]
            argumentnames = [arg["name"] for arg in args]

            proccode = ""
            argumenttypes = []
            argumentdefaults = []
            if definition: # If procedure is being defined, and hasn't been documented yet, set up argument types, proccode, and types
                argumenttypes = [arg["type"] for arg in args]
                proccode = name
                for arg in args:
                    if arg["type"] == "bool":
                        proccode += f" %b"
                        argumentdefaults.append("false")
                    elif arg["type"] == "exp":
                        proccode += f" %s"
                        argumentdefaults.append("")
                    else:
                        error_handler.add_error(f"⁉️🧩 - Unexpected argument type '{arg['type']}' for procedure '{name}'", name, self.line)
                        error_handler.throw_errors(self.id)
                        
            else:
                # If the proc is being read, but has not been documented yet, create a request
                if name in self.procRequests:
                    self.procRequests[name].append(call_args)
                else:
                    self.procRequests[name] = [call_args]
            
            self.procedures[name] = {"defined": definition, 
                                    "proccode": proccode.strip(),
                                    "argumentids": argumentids,
                                    "argumentnames": argumentnames,
                                    "argumenttypes": argumenttypes,
                                    "argumentdefaults": argumentdefaults,
                                    "warp": warp}
            
        elif definition: # If the proc is being defined, but has been used before, correct: proccode, argumenttypes, warp
            argumenttypes = [arg["type"] for arg in args]
            proccode = name
            argumentdefaults = []
            for arg in args:
                if arg["type"] == "bool":
                    proccode += f" %b"
                    argumentdefaults.append("false")
                elif arg["type"] == "exp":
                    proccode += f" %s"
                    argumentdefaults.append("")
                else:
                    error_handler.add_error(f"⁉️🧩 - Unexpected argument type '{arg['type']}' for procedure '{name}", name, self.line)
                    error_handler.throw_errors(self.id)

            # Correct values
            self.procedures[name]["defined"] = True
            self.procedures[name]["proccode"] = proccode
            self.procedures[name]["argumenttypes"] = argumenttypes
            self.procedures[name]["argumentdefaults"] = argumentdefaults
            self.procedures[name]["warp"] = warp
            
            # Correct any orders for this procedure
            if name in self.procRequests:
                for data in self.procRequests[name]:
                    # Get data about procedure promise
                    id = data["id"]
                    arg_vals = data["arg_vals"]
                    
                    # Log promise information
                    error_handler.log(self.id, f"🧩🛠️ - Fixing proccall '{id}' for proc '{name}'")
                    
                    # Execute promise for information about procedure
                    self.target["blocks"][id]["mutation"]["proccode"] = proccode
                    self.target["blocks"][id]["mutation"]["argumentdefaults"] = argumentdefaults
                    self.target["blocks"][id]["mutation"]["warp"] = warp
                    self.target["blocks"][id]["mutation"]["argumentids"] = str(self.procedures[name]["argumentids"]).replace("'", '"')
                    
                    proc = self.procedures[name]                    
                    self.target["blocks"][id]["inputs"] = {arg_block: self.format_args(self._simplify_args(arg_vals[arg_name])[0], type) for arg_block, arg_name, type in zip(proc["argumentids"], proc["argumentnames"], proc["argumenttypes"])}

        return self.procedures[name]
    
    # Func for formatting arguments
    def format_args(self, arg, type):
        boolean = type == "bool"
        match arg[0]:
            case "str":
                return [1, [10, arg[1]]]
            case "num":
                return [1, [4, arg[1]]]
            case "variable":
                return [3, [12, arg[1][0], arg[1][1]], [10, "❤️"]]
            case "list":
                return [3, [13, arg[1][0], arg[1][1]], [10, "❤️"]]
            case "reporter":
                return [3, arg[1][0], [10, "❤️"]] if not boolean else [2, arg[1][0]]
    
    def _process_procDef(self, name, args, comment):
        """
        Process a procedure definition

        ### Parameters:
        - name (str): The name of the procedure to be defined
        - args (list): The arguments for the procedure
        - comment (str): The comment for the procedure
        """
        
        # Log procDef call
        error_handler.log(self.id, f"🧱🫸 - Procedure definition of '{name}' with arguments '{args}' is being defined ...")

        # Set up current procedure for argument handling
        self.curProc = name

        # Set up position
        x = self.stacks * self.stack_spacing

        processed_args = [] # For storing processed arguments
        
        # Validify warp argument
        if not args[0][5:] in ["false", "true"]:
            error_handler.add_error(f"⁉️🧩 - Invalid warp argument '{args[0]}' for procedure definition of '{name}'", name, self.line)
            error_handler.throw_errors(self.id)
          
        # Process arguments  
        for arg in args[1:]: # First argument for determining warp or not for proc
            # Validify type of argument
            if not "[" in arg:
                error_handler.add_error(f"⁉️🧩 - '[' not found for argument '{arg}' for procedure definition of '{name}'", name, self.line)
                error_handler.throw_errors(self.id)
            if not "]" in arg:
                error_handler.add_error(f"⁉️🧩 - ']' not found for argument '{arg}' for procedure definition of '{name}'", name, self.line)
                error_handler.throw_errors(self.id)
            
            argType = arg[arg.rfind("[")+1:arg.rfind("]")]
            argName = arg[:arg.rfind("[")]
            processed_args.append({"name": argName, "type": argType})

        # Create/correct procedure
        proc = self._read_procedure(name, processed_args, args[0][5:], definition=True)

        # Create definition block
        block_id = self._generate_id() # Create id
        block = {
            "opcode": "procedures_definition",
            "next": None,
            "parent": None,
            "inputs": {"custom_block": [1, None]},
            "fields": {},
            "shadow": False,
            "topLevel": True,
            "x": x,
            "y": 0
        }

        # Create proc prototype block
        proto_id = self._generate_id() # Create id for proc prototype
        block["inputs"] = {"custom_block": [1, proto_id]} # Update input

        # Create proc argument blocks
        arg_blocks = {self._generate_id(): {"opcode": "argument_reporter_" + "string_number" if type == "exp" else "boolean",
                                            "next": None,
                                            "parent": proto_id,
                                            "inputs": {},
                                            "fields": {"VALUE": [name, None]},
                                            "shadow": True,
                                            "topLevel": False}
                                                for type, name in zip(proc["argumenttypes"], proc["argumentnames"])}
        
        # Create proto block
        proto_block = {
            "opcode": "procedures_prototype",
            "next": None,
            "parent": block_id,
            "inputs": {id: [1, arg_block] for arg_block, id in zip(arg_blocks, proc["argumentids"])},
            "fields": {},
            "shadow": True,
            "topLevel": False,
            "mutation": {
                "tagName": "mutation",
                "children": [],
                "proccode": proc["proccode"],
                "argumentids": str(proc["argumentids"]).replace("'", '"'),
                "argumentnames": str(proc["argumentnames"]).replace("'", '"'),
                "argumentdefaults": str(proc["argumentdefaults"]).replace("'", '"'),
                "warp": proc["warp"]
            }
        }

        # Save all blocks into target["blocks"]
        self.target["blocks"][block_id] = block
        for arg_block in arg_blocks:
            self.target["blocks"][arg_block] = arg_blocks[arg_block]
        self.target["blocks"][proto_id] = proto_block

        # Return [hat id, json_data] for defining hat block
        return [block_id, block]

    def _process_procCall(self, name, args, comment, prev_block_id):
        """
        Process a procedure call

        ### Parameters:
        - name (str): The name of the procedure to be called
        - args (list): The arguments for the procedure
        - comment (str): The comment for the procedure
        - prev_block_id (str): The previous block's id
        """

        processed_args = [] # Processed arguments
        arg_vals = {} # Dictionary for storing arguments' values
        for arg in args:
            # Validify format of argument --> argName:value
            if not ":" in arg:
                error_handler.add_error(f"⁉️🧩 - No value/argument name provided. ':' not found for argument '{arg}' for procedure call of '{name}'", name, self.line)
                error_handler.throw_errors(self.id)
            
            argValue = arg[arg.rfind(":")+1:]
            argName = arg[:arg.rfind(":")]
            processed_args.append({"name": argName})

            arg_vals[argName] = argValue

        # Create call block id
        call_id = self._generate_id() # Create id
        
        # Create/read procedure
        proc = self._read_procedure(name, processed_args, definition=False, call_args={"id": call_id, "arg_vals": arg_vals})

        # Create proc argument blocks
        arg_blocks = {self._generate_id(): {"opcode": "argument_reporter_" + "string_number" if type == "exp" else "boolean",
                                            "next": None,
                                            "parent": call_id,
                                            "inputs": {},
                                            "fields": {"VALUE": [name, None]},
                                            "shadow": True,
                                            "topLevel": False}
                                                for type, name in zip(proc["argumenttypes"], proc["argumentnames"])}

        self.argument_limit = 0 # Argument limit for resizing

        # Create call block
        call_block = {
            "opcode": "procedures_call",
            "next": None,
            "parent": prev_block_id,
            "inputs": {arg_block: self.format_args(self._simplify_args(arg_vals[arg_name])[0], type) for arg_block, arg_name, type in zip(proc["argumentids"], proc["argumentnames"], proc["argumenttypes"])},
            "fields": {},
            "shadow": False,
            "topLevel": False,
            "mutation": {
                "tagName": "mutation",
                "children": [],
                "proccode": proc["proccode"],
                "argumentids": str(proc["argumentids"]).replace("'", '"'),
                "warp": proc["warp"]
            }
        }

        # Save blocks
        for arg_block in arg_blocks:
            self.target["blocks"][arg_block] = arg_blocks[arg_block]
        self.target["blocks"][call_id] = call_block

        # Return [hat id, json_data] for next block to reference
        return [call_id, call_block]
    
    def _create_comment(self, comment: str, block_id: str, height=None):
        """
        Returns the id of a comment. Creates the comment if it does not exist

        ### Parameters:
        - comment (str): The comment to add
        - block_id (str): The id of the block that the comment is attached to
        - height (int | None): The y-position of the comment, defaults to self.stack_height

        ### Returns:
        - str: The id of the comment
        """

        offset = 15 # There is an offset between the middle of the block, and where the comment connects to the block
        comment_id = self._generate_id(arg="comment")
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

        ### Parameters:
        - text (str): The line of code containing a comment

        ### Returns:
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

        ### Parameters:
        - line (str): The line of code to check for an else statement

        ### Returns:
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
        It will make sure that the character is not within a string.

        ### Parameters:
        - line (str): The line of code to check for the character
        - char (str): The character to look for

        ### Returns:
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
    
    def _getWav(self, filepath):
        """
        Gets the WAV file data from the specified path.

        ### Parameters:
        - filepath (str): The path to the WAV file

        ### Returns:
        - data (tuple): The WAV file data
            - data[0]: Sample count
            - data[1]: Sample rate
        """

        with wave.open(filepath, 'rb') as wav_file:
            # Get the sample rate (fps)
            sample_rate = wav_file.getframerate()
            
            # Get the number of frames (samples)
            sample_count = wav_file.getnframes()

        return sample_count, sample_rate
    
    def _getMp3(self, filepath):
        """
        Gets the MP3 file data from the specified path.

        ### Parameters:
        - filepath (str): The path to the MP3 file

        ### Returns:
        - data (tuple): The MP3 file data
            - data[0]: Sample count
            - data[1]: Sample rate
        """

        audio = MP3(filepath)
        sample_rate = audio.info.sample_rate
        duration = audio.info.length
        sample_count = int(sample_rate * duration) # Estimate but eh

        return sample_count, sample_rate
    
    def _saveDataUrl(self, data_url):
        """
        Saves the data url to the specified path.

        ### Parameters:
        - data_url (str): The URL of the data to be saved
        - path (str): The path where the data should be saved
        """

        # Extract stuff from the data url
        header, encoded = data_url.split(",", 1)
        mime_type = header.split(";")[0].split(":")[1]

        # Get mime ext
        mime_conversion = {
            "image/jpeg": "jpg",
            "image/png": "png",
            "image/svg+xml": "svg",
            "audio/mpeg": "mp3",
            "audio/wav": "wav"
        }
        file_ext = mime_conversion.get(mime_type, "bin")

        # Decode b64 data
        data = base64.b64decode(encoded)

        # Hash the data MD5
        md5_hash = hashlib.md5(data).hexdigest()

        # Create and return file path
        file = f'{md5_hash}.{file_ext}'

        # Set up file path
        file_path = os.path.join(self.directory, file)

        # Create file
        with open(file_path, "wb") as f:
            f.write(data)

        match file_ext:
            case ext if ext in ["png", "jpg"]:
                image = Image.open(file_path)
                center = (image.width // 2, image.height // 2)
                return md5_hash, file_ext, center
            case "svg":
                paths, attributes = svgpathtools.svg2paths(file_path)
                bbox = paths[0].bbox()
                center_x = (bbox[0] + bbox[2]) / 2
                center_y = (bbox[1] + bbox[3]) / 2
                return md5_hash, file_ext, (center_x,center_y)
            case "mp3":
                return md5_hash, file_ext, self._getMp3(file_path)
            case "wav":
                return md5_hash, file_ext, self._getWav(file_path)
            case _:
                error_handler.add_error(f"Unsupported file type: '{file_ext}'", file_ext, -1)
                error_handler.throw_errors(self.id)

    def process_scrtxt(self, content: dict):
        """
        Parses the Scrtxt content and adds it to the program.

        ### Parameters:
        - content (dict): The Scrtxt content to be parsed {spriteName: content, sprite2Name: content, etc.}
            - content[0] (str): The code for the sprite
            - content[1] (list): The costumes for the sprite [[name,dataUrl],[name,dataUrl]]
            - content[2] (list): The sounds for the sprite [[name,dataUrl],[name,dataUrl]]
        """

        for sprite_name, sprite_content in content.items():
            if not sprite_name == "Stage":
                # Create a new sprite
                new_sprite = self.sprite_template
                new_sprite["name"] = sprite_name
                self.data["targets"].append(new_sprite)

            # Process the code for the sprite
            self._add_sprite_scripts(sprite_name, sprite_content[0]) # Make sure to process the assets for the current sprite

            # Make sure all procedures used were all defined
            for procedure in self.procedures:
                if not self.procedures[procedure]["defined"]:
                    error_handler.add_error(f"❓🤷‍♂️ - Procedure '{procedure['name']}' not defined.", procedure, -1)
            error_handler.throw_errors(self.id)

            # Processthe sprite's costumes (if given)
            if len(sprite_content) > 1:
                costumes = sprite_content[1]
                for costume in costumes:
                    error_handler.log(self.id, f"👕 - Processing costume: '{costume[0]}' for sprite: '{sprite_name}'")
                    asset_data = self._saveDataUrl(costume[1])
                    self.data["targets"][-1]["costumes"].append({
                        "name": costume[0],
                        "bitmapResolution": 1,
                        "dataFormat": asset_data[1],
                        "assetId": asset_data[0],
                        "md5ext": asset_data[0] + "." + asset_data[1],
                        "rotationCenterX": asset_data[2][0],
                        "rotationCenterY": asset_data[2][1]
                    })

            # Process the sprite's sounds (if given)
            if len(sprite_content) > 2:
                sounds = sprite_content[2]
                for sound in sounds:
                    error_handler.log(self.id, f"🔊 - Processing sound: '{sound[0]}' for sprite: '{sprite_name}'")
                    asset_data = self._saveDataUrl(sound[1])
                    self.data["targets"][-1]["sounds"].append({
                        "name": sound[0],
                        "assetId": asset_data[0],
                        "md5ext": asset_data[0] + "." + asset_data[1],
                        "dataFormat": asset_data[1],
                        "format": "",
                        "rate": asset_data[2][1],
                        "sampleCount": asset_data[2][0]
                    })

        # Add all monitors into the program
        self.data["monitors"] = self.monitors

        # Add global stuff to stage
        for variable in self.variables:
            variable_id = self.variables[variable]
            self.data["targets"][0]["variables"][variable_id] = [variable, "0"]

        # Process the generated lists
        for list_name in self.lists:
            list_id = self.lists[list_name]
            self.data["targets"][0]["lists"][list_id] = [list_name,[]]

        # Process the generated broadcasts
        for broadcast_name in self.broadcasts:
            broadcast_id = self.broadcasts[broadcast_name]
            self.data["targets"][0]["broadcasts"][broadcast_id] = broadcast_name
    
    def _add_sprite_scripts(self, target: str, program: str):
        """
        Adds sprite scripts to the specified target, parsing through program.

        ### Parameters:
        - target (str): The name of the target (e.g. "S1" or "Sprite1" or "Stage")
        - program (str | list): The program to parse and add to the target
        """

        # Parse through the program
        existing_target = [sprite for sprite in self.data["targets"] if sprite["name"] == target][0]
        idx = self.data["targets"].index(existing_target)
        self.target = existing_target
        self.line = 0 # Set line num to 0 (reset line counter)
        self._parse(program.split("\n"))

        self.data["targets"][idx] = self.target
                
    def _parse(self, lines: list, substack=False, depth=0):
        """
        Parses the given lines and adds them to self.target (current target)
            Will return a string ID of the topmost block if it is a substack for provessing substacks

        ### Parameters:
        - lines (list): The list of lines to parse
        - substack (bool): Whether this is a substack (used for parsing nested c blocks)
        - depth (int): The current depth of the parsing (used for indented c blocks)

        ### Returns:
        - top_id (str | None): The ID of the topmost block [IF] it is a substack for processing substacks
        """

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
                    self.curProc = "" # Reset current procedure
                    continue

            if self._extract_comment(lines[line_num])[0].strip() == "}":
                line_num += 1
                continue

            # Setup line counter and line value
            line = lines[line_num]
            cur_line = line_num

            # Remove comments (if they exist)
            line, comment = self._extract_comment(line) # Will return (line, None) if a comment is not found

            # Log line
            error_handler.log(self.id, f"〰️ - [{self.line}] On line: " + line)

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

            # Process function calls
            if(token_list["name"].startswith("fn.",)):
                token_list["name"] = token_list["name"][3:] # Remove "fn."
                if prev_block:
                    block = self._process_procCall(token_list["name"], token_list["args"], comment, prev_block[0]) # Process block
                    prev_block[1]["next"] = block[0]
                else:
                    block = self._process_procCall(token_list["name"], token_list["args"], comment, None) # Process block
                    self.target["blocks"][block[0]]["toplevel"] = True
                    
                # Embed into the rest of the blocks
                prev_block = block
                if cur_line == top_idx and substack:
                    top_id = block[0]
                line_num += 1
                continue

            if(token_list["name"].startswith("func:")):
                token_list["name"] = token_list["name"][5:] # Remove "func:"
                prev_block = self._process_procDef(token_list["name"], token_list["args"], comment) # Process block
                line_num += 1
                continue

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
                error_handler.throw_errors(self.id)

            # Get current stack height before adding inside tokens (to help c-blocks find where their comments should go)
            current_stack_height = self.stack_height # Get height BEFORE parsing arguments, so we can later add half of the height

            if len(token_list["args"]) > 0: # Might have no arguments
                # Parse the arguments
                func_args = token_list["args"]
                func_args = self._simplify_args(func_args)

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
            # Create the block
            if token_type == "c": # C-blocks need to parse their substack blocks
                substack_blocks = []
                # line_num += 1 # Adjust for currently being processed c-block

                bracket_depth = 1  # To count brackets for closing braces in substack blocks (we set to 1 for openning braces skipped over)

                # Collect lines for parsing the substack
                while line_num + 1 < len(lines): # Repeat while line_num is within line number, current line is not blank, and not(ending thingy in current line, and bracket depth = 0 e.g. ending of current look)
                    # Get next line
                    line_num += 1

                    # Update depth
                    if self._check_char(lines[line_num], "{"):
                        bracket_depth += 1
                    if self._check_char(lines[line_num], "}"):
                        bracket_depth -= 1

                    error_handler.log(self.id, f"🥅 - Capturing line [{line_num+1}] for c-block: {lines[line_num]} (bracket depth: {bracket_depth}), {self._check_char(lines[line_num], '}')}")

                    # Check for else block
                    if self._check_else(lines[line_num]): # Else condition found
                        if bracket_depth == 1:
                            substack_blocks.append("else")
                            self.line += 1
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

                error_handler.log(self.id, "🥅🏆 - Captured blocks: " + str(substack_blocks))
                # Check if it is end of file without running into a closing }
                if line_num == len(lines) and not "}" in lines[line_num-1]:
                    error_handler.add_error("⁉️ - Unexpected end of code block. Expected '}'",lines[line_num-1], self.line)
                    error_handler.throw_errors(self.id)

                # Parse the substack into blocks
                substack_prev_block = prev_block  # Save current state of prev_block
                prev_block = []  # Reset for substack parsing
                substack2_top_block = ""
                if "else" in substack_blocks: # "else" will only exist for the current layer
                    else_location = substack_blocks.index("else") # Get the location of the else block
                    substack_top_block = self._parse(substack_blocks[:else_location], substack=True, depth=depth+1)  # Top block of the substack1
                    prev_block = []  # Reset for next substack parsing
                    self.stack_height += heights["c_end"] # Increment stack height for middle block of "if-else" block
                    substack2_top_block = self._parse(substack_blocks[else_location+1:], substack=True, depth=depth+1)  # Top block of the substack2
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
                new_block = self._create_block(token_list["name"], func_args, prev_block, [comment, current_stack_height - 5]) # Reduce by a little bit to account for a weird offset

                # Update the substack_top_block to have the parent be the c-block
                self.target["blocks"][substack_top_block]["parent"] = new_block[0]

                # Increase height by end of c-block
                self.stack_height += heights["c_end"]

                # Increase line height past }
                self.line += 1

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

        if substack:
            error_handler.log(self.id, "⏬ - I is a Substack: " + top_id + str(lines[0]))
            return top_id # Return the top block of the substack

    def _simplify_args(self, args: list | str, itr = 0):
        """
        Simplifies the arguments, parsing through recursively.

        ### Parameters:
        - args (list | str): The list of arguments to simplify
        - itr (int): Internal counter for recursion of reporters

        ### Returns:
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
            width = font_width.get_width(arg if not "a." in arg else arg[2:])

            # Parse argument
            if arg.startswith("$"):
                _check_width(width, 10)
                var_name = arg[1:]
                return_args.append(["variable", [var_name, self._read_variable(var_name)]])
                if itr > self.itr: # Recursion depth has not been reached before
                    error_handler.log(self.id, "🏢⬆️ - Increasing stack height: " + arg + " at depth: " + str(itr) + " with limit: " + str(self.itr))
                    self.itr += 1
                    self.stack_height += 8 # Increase the stack height
            elif arg.startswith("@"):
                _check_width(width, 10)
                list_name = arg[1:]
                return_args.append(["list", [list_name, self._read_list(list_name)]])
            elif arg.startswith("a."):
                _check_width(width, 10)
                reporter_name = arg[2:]
                info = self._read_procedure(self.curProc) # Get procedure info
                
                # Figure out if argument actually exists
                if not reporter_name in info["argumentnames"]:
                    error_handler.log(self.id, info["argumentnames"])
                    error_handler.add_error(f"Argument '{reporter_name}' does not exist in procedure '{self.curProc}'", arg, self.line)
                    error_handler.throw_errors(self.id)
                
                idx = info["argumentnames"].index(reporter_name) # Get index of argument
                type = info["argumenttypes"][idx] # Get type
                proc_arg = self._create_block(f"funcarg{type}", [["str", reporter_name]]) # Create the argument block
                
                self.target["blocks"][proc_arg[0]] = proc_arg[1] # Add the block to target
                return_args.append(["reporter", proc_arg]) # Return the block
            elif arg.startswith('"'):
                _check_width(width)
                return_args.append(["str", arg[1:-1]])
            elif self._is_num(arg):
                _check_width(width)
                return_args.append(["num", arg])
            elif "(" in arg and ")" in arg:
                self.stack_width += 100 # Increase width of stack
                if itr > self.itr: # Recursion depth has not been reached before
                    error_handler.log(self.id, "🏢⬆️ - Increasing stack height: " + arg + " at depth: " + str(itr))
                    self.itr += 1
                    self.stack_height += 8 # Increase the stack height
                # Create a new stack block with its relavent data
                func_pieces = self._extract(arg)
                simplified_args = self._simplify_args(func_pieces["args"], itr + 1)
                func = self._create_block(func_pieces["name"], simplified_args)

                self.target["blocks"][func[0]] = func[1] # Add the block to target
                return_args.append(["reporter", func]) # Return the block
            else:
                error_handler.add_error("Invalid argument type",arg,self.line)

        error_handler.throw_errors(self.id) # Will automatically check for any errors, and will raise all found errors
        return return_args

    def _create_block(self, name, args, prev=None, comment=None):
        """
        Creates a new block given its name and arguments

        ### Parameters:
        - name (str): The name of the block
        - args (list): The arguments for the block
        - prev (list): The previous block (if any)
            - [0]: The previous block's id
            - [1]: The previous block's data
        - comment (list | None): The comment for the block
            - [0]: The comment for the block
            - [1]: The height at which to place the block
        
        ### Returns:
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
        data = command_manager.read_by_name(name)
        error_handler.log(self.id, "👀 - Getting block: " + name)

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

        # Check for correct number of arguments
        if len(fill_args) != len(args):
            error_handler.add_error(f"🔢❌ - Invalid number of arguments. '{name}' expects [{len(fill_args)}] arguments, but got [{len(args)}]", args, self.line)
            error_handler.throw_errors(self.id)

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
                    error_handler.add_error(f"⁉️🧩Invalid input argument type. Expected 'boolean', got '{arg[0]}'", fill_arg, self.line)
                    error_handler.throw_errors(self.id)

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
                        block["inputs"][fill_arg] = [1, [4, arg[1]]]
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

        return block_id, block
    
    def write(self):
        """
        Writes the current project data to a file. Creates the SB3 file 'app_static/generated_projects/program_{self.id}.sb3'
        """
        
        # Create generated projects directory if it does not exist
        if not os.path.exists(os.path.join("app_static", "generated_projects")):
            os.mkdir(os.path.join("app_static", "generated_projects"))

        # Save json file to output as well (debug only)
        # with open(os.path.join("app_static", "generated_projects", f"{self.id}.json"), "w") as f:
        #     f.write(json.dumps(self.data))

        # Add json file to tempdir
        with open(os.path.join(self.directory, "project.json"), "w") as f:
            f.write(json.dumps(self.data))

        # Create hierarchy for project
        with open(os.path.join("app_static", "generated_projects", str(self.id), f"hierarchy_{self.id}.txt"), "w", encoding="utf-8") as f:
            f.write(hierarchy.gen_hierarchy(self.data))
        
        # Zip contents to sb3 folder
        with zipfile.ZipFile(os.path.join("app_static", "generated_projects", str(self.id), f"program_{self.id}.sb3"), "w", zipfile.ZIP_DEFLATED) as zipf:
            for root, _, files in os.walk(self.directory):
                for file in files:
                    zipf.write(os.path.join(root, file), os.path.relpath(os.path.join(root, file), self.directory))
        
        # Remove temp directory
        shutil.rmtree(self.directory)

        # Return created filename
        return f'program_{self.id}.sb3'
