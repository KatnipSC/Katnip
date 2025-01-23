import json

def generate_ascii_hierarchy(blocks, current_block_id=None, indent="", is_last=False):
    hierarchy = ""
     
    # If current block is not provided, assume it's the first one
    if not current_block_id:
        current_block_id = list(blocks.keys())[0]
    
    # Choose the connector based on whether this is the last item
    connector = "└─" if is_last else "├─"
    hierarchy += f"{indent}{connector} {current_block_id}: {blocks[current_block_id]['opcode']}\n"
    
    # New indent for children
    new_indent = indent + ("    " if is_last else "│   ")
    
    # Process inputs
    if blocks[current_block_id]["inputs"]:
        input_items = list(blocks[current_block_id]["inputs"].keys())
        input_length = len(input_items)
        for i, input_name in enumerate(input_items):
            if "SUBSTACK" in input_name:
                continue

            is_last_input = (i + 1 == input_length) and not blocks[current_block_id]["fields"]
            sub_connector = "└─" if is_last_input else "├─"
            input_value = blocks[current_block_id]["inputs"][input_name]

            if isinstance(input_value[1], list): # It is a value with type
                # Set up value types
                inputTable = {
                    4: "Number",
                    5: "Positive Number",
                    6: "Positive Integer",
                    7: "Integer",
                    8: "Angle",
                    9: "Color",
                    10: "String",
                    11: "Broadcast",
                    12: "Variable",
                    13: "List"
                }

                if len(input_value[1]) > 2: # It is a value such as variable, list, or broadcast
                    hierarchy += f"{new_indent}{sub_connector} {input_name} [{inputTable[input_value[1][0]]}] ({input_value[1][1]}): {input_value[1][2]}\n"
                else:
                    hierarchy += f"{new_indent}{sub_connector} {input_name} [{inputTable[input_value[1][0]]}]: {input_value[1][1]}\n"

            elif input_value[1] in blocks:  # It's a nested block
                hierarchy += f"{new_indent}{sub_connector} {input_name} [Reporter]:\n"
                hierarchy += generate_ascii_hierarchy(
                    blocks, input_value[1], new_indent + ("    " if is_last_input else "│   "), is_last=True # Set to True because argument will only contain 1 block
                )

    # Process fields
    if blocks[current_block_id]["fields"]:
        field_items = list(blocks[current_block_id]["fields"].keys())
        field_length = len(field_items)
        for i, field_name in enumerate(field_items):
            is_last_input = (i + 1 == field_length)
            sub_connector = "└─" if is_last_input else "├─"
            field_values = blocks[current_block_id]["fields"][field_name]

            hierarchy += f"{new_indent}{sub_connector} {field_name} ({field_values[0]}): {field_values[1]}\n"
    
    # Process substack
    if "SUBSTACK" in blocks[current_block_id]["inputs"]:
        substack_block_id = blocks[current_block_id]["inputs"]["SUBSTACK"][1]

        last = blocks[current_block_id]["next"] == None
        sub_connector = "└─" if is_last else "├─"
        hierarchy += f"{new_indent}{sub_connector} SUBSTACK:\n"
        hierarchy += generate_ascii_hierarchy(
            blocks, substack_block_id, new_indent + ("    " if last else "│   "), is_last=last
        )

    # If there is a 2nd substack parse it as well
    if "SUBSTACK2" in blocks[current_block_id]["inputs"]:
        substack_block_id = blocks[current_block_id]["inputs"]["SUBSTACK2"][1]

        last = blocks[current_block_id]["next"] == None
        sub_connector = "└─" if is_last else "├─"
        hierarchy += f"{new_indent}{sub_connector} SUBSTACK2:\n"
        hierarchy += generate_ascii_hierarchy(
            blocks, substack_block_id, new_indent + ("    " if last else "│   "), is_last=last
        )
    
    # Add next block if available
    if "next" in blocks[current_block_id] and blocks[current_block_id]["next"] is not None:
        next_block_id = blocks[current_block_id]["next"]
        hierarchy += generate_ascii_hierarchy(blocks, next_block_id, indent, is_last=is_last)
    
    return hierarchy

def gen_hierarchy(project_data):
    """
    Generate ASCII hierarchy from Scratch 3 project data.
    
    ### Parameters:
    - project_data (dict): Scratch 3 project data

    ### Returns:
    - hierarchy (str): ASCII hierarchy of the project data
    """

    hierarchy = ""

    # Iterate over all sprites
    for sprite in project_data["targets"]:
        hierarchy += f"{sprite["name"]} >\n"
        if sprite["blocks"]: # If blocks exist, parse em
            hierarchy += generate_ascii_hierarchy(sprite["blocks"])

    return hierarchy

# with open(r"app_static\generated_projects\project.json", "r", encoding="utf-8") as f:
#     data = json.load(f)
#     hierarchy = generate_ascii_hierarchy(data["targets"][1]["blocks"])

# with open(r"app_static\generated_projects\hierarchy.txt", "w", encoding="utf-8") as f:
#     f.write(hierarchy)