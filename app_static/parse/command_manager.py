"""
Manages Katnip commands
"""

import error_handler
import os

# Change i. and f. to inputs and fields respectively
commands = {
    "internal": {
        "goto_menu": {
            "opcode": "motion_goto_menu",
            "type": "reporter",
            "args": ["f.to{_random_;_mouse_;...}"]
        },
        "glideto_menu": {
            "opcode": "motion_glideto_menu",
            "type": "reporter",
            "args": ["f.to{_random_;_mouse_;...}"]
        },
        "point_towards_menu": {
            "opcode": "motion_pointtowards_menu",
            "type": "reporter",
            "args": ["f.towards{_random_;_mouse_;...}"]
        },
        "costume_menu": {
            "opcode": "looks_costume",
            "type": "reporter",
            "args": ["f.costume{...}"]
        },
        "backdrop_menu": {
            "opcode": "looks_backdrops",
            "type": "reporter",
            "args": ["f.backdrop{...}"]
        },
        "sound_menu": {
            "opcode": "sound_sounds_menu",
            "type": "reporter",
            "args": ["f.sound_menu{...}"]
        },
        "clone_menu": {
            "opcode": "control_create_clone_of_menu",
            "type": "reporter",
            "args": ["f.clone_option"]
        },
        "touching_menu": {
            "opcode": "sensing_touchingobjectmenu",
            "type": "reporter",
            "args": ["f.touchingobjectmenu"]
        },
        "distance_menu": {
            "opcode": "sensing_distancetomenu",
            "type": "reporter",
            "args": ["f.distancetomenu"]
        },
        "key_menu": {
            "opcode": "sensing_keyoptions",
            "type": "reporter",
            "args": ["f.key_option"]
        },
        "sensingobj_menu": {
            "opcode": "sensing_of_object_menu",
            "type": "reporter",
            "args": ["f.object"]
        },
        "pen_menu": {
            "opcode": "pen_menu_colorParam",
            "type": "reporter",
            "args": ["f.colorParam"]
        }
    },
    "motion": {
        "move": {
            "opcode": "motion_movesteps", 
            "type": "stack", 
            "args": ["i.steps"]
        },
        "turn": {
            "opcode": "motion_turnright", 
            "type": "stack", 
            "args": ["i.degrees"]
        },
        "gotoxy": {
            "opcode": "motion_gotoxy", 
            "type": "stack", 
            "args": ["i.x", "i.y"]
        },
        "goto": {
            "opcode": "motion_goto", 
            "type": "stack", 
            "args": ["i.to(goto_menu)"]
        },
        "glideXY": {
            "opcode": "motion_glidesecstoxy", 
            "type": "stack", 
            "args": ["i.secs", "i.x", "i.y"]
        },
        "glideto": {
            "opcode": "motion_glideto", 
            "type": "stack", 
            "args": ["i.secs", "i.to(glideto_menu)"]
        },
        "point": {
            "opcode": "motion_pointindirection", 
            "type": "stack", 
            "args": ["i.direction"]
        },
        "pointTo": {
            "opcode": "motion_pointtowards", 
            "type": "stack", 
            "args": ["i.towards(point_towards_menu)"]
        },
        "changeX": {
            "opcode": "motion_changexby", 
            "type": "stack", 
            "args": ["i.dx"]
        },
        "setX": {
            "opcode": "motion_setx", 
            "type": "stack", 
            "args": ["i.x"]
        },
        "changeY": {
            "opcode": "motion_changeyby", 
            "type": "stack", 
            "args": ["i.dy"]
        },
        "setY": {
            "opcode": "motion_sety", 
            "type": "stack", 
            "args": ["i.y"]
        },
        "edgeBounce": {
            "opcode": "motion_ifonedgebounce", 
            "type": "stack", 
            "args": []
        },
        "rotationStyle": {
            "opcode": "motion_setrotationstyle", 
            "type": "stack", 
            "args": ["f.style{left-right;don't rotate;all around}"]
        },
        "xPos": {
            "opcode": "motion_xposition", 
            "type": "reporter", 
            "args": []
        },
        "yPos": {
            "opcode": "motion_yposition", 
            "type": "reporter", 
            "args": []
        },
        "direction": {
            "opcode": "motion_direction", 
            "type": "reporter", 
            "args": []
        }
    },
    "looks": {
        "timesay": {
            "opcode": "looks_sayforsecs", 
            "type": "stack", 
            "args": ["i.message", "i.secs"]
        },
        "say": {
            "opcode": "looks_say", 
            "type": "stack", 
            "args": ["i.message"]
        },
        "timethink": {
            "opcode": "looks_thinkforsecs", 
            "type": "stack", 
            "args": ["i.message", "i.secs"]
        },
        "think": {
            "opcode": "looks_think", 
            "type": "stack", 
            "args": ["i.message"]
        },
        "costume": {
            "costume": {
                "opcode": "looks_costumenumbername", 
                "type": "reporter", 
                "args": ["f.number_name{number;name}"]
            },
            "switch": {
                "opcode": "looks_switchcostumeto", 
                "type": "stack", 
                "args": ["i.costume(costume_menu)"]
            },
            "next": {
                "opcode": "looks_nextcostume", 
                "type": "stack", 
                "args": []
            },
        },
        "backdrop": {
            "backdrop": {
                "opcode": "looks_backdropnumbername", 
                "type": "reporter", 
                "args": ["f.number_name{number;name}"]
            },
            "switch": {
                "opcode": "looks_switchbackdropto", 
                "type": "stack", 
                "args": ["i.costume(backdrop_menu)"]
            },
            "next": {
                "opcode": "looks_nextbackdrop", 
                "type": "stack", 
                "args": []
            },
        },
        "size": {
            "size": {
                "opcode": "looks_size", 
                "type": "reporter", 
                "args": []
            },
            "change": {
                "opcode": "looks_changesizeby", 
                "type": "stack", 
                "args": ["i.change"]
            },
            "set": {
                "opcode": "looks_setsizeto", 
                "type": "stack", 
                "args": ["i.size"]
            },
        },
        "fx": {
            "change": {
                "opcode": "looks_changeeffectby", 
                "type": "stack", 
                "args": ["f.effect{color;fisheye;whirl;pixelate;mosaic;brightness;ghost}", "i.change"]
            },
            "set": {
                "opcode": "looks_seteffectto", 
                "type": "stack", 
                "args": ["f.effect{color;fisheye;whirl;pixelate;mosaic;brightness;ghost}", "i.value"]
            },
            "clear": {
                "opcode": "looks_cleargraphiceffects", 
                "type": "stack", 
                "args": []
            },
        },
        "show": {
            "opcode": "looks_show", 
            "type": "stack", 
            "args": []
        },
        "hide": {
            "opcode": "looks_hide", 
            "type": "stack", 
            "args": []
        },
        "goToLayer": {
            "opcode": "looks_gotofrontback", 
            "type": "stack", 
            "args": ["f.front_back{front;back}"]
        },
        "changeLayer": {
            "opcode": "looks_goforwardbackwardlayers", 
            "type": "stack", 
            "args": ["f.forward_backward{front;back}", "i.num"]
        },
    },
    "sound": {
        "play": {
            "opcode": "sound_play",
            "type": "stack",
            "args": ["i.sound_menu(sound_menu)"]
        },
        "playwait": {
            "opcode": "sound_playuntildone",
            "type": "stack",
            "args": ["i.sound_menu(sound_menu)"]
        },
        "stopall": {
            "opcode": "sound_stopallsounds",
            "type": "stack",
            "args": []
        },
        "fx": {
            "change": {
                "opcode": "sound_changeeffectby",
                "type": "stack",
                "args": ["i.effect{pitch;pan left/right}", "i.value"]
            },
            "set": {
                "opcode": "sound_seteffectto",
                "type": "stack",
                "args": ["i.effect{pitch;pan left/right}", "i.value"]
            },
            "clear": {
                "opcode": "sound_cleareffects",
                "type": "stack",
                "args": []
            },
        },
        "volume": {
            "volume": {
                "opcode": "sound_volume",
                "type": "reporter",
                "args": []
            },
            "change": {
                "opcode": "sound_changevolumeby",
                "type": "stack",
                "args": ["i.volume"]
            },
            "set": {
                "opcode": "sound_setvolumeto",
                "type": "stack",
                "args": ["i.volume"]
            },
        } 
    },
    "events": {
        "onflag": {
            "opcode": "event_whenflagclicked",
            "type": "hat",
            "args": []
        },
        "onkey": {
            "opcode": "event_whenkeypressed",
            "type": "hat",
            "args": ["f.key_option{...}"]
        },
        "onclick": {
            "opcode": "event_whenthisspriteclicked",
            "type": "hat",
            "args": []
        },
        "onbgswitch": {
            "opcode": "event_whenbackdropswitchesto",
            "type": "hat",
            "args": ["f.backdrop{backdrop1;...}"]
        },
        "ongreater": {
            "opcode": "event_whengreaterthan",
            "type": "hat",
            "args": ["f.whengreaterthanmenu{loudness,timer}", "i.value"]
        },
        "ontouch": {
            "opcode": "event_whentouchingobject",
            "type": "hat",
            "args": ["i.touchingobjectmenu(touching_menu)"]
        },
        "broadcast": {
            "whenbroadcast": {
                "opcode": "event_whenbroadcastreceived",
                "type": "hat",
                "args": ["f.broadcast_option{...}"]
            },
            "send": {
                "opcode": "event_broadcast",
                "type": "stack",
                "args": ["i.broadcast_input"]
            },
            "sendwait": {
                "opcode": "event_broadcastandwait",
                "type": "stack",
                "args": ["i.broadcast_input"]
            },
        }
    },
    "control": {
        "wait": {
            "opcode": "control_wait",
            "type": "stack",
            "args": ["i.duration"]
        },
        "repeat": {
            "opcode": "control_repeat",
            "type": "c",
            "args": ["i.times", "i.substack"]
        },
        "forever": {
            "opcode": "control_forever",
            "type": "c",
            "args": ["i.substack"]
        },
        "if": {
            "opcode": "control_if",
            "type": "c",
            "args": ["i.condition[bool]", "i.substack"]
        },
        "ifelse": {
            "opcode": "control_if_else",
            "type": "c",
            "args": ["i.condition[bool]", "i.substack", "i.substack2"]
        },
        "waituntil": {
            "opcode": "control_wait_until",
            "type": "stack",
            "args": ["i.condition[bool]"]
        },
        "repeatuntil": {
            "opcode": "control_repeat_until",
            "type": "c",
            "args": ["i.condition[bool]", "i.substack"]
        },
        "stop": {
            "opcode": "control_stop",
            "type": "cap",
            "args": ["f.stop_option{all;this script;other scripts in sprite}"]
        },
        "clone": {
            "onstart": {
                "opcode": "control_start_as_clone",
                "type": "hat",
                "args": []
            },
            "create": {
                "opcode": "control_create_clone_of",
                "type": "stack",
                "args": ["i.clone_option(clone_menu)"]
            },
            "delete": {
                "opcode": "control_delete_this_clone",
                "type": "cap",
                "args": []
            }
        },
        "while": {
            "opcode": "control_while",
            "type": "c",
            "args": ["i.condition", "i.substack"]
        },
        "for": {
            "opcode": "control_for_each",
            "type": "c",
            "args": ["f.variable", "i.value", "i.substack"]
        },
        "allAtOnce": {
            "opcode": "control_all_at_once",
            "type": "c",
            "args": ["i.substack"]
        },
        "counter": {
            "counter": {
                "opcode": "control_get_counter",
                "type": "reporter",
                "args": []
            },
            "clear": {
                "opcode": "control_clear_counter",
                "type": "stack",
                "args": []
            },
            "inc": {
                "opcode": "control_incr_counter",
                "type": "stack",
                "args": []
            }
        },
    },
    "sensing": {
        "touching": {
            "opcode": "sensing_touchingobject",
            "type": "reporter",
            "args": ["i.touchingobjectmenu(touching_menu)"]
        },
        "touchingClr": {
            "opcode": "sensing_touchingcolor",
            "type": "reporter",
            "args": ["i.color"]
        },
        "clronclr": {
            "opcode": "sensing_coloristouchingcolor",
            "type": "reporter",
            "args": ["i.color", "i.color2"]
        },
        "distanceto": {
            "opcode": "sensing_distanceto",
            "type": "reporter",
            "args": ["i.distancetomenu(distance_menu)"]
        },
        "ask": {
            "opcode": "sensing_askandwait",
            "type": "stack",
            "args": ["i.question"]
        },
        "answer": {
            "opcode": "sensing_answer",
            "type": "reporter",
            "args": []
        },
        "keypressed": {
            "opcode": "sensing_keypressed",
            "type": "reporter",
            "args": ["i.key_option(key_menu)"]
        },
        "mouse": {
            "mouse": {
                "opcode": "sensing_mousedown",
                "type": "reporter",
                "args": []
            },
            "x": {
                "opcode": "sensing_mousex",
                "type": "reporter",
                "args": []
            },
            "y": {
                "opcode": "sensing_mousey",
                "type": "reporter",
                "args": []
            },
        },
        "setdragmode": {
            "opcode": "sensing_setdragmode",
            "type": "stack",
            "args": ["f.drag_mode{draggable;not draggable}"]
        },
        "loudness": {
            "opcode": "sensing_loudness",
            "type": "reporter",
            "args": []
        },
        "time": {
            "timer": {
                "opcode": "sensing_timer",
                "type": "reporter",
                "args": []
            },
            "reset": {
                "opcode": "sensing_resettimer",
                "type": "stack",
                "args": []
            },
        },
        "getAttribute": {
            "opcode": "sensing_of",
            "type": "reporter",
            "args": ["f.property{x position;y position;direction;costume #;costume name;size;volume}", "i.object(sensingobj_menu)"]
        },
        "current": {
            "opcode": "sensing_current",
            "type": "reporter",
            "args": ["f.currentmenu{year;month;date;day of week;hour;minute;second}"]
        },
        "dayssince2000": {
            "opcode": "sensing_dayssince2000",
            "type": "reporter",
            "args": []
        },
        "username": {
            "opcode": "sensing_username",
            "type": "reporter",
            "args": []
        }
    },
    "operator": {
        "add": {
            "opcode": "operator_add",
            "type": "reporter",
            "args": ["i.num1", "i.num2"]
        },
        "subtract": {
            "opcode": "operator_subtract",
            "type": "reporter",
            "args": ["i.num1", "i.num2"]
        },
        "multiply": {
            "opcode": "operator_multiply",
            "type": "reporter",
            "args": ["i.num1", "i.num2"]
        },
        "divide": {
            "opcode": "operator_divide",
            "type": "reporter",
            "args": ["i.num1", "i.num2"]
        },
        "random": {
            "opcode": "operator_random",
            "type": "reporter",
            "args": ["i.from", "i.to"]
        },
        "lt": {
            "opcode": "operator_lt",
            "type": "reporter",
            "args": ["i.operand1", "i.operand2"]
        },
        "equals": {
            "opcode": "operator_equals",
            "type": "reporter",
            "args": ["i.operand1", "i.operand2"]
        },
        "gt": {
            "opcode": "operator_gt",
            "type": "reporter",
            "args": ["i.operand1", "i.operand2"]
        },
        "and": {
            "opcode": "operator_and",
            "type": "reporter",
            "args": ["i.operand1[bool]", "i.operand2[bool]"]
        },
        "or": {
            "opcode": "operator_or",
            "type": "reporter",
            "args": ["i.operand1[bool]", "i.operand2[bool]"]
        },
        "not": {
            "opcode": "operator_not",
            "type": "reporter",
            "args": ["i.operand[bool]"]
        },
        "join": {
            "opcode": "operator_join",
            "type": "reporter",
            "args": ["i.string1", "i.string2"]
        },
        "getLetter": {
            "opcode": "operator_letter_of",
            "type": "reporter",
            "args": ["i.letter", "i.string"]
        },
        "length": {
            "opcode": "operator_length",
            "type": "reporter",
            "args": ["i.string"]
        },
        "contains": {
            "opcode": "operator_contains",
            "type": "reporter",
            "args": ["i.string1", "i.string2"]
        },
        "mod": {
            "opcode": "operator_mod",
            "type": "reporter",
            "args": ["i.num1", "i.num2"]
        },
        "round": {
            "opcode": "operator_round",
            "type": "reporter",
            "args": ["i.num"]
        },
        "mathop": {
            "opcode": "operator_mathop",
            "type": "reporter",
            "args": ["f.operator{abs;floor;ceiling;sqrt;sin;cos;tan;asin;acos;atan;ln;log;e ^;10 ^}", "i.num"]
        }
    },
    "variable": {
        "set": {
            "opcode": "data_setvariableto",
            "type": "stack",
            "args": ["f.variable{...}", "i.value"]
        },
        "change": {
            "opcode": "data_changevariableby",
            "type": "stack",
            "args": ["f.variable{...}", "i.value"]
        },
        "show": {
            "opcode": "data_showvariable",
            "type": "stack",
            "args": ["f.variable{...}"]
        },
        "hide": {
            "opcode": "data_hidevariable",
            "type": "stack",
            "args": ["f.variable{...}"]
        }
    },
    "list": {
        "add": {
            "opcode": "data_addtolist",
            "type": "stack",
            "args": ["f.list", "i.item"]
        },
        "delete": {
            "opcode": "data_deleteoflist",
            "type": "stack",
            "args": ["f.list", "i.index"]
        },
        "deleteall": {
            "opcode": "data_deletealloflist",
            "type": "stack",
            "args": ["f.list"]
        },
        "insert": {
            "opcode": "data_insertatlist",
            "type": "stack",
            "args": ["f.list", "i.index", "i.item"]
        },
        "replace": {
            "opcode": "data_replaceitemoflist",
            "type": "stack",
            "args": ["f.list", "i.index", "i.item"]
        },
        "get": {
            "opcode": "data_itemoflist",
            "type": "reporter",
            "args": ["f.list", "i.index"]
        },
        "getindex": {
            "opcode": "data_itemnumoflist",
            "type": "reporter",
            "args": ["f.list", "i.item"]
        },
        "length": {
            "opcode": "data_lengthoflist",
            "type": "reporter",
            "args": ["f.list"]
        },
        "contains": {
            "opcode": "data_listcontainsitem",
            "type": "reporter",
            "args": ["f.list", "i.item"]
        },
        "show": {
            "opcode": "data_showlist",
            "type": "stack",
            "args": ["f.list"]
        },
        "hide": {
            "opcode": "data_hidelist",
            "type": "stack",
            "args": ["f.list"]
        }
    },
    "myblocks": {
        "funcargbool": {
            "opcode": "argument_reporter_boolean",
            "type": "reporter",
            "args": ["f.value"]
        },
        "funcargexp": {
            "opcode": "argument_reporter_string_number",
            "type": "reporter",
            "args": ["f.value"]
        },
        "return": {
            "opcode": None,
            "type": "cap",
            "args": ["__all__"],
            "interpreted": True,
            "composition": ['lists.add(@l:{function})\ncontrol.stop("this script")'] # Create a list of items to be added to the ast, allowing it to return returned values by inserting return deletion after control.stop
        }
    },
    "pen": {
        "clear": {
            "opcode": "pen_clear",
            "type": "stack",
            "args": []
        },
        "stamp": {
            "opcode": "pen_stamp",
            "type": "stack",
            "args": []
        },
        "down": {
            "opcode": "pen_penDown",
            "type": "stack",
            "args": []
        },
        "up": {
            "opcode": "pen_penUp",
            "type": "stack",
            "args": []
        },
        "hexset": {
            "opcode": "pen_setPenColorToColor",
            "type": "stack",
            "args": ["i.color"]
        },
        "change": {
            "opcode": "pen_changePenColorParamBy",
            "type": "stack",
            "args": ["i.color_param{color;saturation;brightness;transparency}", "i.value"]
        },
        "set": {
            "opcode": "pen_setPenColorParamTo",
            "type": "stack",
            "args": ["i.color_param(pen_menu)", "i.value"]
        },
        "size": {
            "change": {
                "opcode": "pen_changePenSizeBy",
                "type": "stack",
                "args": ["i.size"]
            },
            "set": {
                "opcode": "pen_setPenSizeTo",
                "type": "stack",
                "args": ["i.size"]
            },
        },
        "shade": {
            "set": {
                "opcode": "pen_setPenShadeToNumber",
                "type": "stack",
                "args": ["i.shade"]
            },
            "changeshade": {
                "opcode": "pen_changePenShadeBy",
                "type": "stack",
                "args": ["i.shade"]
            }
        }
    },
    "sys": {
        "load": {
            "args": ["filename"], # load("data.txt")
        },
        "create": {
            "args": ["type","instance","data"], # create(type: public, @l:bazinga, data: "stuff\nstuff\nstuff") or data: load("data.txt") ... create(type: public, @d:costumes, data: load("costumes.json"))
        },
        "import": {
            "args": ["filename"], # import("costume.png")
        },
        "alias": {
            "args": ["alias","command"], # alias("move","motion.move")
        }
    },
    "bltn": {
        "true": {
            "opcode": None,
            "type": "reporter",
            "args": [],
            "interpreted": True,
            "composition": ['lists.add(@l:{function})\ncontrol.stop("this script")'] # Create a list of items to be added to the ast, allowing it to return returned values by inserting return deletion after control.stop
        }
    },
    "fn": {}, # Blank, but used for all functions created in the script
    "creds": {
        "misty": { # JS patch
            "opcode": "creds_misty",
            "type": "stack",
            "args": []
        },
        "allu": { # Prints: "Hlleo Wlrod"
            "opcode": "creds_allu",
            "type": "stack",
            "args": []
        }
    }
}

# So. Um. Aliases can be used to overwrite built in functions ... (bug or feature?)
aliases = {"move": "motion.move"}

def get_command(command: str) -> dict:
    """
    Returns the command dictionary given a command reference

    ### Parameters:
    - command (str): Command reference (e.g. "motion.move")

    ### Returns:
    - command (dict): Command dictionary (or None if not found)
    """

    # Check for alias
    if command in aliases:
        command = aliases[command]

    # Split the command into keys
    keys = command.split(".")
    
    # Get the command by traversing the dictionary
    result = commands
    for key in keys:
        result = result.get(key, None)

    if not result:
        return None

    return result

def read_commands() -> list[str]:
    """
    Reads through and gets all the commands from the commands file (and preprocess and returns a neat list of commands)

    ### Returns:
    - found_commands (list[str]): Cleaned list of commands
    """

    with open(os.path.join('app_static', 'references', 'commands.txt'), "r") as f:
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

    ### Parameters:
    - opcode (str): OpCode of the command

    ### Returns:
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

    if not return_dict:
        error_handler.add_error(f"Cmd with opcode: '{opcode}' not found", opcode, -1)
        error_handler.throw_errors()

    return return_dict

def read_by_name(name: str):
    """
    Returns a dictionary of attributes about a command including:
    - name (str): Name of the command
    - opcode (str): OpCode of the command
    - type (str): Type of the command
    - inputs (str): Input names of the command (separated by commas)

    ### Parameters:
    - name (str): Name of the command (different than opCode)

    ### Returns:
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

    if not name:
        error_handler.add_error(f"Cmd with opcode: '{name}' not found", name, -1)
        error_handler.throw_errors()

    return return_dict

# print(read_by_opcode("motion_glidesecstoxy"))

#print(get_command("looks.say"))