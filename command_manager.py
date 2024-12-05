"""
Manages commands file
"""

def read_commands():
    with open("commands.txt", "r") as f:
        commands = f.readlines()
        found_commands = []

        for command in commands:
            if command.startswith("#") or command == "\n": # Ignore commented lines
                    continue
           
            command = command.strip() # Remove leading and trailing whitespaces
            found_commands.append(command)

        f.close()

    return found_commands

def read_by_opcode(opcode):
    found_commands = read_commands()
    attributes = ["name","opcode","type","inputs"]
    command_found = [cmd.split(":") for cmd in found_commands if cmd.split(":")[1] == opcode]

    return_dict = {}
    for attribute, value in zip(attributes, command_found[0]):
          return_dict[attribute] = value

    return return_dict

def read_by_name(name):
    name = name.lower()
    found_commands = read_commands()
    attributes = ["name","opcode","type","inputs"]
    command_found = [cmd.split(":") for cmd in found_commands if cmd.split(":")[0].lower() == name]

    return_dict = {}
    for attribute, value in zip(attributes, command_found[0]):
          return_dict[attribute] = value

    return return_dict

# print(read_by_opcode("motion_glidesecstoxy"))