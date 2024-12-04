"""
Code for validating the commands (ensuring proper formatting and syntax)
"""

def validify_commands():
    with open("commands.txt", "r") as f:
        commands = f.readlines() # Read file

        # Create list for invalid commands
        invalid_commands = []

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
                print(f"❌ - Invalid arguments length in command [{command}] on line [{line_num}]\n")
                invalid_commands.append(command)
                continue

            # Check if useName, opCode, and type are non-empty
            if command_parts[0] == "":
                print(f"❌ - Invalid useName in command [{command}] on line [{line_num}]\n")
                invalid_commands.append(command)
                continue
            if command_parts[1] == "":
                print(f"❌ - Invalid opCode in command [{command}] on line [{line_num}]\n")
                invalid_commands.append(command)
                continue
            if command_parts[2] == "":
                print(f"❌ - Invalid type in command [{command}] on line [{line_num}]\n")
                invalid_commands.append(command)
                continue

            # Check if useName, opCode, and type are unique
            if command_parts[0] in all_names:
                print(f"❌ - Duplicate useName found [{command_parts[0]}] on line [{line_num}]\n")
                invalid_commands.append(command)
                continue
            if command_parts[1] in all_opcodes:
                print(f"❌ - Duplicate opCode found [{command_parts[1]}] on line [{line_num}]\n")
                invalid_commands.append(command)
                continue

            # Add useName and opCode to list of processed commands
            all_names.append(command_parts[0])
            all_opcodes.append(command_parts[1])


        # Raise exception if invalid commands exist
        if invalid_commands:
            raise ValueError(f"[{len(invalid_commands)}] invalid commands found. See above for details.")
        else:
            print("✅ - All commands are valid.")
        
validify_commands()