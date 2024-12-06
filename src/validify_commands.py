"""
Code for validating the commands (ensuring proper formatting and syntax)
"""

import error_handler

def validify_commands():
    """
    Validates the commands (ensuring proper formatting and syntax)
    
    1. Checks if commands contain all needed arguments
    2. Checks if useName, opCode, and type are non-empty
    3. Checks if there are duplicate commands (or parameters)
    4. Throws an error if invalid commands exist
    """
    
    print(f"🔍 - Validating commands...")

    with open("references/commands.txt", "r") as f:
        commands = f.readlines() # Read file

        # Create list for checking duplicate commands (or parameters)
        all_names = [] # List of useName
        all_opcodes = [] # List of opCodes

        # Check if commands contain all needed arguments
        for line_num, command in enumerate(commands):
            line_num += 1 # Adjust for reading offset

            if command.startswith("#") or command == "\n": # Ignore commented lines
                continue

            command = command.strip("\n")
            command_parts = command.split(":") # Split by sep char

            # Check if command has 4 parts (useName:opCode:type:inputName1,inputName2, ...)
            if len(command_parts) < 4:
                error_handler.add_error(f"Invalid arguments length. Expected 4 parts, but received [{len(command_parts)}]", command, line_num)
                continue

            # Check if useName, opCode, and type are non-empty
            if command_parts[0] == "":
                error_handler.add_error(f"Invalid useName argument. Blank argument received.", command, line_num)
                continue
            if command_parts[1] == "":
                error_handler.add_error(f"Invalid opCode argument. Blank argument received.", command, line_num)
                continue
            if command_parts[2] == "":
                error_handler.add_error(f"Invalid useName argument. Blank argument received.", command, line_num)
                continue

            # Check if useName, opCode, and type are unique
            if command_parts[0] in all_names:
                error_handler.add_error(f"Duplicate useName found. ", command, line_num)
                continue
            if command_parts[1] in all_opcodes:
                error_handler.add_error(f"Duplicate opCode found. ", command, line_num)
                continue

            # Add useName and opCode to list of processed commands
            all_names.append(command_parts[0])
            all_opcodes.append(command_parts[1])


        # Raise exception if invalid commands exist
        error_handler.throw_errors()
        print("✅ - All commands are valid.")
        
validify_commands()