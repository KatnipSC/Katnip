"""
Manages commands file
"""

def read_commands() -> list[str]:
    """
    Reads through and gets all the commands from the commands file (and preprocess and returns a neat list of commands)

    Returns:
    - found_commands (list[str]): Cleaned list of commands
    """

    with open("references\commands.txt", "r") as f:
        commands = f.readlines()
        found_commands = []

        for command in commands:
            if command.startswith("#") or command == "\n": # Ignore commented lines
                continue
            
            command = command.strip() # Remove leading and trailing whitespaces
            if "{" in command: # Ignore the metadata for the command. This is primarily for future hinting when writing code
                command = command.split("{")[0] + command.split("}")[1]
            found_commands.append(command)

        f.close()

    return found_commands

def read_by_opcode(opcode: str) -> dict:
    """
    Returns a dictionary of attributes about a command given its opcode

    Parameters:
    - opcode (str): OpCode of the command

    Returns:
    - return_dict (dict): Dictionary with command attributes
        - ["name"] (str): Name of the command
        - ["opcode"] (str): OpCode of the command
        - ["type"] (str): Type of the command
        - ["inputs"] (str): Input names of the command (separated by commas)
    """

    found_commands = read_commands()
    attributes = ["name","opcode","type","inputs"]
    command_found = [cmd.split(":") for cmd in found_commands if cmd.split(":")[1] == opcode]

    return_dict = {}
    for attribute, value in zip(attributes, command_found[0]):
          return_dict[attribute] = value

    return return_dict

def read_by_name(name: str):
    """
    Returns a dictionary of attributes about a command including:
    - name (str): Name of the command
    - opcode (str): OpCode of the command
    - type (str): Type of the command
    - inputs (str): Input names of the command (separated by commas)

    Parameters:
    - name (str): Name of the command (different than opCode)

    Returns:
    - return_dict (dict): Dictionary with command attributes [name,opcode,type,inputs]
    """
    
    name = name.lower()
    found_commands = read_commands()
    attributes = ["name","opcode","type","inputs"]
    command_found = [cmd.split(":") for cmd in found_commands if cmd.split(":")[0].lower() == name]

    if not command_found:
         return None

    return_dict = {}
    for attribute, value in zip(attributes, command_found[0]):
          return_dict[attribute] = value

    return return_dict

# print(read_by_opcode("motion_glidesecstoxy"))