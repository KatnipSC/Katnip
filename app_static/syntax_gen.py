from colorsys import rgb_to_hls, hls_to_rgb

# Category colors
category_colors = {
    "motion": "4C97FF",
    "looks": "9966FF",
    "sound": "CF63CF",
    "events": "FFBF00",
    "control": "FFAB19",
    "sensing": "5CB1D6",
    "operators": "59C059",
    "variables": "FF8C1A",
    "lists": "FF661A",
    "pen": "0FBD8C"
}

# Define block types and brightness adjustments
block_types = {
    "hat": 0.8,
    "reporter": 1.2,
    "stack": 1.0,
    "c": 1.0,
    "cap": 1.0
}

# Function to adjust color brightness
def adjust_brightness(hex_color, factor):
    r = int(hex_color[0:2], 16) / 255.0
    g = int(hex_color[2:4], 16) / 255.0
    b = int(hex_color[4:6], 16) / 255.0
    h, l, s = rgb_to_hls(r, g, b)
    l = min(1, max(0, l * factor))
    r, g, b = hls_to_rgb(h, l, s)
    return f"{int(r * 255):02X}{int(g * 255):02X}{int(b * 255):02X}"

with open("app_static\\references\\commands.txt", "r") as file:
    writen_commandPatterns = []
    write_str = ""
    current_category = ""
    for line in file:
        line = line.strip()
        # Skip func
        if line.startswith("func"):
            continue
        # Check for a category marker
        if line.startswith("# NAME:"):
            current_category = line.split(":")[1].strip().lower()
        # Skip comments and blank lines
        elif line and not line.startswith("#") and current_category:
            # Extract command and type
            parts = line.split(":")
            command_type = parts[2] if len(parts) > 2 else "unknown"
            
            # Generate color based on category and block type
            base_color = category_colors.get(current_category, "FFFFFF")
            adjusted_color = adjust_brightness(base_color, block_types.get(command_type, 1.0))

            # Generate the command pattern
            css_chunk = f".{current_category}-{command_type}" + "{\n    " + f"color: #{adjusted_color};\n" + "}\n"

            # Add to dictionary
            if not f".cm-{current_category}-{command_type}" in writen_commandPatterns:
                writen_commandPatterns.append(f".cm-{current_category}-{command_type}")
                write_str += css_chunk

write_str += ".string" + "{\n    " + f"color: #d60b37;\n" + "}\n"
write_str += ".num" + "{\n    " + f"color: #d60b37;\n" + "}\n"
write_str += ".variable" + "{\n    " + f"color: #FF8C1A;\n" + "}\n"
write_str += ".list" + "{\n    " + f"color: #FF661A;\n" + "}\n"
write_str += ".comment" + "{\n    " + f"color: #E4DB8C;\n" + "}\n"
write_str += ".my_blocks-hat" + "{\n    " + f"color: #FF4D6A;\n" + "}\n"
write_str += ".my_blocks-stack" + "{\n    " + f"color: #FF7D9E;\n" + "}\n"
write_str += ".my_blocks-reporter" + "{\n    " + f"color: #FF3D4A;\n" + "}\n"

with open("app_static\\syntax.css", "w") as file:
    file.write(write_str)