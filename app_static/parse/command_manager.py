"""
Manages Katnip commands
"""

# Standard Library
import os
from typing import Optional, Dict, Any, List

# Third Party

# Local
import error_handler
from custom_types import CommandArg, CommandInfo

class CommandManager:
    def __init__(self, project_id: int):
        self.project_id = project_id
        
        self.commands = {
            "internal": {
                "goto_menu": {
                    "opcode": "motion_goto_menu",
                    "type": "reporter",
                    "args": [{"section":"fields", "name":"to", "options":["_random_","_mouse_","..."]}]
                },
                "glideto_menu": {
                    "opcode": "motion_glideto_menu",
                    "type": "reporter",
                    "args": [{"section":"fields", "name":"to", "options":["_random_","_mouse_","..."]}]
                },
                "point_towards_menu": {
                    "opcode": "motion_pointtowards_menu",
                    "type": "reporter",
                    "args": [{"section":"fields", "name":"towards", "options":["_random_","_mouse_","..."]}]
                },
                "costume_menu": {
                    "opcode": "looks_costume",
                    "type": "reporter",
                    "args": [{"section":"fields", "name":"costume", "options":["..."]}]
                },
                "backdrop_menu": {
                    "opcode": "looks_backdrops",
                    "type": "reporter",
                    "args": [{"section":"fields", "name":"backdrop", "options":["..."]}]
                },
                "sound_menu": {
                    "opcode": "sound_sounds_menu",
                    "type": "reporter",
                    "args": [{"section":"fields", "name":"sound_menu", "options":["..."]}]
                },
                "clone_menu": {
                    "opcode": "control_create_clone_of_menu",
                    "type": "reporter",
                    "args": [{"section":"fields", "name":"costume", "options":["myself","..."]}]
                },
                "touching_menu": {
                    "opcode": "sensing_touchingobjectmenu",
                    "type": "reporter",
                    "args": [{"section":"fields", "name":"touchingobjectmenu", "options":["_mouse_","_edge_","..."]}]
                },
                "distance_menu": {
                    "opcode": "sensing_distancetomenu",
                    "type": "reporter",
                    "args": [{"section":"fields", "name":"distancetomenu", "options":["_mouse_","..."]}]
                },
                "key_menu": {
                    "opcode": "sensing_keyoptions",
                    "type": "reporter",
                    "args": [{"section":"fields", "name":"key_option", "options":["space","left arrow","right arrow","down arrow","up arrow","enter","any"] + list("abcdefghijklmnopqrstuvwxyz1234567890-,.`=[]\\;'/")}]
                },
                "sensingobj_menu": {
                    "opcode": "sensing_of_object_menu",
                    "type": "reporter",
                    "args": [{"section":"fields", "name":"object", "options":["..."]}]
                },
                "pen_menu": {
                    "opcode": "pen_menu_colorParam",
                    "type": "reporter",
                    "args": [{"section":"fields", "name":"colorParam", "options":["..."]}]
                }
            },
            "motion": {
                "move": {
                    "opcode": "motion_movesteps", 
                    "type": "stack", 
                    "args": [{"section":"inputs", "name":"steps", "type":"num"}]
                },
                "turn": {
                    "opcode": "motion_turnright", 
                    "type": "stack", 
                    "args": [{"section":"inputs", "name":"degrees", "type":"num"}]
                },
                "gotoxy": {
                    "opcode": "motion_gotoxy", 
                    "type": "stack", 
                    "args": [{"section":"inputs", "name":"x", "type":"num"}, 
                             {"section":"inputs", "name":"y", "type":"num"}]
                },
                "goto": {
                    "opcode": "motion_goto", 
                    "type": "stack", 
                    "args": [{"section":"inputs", "name":"to", "type":"menu:internal.goto_menu"}]
                },
                "glideXY": {
                    "opcode": "motion_glidesecstoxy", 
                    "type": "stack", 
                    "args": [{"section":"inputs", "name":"secs", "type":"num"}, 
                             {"section":"inputs", "name":"x", "type":"num"}, 
                             {"section":"inputs", "name":"y", "type":"num"}]
                },
                "glideto": {
                    "opcode": "motion_glideto", 
                    "type": "stack", 
                    "args": [{"section":"inputs", "name":"secs", "type":"num"}, 
                             {"section":"inputs", "name":"to", "type":"menu:internal.glideto_menu"}]
                },
                "point": {
                    "opcode": "motion_pointindirection", 
                    "type": "stack", 
                    "args": [{"section":"inputs", "name":"direction", "type":"num"}]
                },
                "pointTo": {
                    "opcode": "motion_pointtowards", 
                    "type": "stack", 
                    "args": [{"section":"inputs", "name":"towards", "type":"menu:internal.point_towards_menu"}]
                },
                "changeX": {
                    "opcode": "motion_changexby", 
                    "type": "stack", 
                    "args": [{"section":"inputs", "name":"dx", "type":"num"}]
                },
                "setX": {
                    "opcode": "motion_setx", 
                    "type": "stack", 
                    "args": [{"section":"inputs", "name":"x", "type":"num"}]
                },
                "changeY": {
                    "opcode": "motion_changeyby", 
                    "type": "stack", 
                    "args": [{"section":"inputs", "name":"dy", "type":"num"}]
                },
                "setY": {
                    "opcode": "motion_sety", 
                    "type": "stack", 
                    "args": [{"section":"inputs", "name":"y", "type":"num"}]
                },
                "edgeBounce": {
                    "opcode": "motion_ifonedgebounce", 
                    "type": "stack", 
                    "args": []
                },
                "rotationStyle": {
                    "opcode": "motion_setrotationstyle", 
                    "type": "stack", 
                    "args": [{"section":"fields", "name":"style", "options":["left-right","don't rotate","all around"]}]
                },
                "xPos": {
                    "opcode": "motion_xposition", 
                    "type": "reporter", 
                    "args": [],
                    "returnType": "num"
                },
                "yPos": {
                    "opcode": "motion_yposition", 
                    "type": "reporter", 
                    "args": [],
                    "returnType": "num"
                },
                "direction": {
                    "opcode": "motion_direction", 
                    "type": "reporter", 
                    "args": [],
                    "returnType": "num"
                }
            },
            "looks": {
                "timesay": {
                    "opcode": "looks_sayforsecs", 
                    "type": "stack", 
                    "args": [{"section":"inputs", "name":"message", "type":"exp"}, 
                             {"section":"inputs", "name":"secs", "type":"num"}]
                },
                "say": {
                    "opcode": "looks_say", 
                    "type": "stack", 
                    "args": [{"section":"inputs", "name":"message", "type":"exp"}]
                },
                "timethink": {
                    "opcode": "looks_thinkforsecs", 
                    "type": "stack", 
                    "args": [{"section":"inputs", "name":"message", "type":"exp"}, 
                             {"section":"inputs", "name":"secs", "type":"num"}]
                },
                "think": {
                    "opcode": "looks_think", 
                    "type": "stack", 
                    "args": [{"section":"inputs", "name":"message", "type":"exp"}]
                },
                "costume": {
                    "costume": {
                        "opcode": "looks_costumenumbername", 
                        "type": "reporter", 
                        "args": [{"section":"fields", "name":"number_name", "options":["number","name"]}],
                        "returnType": "exp"
                    },
                    "switch": { 
                        "opcode": "looks_switchcostumeto", 
                        "type": "stack", 
                        "args": [{"section":"inputs", "name":"costume", "type":"menu:internal.costume_menu"}]
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
                        "args": [{"section":"inputs", "name":"number_name", "options":["number","name"]}],
                        "returnType": "exp"
                    },
                    "switch": {
                        "opcode": "looks_switchbackdropto", 
                        "type": "stack", 
                        "args": [{"section":"inputs", "name":"costume", "type":"menu:internal.backdrop_menu"}]
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
                        "args": [],
                        "returnType": "num"
                    },
                    "change": {
                        "opcode": "looks_changesizeby", 
                        "type": "stack", 
                        "args": [{"section":"inputs", "name":"change", "type":"num"}]
                    },
                    "set": {
                        "opcode": "looks_setsizeto", 
                        "type": "stack", 
                        "args": [{"section":"inputs", "name":"size", "type":"num"}]
                    },
                },
                "fx": {
                    "change": {
                        "opcode": "looks_changeeffectby", 
                        "type": "stack", 
                        "args": [{"section":"fields", "name":"effect", "options":["color","fisheye","whirl","pixelate","mosaic","brightness","ghost"]}, 
                                 {"section":"inputs", "name":"change", "type":"num"}]
                    },
                    "set": {
                        "opcode": "looks_seteffectto", 
                        "type": "stack", 
                        "args": [{"section":"fields", "name":"effect", "options":["color","fisheye","whirl","pixelate","mosaic","brightness","ghost"]}, 
                                 {"section":"inputs", "name":"change", "type":"num"}]
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
                    "args": [{"section":"fields", "name":"front_back", "options":["front","back"]}]
                },
                "changeLayer": {
                    "opcode": "looks_goforwardbackwardlayers", 
                    "type": "stack", 
                    "args": [{"section":"fields", "name":"forward_backward", "options":["forward","backward"]}, 
                             {"section":"inputs", "name":"num", "type":"num"}]
                },
            },
            "sound": {
                "play": {
                    "opcode": "sound_play",
                    "type": "stack",
                    "args": [{"section":"inputs", "name":"sound_menu", "type":"menu:sound_menu"}]
                },
                "playwait": {
                    "opcode": "sound_playuntildone",
                    "type": "stack",
                    "args": [{"section":"inputs", "name":"sound_menu", "type":"menu:sound_menu"}]
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
                        "args": [{"section":"fields", "name":"effect", "options":["pitch","pan left/right"]}, 
                                 {"section":"inputs", "name":"value", "type":"num"}]
                    },
                    "set": {
                        "opcode": "sound_seteffectto",
                        "type": "stack",
                        "args": [{"section":"fields", "name":"effect", "options":["pitch","pan left/right"]}, 
                                 {"section":"inputs", "name":"value", "type":"num"}]
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
                        "args": [],
                        "returnType": "num"
                    },
                    "change": {
                        "opcode": "sound_changevolumeby",
                        "type": "stack",
                        "args": [{"section":"inputs", "name":"volume", "type":"num"}]
                    },
                    "set": {
                        "opcode": "sound_setvolumeto",
                        "type": "stack",
                        "args": [{"section":"inputs", "name":"volume", "type":"num"}]
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
                    "args": [{"section":"fields", "name":"key_option", "options":["..."]}]
                },
                "onclick": {
                    "opcode": "event_whenthisspriteclicked",
                    "type": "hat",
                    "args": []
                },
                "onbgswitch": {
                    "opcode": "event_whenbackdropswitchesto",
                    "type": "hat",
                    "args": [{"section":"fields", "name":"backdrop", "options":["..."]}]
                },
                "ongreater": {
                    "opcode": "event_whengreaterthan",
                    "type": "hat",
                    "args": [{"section":"fields", "name":"whengreaterthanmenu", "options":["loudness","timer"]},
                             {"section":"inputs", "name":"value", "type":"num"}]
                },
                "ontouch": {
                    "opcode": "event_whentouchingobject",
                    "type": "hat",
                    "args": [{"section":"inputs", "name":"touchingobjectmenu", "type":"menu:touching_menu"}]
                },
                "broadcast": {
                    "whenbroadcast": {
                        "opcode": "event_whenbroadcastreceived",
                        "type": "hat",
                        "args": [{"section":"fields", "name":"broadcast_option", "options":["..."]}]
                    },
                    "send": {
                        "opcode": "event_broadcast",
                        "type": "stack",
                        "args": [{"section":"fields", "name":"broadcast_input", "options":["..."]}]
                    },
                    "sendwait": {
                        "opcode": "event_broadcastandwait",
                        "type": "stack",
                        "args": [{"section":"fields", "name":"broadcast_input", "options":["..."]}]
                    },
                }
            },
            "control": {
                "wait": {
                    "opcode": "control_wait",
                    "type": "stack",
                    "args": [{"section":"inputs", "name":"duration", "type":"num"}]
                },
                "repeat": {
                    "opcode": "control_repeat",
                    "type": "c",
                    "args": [{"section":"inputs", "name":"times", "type":"num"}, 
                             {"section":"inputs", "name":"substack", "type":"substack"}]
                },
                "forever": {
                    "opcode": "control_forever",
                    "type": "c",
                    "args": [{"section":"inputs", "name":"substack", "type":"substack"}]
                },
                "if": {
                    "opcode": "control_if",
                    "type": "c",
                    "args": [{"section":"inputs", "name":"condition", "type":"bool"}, 
                             {"section":"inputs", "name":"substack", "type":"substack"}]
                },
                "ifelse": {
                    "opcode": "control_if_else",
                    "type": "c",
                    "args": [{"section":"inputs", "name":"condition", "type":"bool"}, 
                             {"section":"inputs", "name":"substack", "type":"substack"},
                             {"section":"inputs", "name":"substack2", "type":"substack"}]
                },
                "waituntil": {
                    "opcode": "control_wait_until",
                    "type": "stack",
                    "args": [{"section":"inputs", "name":"condition", "type":"bool"}]
                },
                "repeatuntil": {
                    "opcode": "control_repeat_until",
                    "type": "c",
                    "args": [{"section":"inputs", "name":"condition", "type":"bool"}, 
                             {"section":"inputs", "name":"substack", "type":"substack"}]
                },
                "stop": {
                    "opcode": "control_stop",
                    "type": "cap",
                    "args": [{"section":"fields", "name":"stop_option", "options":["all","this script","other scripts in sprite"]}]
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
                        "args": [{"section":"inputs", "name":"clone_option", "type":"menu:clone_menu"}]
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
                    "args": [{"section":"inputs", "name":"condition", "type":"bool"}, 
                             {"section":"inputs", "name":"substack", "type":"substack"}]
                },
                "for": {
                    "opcode": "control_for_each",
                    "type": "c",
                    "args": [{"section":"fields", "name":"variable", "options":["..."]},
                             {"section":"inputs", "name":"value", "type":"num"}, 
                             {"section":"inputs", "name":"substack", "type":"substack"}]
                },
                "allAtOnce": {
                    "opcode": "control_all_at_once",
                    "type": "c",
                    "args": [{"section":"inputs", "name":"substack", "type":"substack"}]
                },
                "counter": {
                    "counter": {
                        "opcode": "control_get_counter",
                        "type": "reporter",
                        "args": [],
                        "returnType": "num"
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
                    "args": [{"section":"inputs", "name":"touchingobjectmenu", "type":"menu:touching_menu"}],
                    "returnType": "bool"
                },
                "touchingClr": {
                    "opcode": "sensing_touchingcolor",
                    "type": "reporter",
                    "args": [{"section":"inputs", "name":"color", "type":"str"}], # Needs to be in 2 formats: "#RRGGBB" or "#RGB"
                    "returnType": "bool"
                },
                "clronclr": {
                    "opcode": "sensing_coloristouchingcolor",
                    "type": "reporter",
                    "args": [{"section":"inputs", "name":"color", "type":"str"}, 
                             {"section":"inputs", "name":"color2", "type":"str"}],
                    "returnType": "bool"
                },
                "distanceto": {
                    "opcode": "sensing_distanceto",
                    "type": "reporter",
                    "args": [{"section":"inputs", "name":"distancetomenu", "type":"menu:distance_menu"}],
                    "returnType": "num"
                },
                "ask": {
                    "opcode": "sensing_askandwait",
                    "type": "stack",
                    "args": ["i.question"]
                },
                "answer": {
                    "opcode": "sensing_answer",
                    "type": "reporter",
                    "args": [],
                    "returnType": "exp"
                },
                "keypressed": {
                    "opcode": "sensing_keypressed",
                    "type": "reporter",
                    "args": [{"section":"inputs", "name":"key_option", "type":"menu:key_menu"}],
                    "returnType": "bool"
                },
                "mouse": {
                    "down": {
                        "opcode": "sensing_mousedown",
                        "type": "reporter",
                        "args": [],
                        "returnType": "bool"
                    },
                    "x": {
                        "opcode": "sensing_mousex",
                        "type": "reporter",
                        "args": [],
                        "returnType": "num"
                    },
                    "y": {
                        "opcode": "sensing_mousey",
                        "type": "reporter",
                        "args": [],
                        "returnType": "num"
                    },
                },
                "setdragmode": {
                    "opcode": "sensing_setdragmode",
                    "type": "stack",
                    "args": [{"section":"fields", "name":"drag_mode", "options":["draggable","not draggable"]}]
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
                        "args": [],
                        "returnType": "num"
                    },
                    "reset": {
                        "opcode": "sensing_resettimer",
                        "type": "stack",
                        "args": []
                    },
                },
                "getattr": {
                    "opcode": "sensing_of",
                    "type": "reporter",
                    "args": [{"section":"fields", "name":"property", "options":["x position","y position","direction","costume #","costume name","size","volume"]}, 
                             {"section":"inputs", "name":"object", "type":"menu:internal.sensingobj_menu"}]
                },
                "current": {
                    "opcode": "sensing_current",
                    "type": "reporter",
                    "args": [{"section":"fields", "name":"currentmenu", "options":["year","month","date","day of week","hour","minute","second"]}],
                    "returnType": "exp"
                },
                "dayssince2000": {
                    "opcode": "sensing_dayssince2000",
                    "type": "reporter",
                    "args": [],
                    "returnType": "num"
                },
                "username": {
                    "opcode": "sensing_username",
                    "type": "reporter",
                    "args": [],
                    "returnType": "exp"
                }
            },
            "op": { # Operator
                "add": {
                    "opcode": "operator_add",
                    "type": "reporter",
                    "args": [{"section":"inputs", "name":"num1", "type":"num"}, 
                             {"section":"inputs", "name":"num2", "type":"num"}],
                    "returnType": "num"
                },
                "subtract": {
                    "opcode": "operator_subtract",
                    "type": "reporter",
                    "args": [{"section":"inputs", "name":"num1", "type":"num"}, 
                             {"section":"inputs", "name":"num2", "type":"num"}],
                    "returnType": "num"
                },
                "multiply": {
                    "opcode": "operator_multiply",
                    "type": "reporter",
                    "args": [{"section":"inputs", "name":"num1", "type":"num"}, 
                             {"section":"inputs", "name":"num2", "type":"num"}],
                    "returnType": "num"
                },
                "divide": {
                    "opcode": "operator_divide",
                    "type": "reporter",
                    "args": [{"section":"inputs", "name":"num1", "type":"num"}, 
                             {"section":"inputs", "name":"num2", "type":"num"}],
                    "returnType": "num"
                },
                "mod": {
                    "opcode": "operator_mod",
                    "type": "reporter",
                    "args": [{"section":"inputs", "name":"num1", "type":"num"}, 
                             {"section":"inputs", "name":"num2", "type":"num"}],
                    "returnType": "num"
                },
                "random": {
                    "opcode": "operator_random",
                    "type": "reporter",
                    "args": [{"section":"inputs", "name":"operand1", "type":"bool"}, 
                             {"section":"inputs", "name":"operand", "type":"bool"}],
                    "returnType": "num"
                },
                "lt": {
                    "opcode": "operator_lt",
                    "type": "reporter",
                    "args": [{"section":"inputs", "name":"operand1", "type":"bool"}, 
                             {"section":"inputs", "name":"operand", "type":"bool"}],
                    "returnType": "bool"
                },
                "equals": {
                    "opcode": "operator_equals",
                    "type": "reporter",
                    "args": [{"section":"inputs", "name":"operand1", "type":"bool"}, 
                             {"section":"inputs", "name":"operand", "type":"bool"}],
                    "returnType": "bool"
                },
                "gt": {
                    "opcode": "operator_gt",
                    "type": "reporter",
                    "args": [{"section":"inputs", "name":"operand1", "type":"bool"}, 
                             {"section":"inputs", "name":"operand", "type":"bool"}],
                    "returnType": "bool"
                },
                "and": {
                    "opcode": "operator_and",
                    "type": "reporter",
                    "args": [{"section":"inputs", "name":"operand1", "type":"bool"}, 
                             {"section":"inputs", "name":"operand", "type":"bool"}],
                    "returnType": "bool"
                },
                "or": {
                    "opcode": "operator_or",
                    "type": "reporter",
                    "args": [{"section":"inputs", "name":"operand1", "type":"bool"}, 
                             {"section":"inputs", "name":"operand", "type":"bool"}],
                    "returnType": "bool"
                },
                "not": {
                    "opcode": "operator_not",
                    "type": "reporter",
                    "args": [{"section":"inputs", "name":"operand", "type":"bool"}],
                    "returnType": "bool"
                },
                "join": {
                    "opcode": "operator_join",
                    "type": "reporter",
                    "args": [{"section":"inputs", "name":"string1", "type":"exp"}, 
                             {"section":"inputs", "name":"string2", "type":"exp"}],
                    "returnType": "exp"
                },
                "getChar": {
                    "opcode": "operator_letter_of",
                    "type": "reporter",
                    "args": [{"section":"inputs", "name":"letter", "type":"num"}, 
                             {"section":"inputs", "name":"string", "type":"num"}],
                    "returnType": "exp"
                },
                "length": {
                    "opcode": "operator_length",
                    "type": "reporter",
                    "args": [{"section":"inputs", "name":"string", "type":"num"}],
                    "returnType": "num"
                },
                "contains": {
                    "opcode": "operator_contains",
                    "type": "reporter",
                    "args": [{"section":"inputs", "name":"string1", "type":"num"}, 
                             {"section":"inputs", "name":"string2", "type":"num"}],
                    "returnType": "bool"
                },
                "round": {
                    "opcode": "operator_round",
                    "type": "reporter",
                    "args": [{"section":"inputs", "name":"num", "type":"num"}],
                    "returnType": "num"
                },
                "mathop": {
                    "opcode": "operator_mathop",
                    "type": "reporter",
                    "args": [{"section": "fields", "name": "operator", "options": ["floor", "ceiling", "sqrt", "sin", "cos", "tan", "asin", "acos", "atan", "ln", "log", "e ^", "10 ^"]}, 
                            {"section": "inputs", "name": "num", "type": "num"}],
                    "returnType": "num"
                },
                # Seperate commands to make mathop references easier
                "abs": {
                    "opcode": None,
                    "type": "reporter",
                    "args": [{"section": None, "name": "num", "type": "num"}],
                    "macro": True,
                    "template": ['op.mathop("abs", {num})'],
                    "returnType": "num"
                },
                "floor": {
                    "opcode": None,
                    "type": "reporter",
                    "args": [{"section": None, "name": "num", "type": "num"}],
                    "macro": True,
                    "template": ['op.mathop("floor", {num})'],
                    "returnType": "num"
                },
                "ceiling": {
                    "opcode": None,
                    "type": "reporter",
                    "args": [{"section": None, "name": "num", "type": "num"}],
                    "macro": True,
                    "template": ['op.mathop("ceiling", {a.num})'],
                    "returnType": "num"
                },
                "sqrt": {
                    "opcode": None,
                    "type": "reporter",
                    "args": [{"section": None, "name": "num", "type": "num"}],
                    "macro": True,
                    "template": ['op.mathop("sqrt", {a.num})'],
                    "returnType": "num"
                },
                "sin": {
                    "opcode": None,
                    "type": "reporter",
                    "args": [{"section": None, "name": "num", "type": "num"}],
                    "macro": True,
                    "template": ['op.mathop("sin", {a.num})'],
                    "returnType": "num"
                },
                "cos": {
                    "opcode": None,
                    "type": "reporter",
                    "args": [{"section": None, "name": "num", "type": "num"}],
                    "macro": True,
                    "template": ['op.mathop("cos", {a.num})'],
                    "returnType": "num"
                },
                "tan": {
                    "opcode": None,
                    "type": "reporter",
                    "args": [{"section": None, "name": "num", "type": "num"}],
                    "macro": True,
                    "template": ['op.mathop("tan", {a.num})'],
                    "returnType": "num"
                },
                "asin": {
                    "opcode": None,
                    "type": "reporter",
                    "args": [{"section": None, "name": "num", "type": "num"}],
                    "macro": True,
                    "template": ['op.mathop("asin", {a.num})'],
                    "returnType": "num"
                },
                "acos": {
                    "opcode": None,
                    "type": "reporter",
                    "args": [{"section": None, "name": "num", "type": "num"}],
                    "macro": True,
                    "template": ['op.mathop("acos", {a.num})'],
                    "returnType": "num"
                },
                "atan": {
                    "opcode": None,
                    "type": "reporter",
                    "args": [{"section": None, "name": "num", "type": "num"}],
                    "macro": True,
                    "template": ['op.mathop("atan", {a.num})'],
                    "returnType": "num"
                },
                "ln": {
                    "opcode": None,
                    "type": "reporter",
                    "args": [{"section": None, "name": "num", "type": "num"}],
                    "macro": True,
                    "template": ['op.mathop("ln", {a.num})'],
                    "returnType": "num"
                },
                "log": {
                    "opcode": None,
                    "type": "reporter",
                    "args": [{"section": None, "name": "num", "type": "num"}],
                    "macro": True,
                    "template": ['op.mathop("log", {a.num})'],
                    "returnType": "num"
                },
                "e^": {
                    "opcode": None,
                    "type": "reporter",
                    "args": [{"section": None, "name": "num", "type": "num"}],
                    "macro": True,
                    "template": ['op.mathop("e ^", {a.num})'],
                    "returnType": "num"
                },
                "10^": {
                    "opcode": None,
                    "type": "reporter",
                    "args": [{"section": None, "name": "num", "type": "num"}],
                    "macro": True,
                    "template": ['op.mathop("10 ^", {a.num})'],
                    "returnType": "num"
                },
                "pow": {
                    "opcode": None,
                    "type": "reporter",
                    "args": [{"section":None, "name":"base", "type":"num"},
                             {"section":None, "name":"power", "type":"num"}],
                    "macro": True,
                    "template": [''], # NOTE wip
                    "returnType": "num"
                }
            },
            "var": {
                "set": {
                    "opcode": "data_setvariableto",
                    "type": "stack",
                    "args": [{"section":"fields", "name":"variable", "options":["..."]}, 
                             {"section":"inputs", "name":"value", "type":"num"}]
                },
                "modset": {
                    "opcode": None,
                    "type": "reporter",
                    "args": [{"section": None, "name": "var", "type": "var"},
                             {"section": None, "name": "val", "type": "num"}],
                    "macro": True,
                    "template": ['var.set(${var}, op.multiply(${var}, {val}))'],
                    "returnType": "num"
                },
                "change": {
                    "opcode": "data_changevariableby",
                    "type": "stack",
                    "args": [{"section":"fields", "name":"variable", "options":["..."]}, 
                             {"section":"inputs", "name":"value", "type":"num"}]
                },
                "show": {
                    "opcode": "data_showvariable",
                    "type": "stack",
                    "args": [{"section":"fields", "name":"variable", "options":["..."]}]
                },
                "hide": {
                    "opcode": "data_hidevariable",
                    "type": "stack",
                    "args": [{"section":"fields", "name":"variable", "options":["..."]}]
                }
            },
            "list": {
                "add": {
                    "opcode": "data_addtolist",
                    "type": "stack",
                    "args": [{"section":"fields", "name":"list", "options":["..."]}, 
                             {"section":"inputs", "name":"item", "type":"exp"}]
                },
                "delete": {
                    "opcode": "data_deleteoflist",
                    "type": "stack",
                    "args": [{"section":"fields", "name":"list", "options":["..."]}, 
                             {"section":"inputs", "name":"index", "type":"num"}]
                },
                "deleteall": {
                    "opcode": "data_deletealloflist",
                    "type": "stack",
                    "args": [{"section":"fields", "name":"list", "options":["..."]}]
                },
                "insert": {
                    "opcode": "data_insertatlist",
                    "type": "stack",
                    "args": [{"section":"fields", "name":"list", "options":["..."]}, 
                             {"section":"inputs", "name":"index", "type":"num"}, 
                             {"section":"inputs", "name":"item", "type":"exp"}]
                },
                "replace": {
                    "opcode": "data_replaceitemoflist",
                    "type": "stack",
                    "args": [{"section":"fields", "name":"list", "options":["..."]}, 
                             {"section":"inputs", "name":"index", "type":"num"}, 
                             {"section":"inputs", "name":"item", "type":"exp"}]
                },
                "get": {
                    "opcode": "data_itemoflist",
                    "type": "reporter",
                    "args": [{"section":"fields", "name":"list", "options":["..."]}, 
                             {"section":"inputs", "name":"index", "type":"num"}]
                },
                "getindex": {
                    "opcode": "data_itemnumoflist",
                    "type": "reporter",
                    "args": [{"section":"fields", "name":"list", "options":["..."]}, 
                             {"section":"inputs", "name":"item", "type":"exp"}]
                },
                "length": {
                    "opcode": "data_lengthoflist",
                    "type": "reporter",
                    "args": [{"section":"fields", "name":"list", "options":["..."]}]
                },
                "contains": {
                    "opcode": "data_listcontainsitem",
                    "type": "reporter",
                    "args": [{"section":"fields", "name":"list", "options":["..."]}, 
                             {"section":"inputs", "name":"item", "type":"exp"}]
                },
                "show": {
                    "opcode": "data_showlist",
                    "type": "stack",
                    "args": [{"section":"fields", "name":"list", "options":["..."]}]
                },
                "hide": {
                    "opcode": "data_hidelist",
                    "type": "stack",
                    "args": [{"section":"fields", "name":"list", "options":["..."]}]
                }
            },
            "func": {
                "funcargbool": {
                    "opcode": "argument_reporter_boolean",
                    "type": "reporter",
                    "args": [{"section":"fields", "name":"value", "options":["..."]}]
                },
                "funcargexp": {
                    "opcode": "argument_reporter_string_number",
                    "type": "reporter",
                    "args": [{"section":"fields", "name":"value", "options":["..."]}]
                },
                "return": {
                    "opcode": None,
                    "type": "cap",
                    "args": ["__all__"],
                    "macro": True,
                    "template": ['lists.add(@l:{function})\ncontrol.stop("this script")'] # Create a list of items to be added to the ast, allowing it to return returned values by inserting return deletion after control.stop
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
                    "args": [{"section":"inputs", "name":"color", "type":"num"}]
                },
                "change": {
                    "opcode": "pen_changePenColorParamBy",
                    "type": "stack",
                    "args": [{"section":"fields", "name":"color_param", "options":["color","saturation","brightness","transparency"]}, 
                             {"section":"inputs", "name":"value", "type":"num"}]
                },
                "set": {
                    "opcode": "pen_setPenColorParamTo",
                    "type": "stack",
                    "args": [{"section":"inputs", "name":"color_param", "type":"menu:pen_menu"}, 
                             {"section":"inputs", "name":"value", "type":"num"}]
                },
                "size": {
                    "change": {
                        "opcode": "pen_changePenSizeBy",
                        "type": "stack",
                        "args": [{"section":"inputs", "name":"size", "type":"num"}]
                    },
                    "set": {
                        "opcode": "pen_setPenSizeTo",
                        "type": "stack",
                        "args": [{"section":"inputs", "name":"size", "type":"num"}]
                    },
                },
                "shade": {
                    "set": {
                        "opcode": "pen_setPenShadeToNumber",
                        "type": "stack",
                        "args": [{"section":"inputs", "name":"shade", "type":"num"}]
                    },
                    "changeshade": {
                        "opcode": "pen_changePenShadeBy",
                        "type": "stack",
                        "args": [{"section":"inputs", "name":"shade", "type":"num"}]
                    }
                }
            },
            "casting": {
                "tonum": {
                    "opcode": None,
                    "type": "reporter",
                    "args": [{"section": None, "name": "val", "type": "exp"}],
                    "macro": True,
                    "template": ['{val}'],
                    "returnType": "num"
                },
                "tostr": {
                    "opcode": None,
                    "type": "reporter",
                    "args": [{"section": None, "name": "val", "type": "exp"}],
                    "macro": True,
                    "template": ['{val}'],
                    "returnType": "str"
                },
                "tobool": {
                    "opcode": None,
                    "type": "reporter",
                    "args": [{"section": None, "name": "val", "type": "exp"}],
                    "macro": True,
                    "template": ['{val}'],
                    "returnType": "bool"
                },
            },
            "sys": {
                "setup":{
                    "opcode": "sys_setup",
                    "type": "hat",
                    "args": [],
                },
                "load": {
                    "opcode": "sys_load",
                    "type": "stack",
                    "args": [{"section": None, "name":"filepath", "type":"str"}], # load("data.txt")
                },
                "create": {
                    "opcode": "sys_create",
                    "type": "stack",
                    "args": [{"section": None, "name":"type", "type":"str"},
                             {"section": None, "name":"instance", "type":"exp"},
                             {"section": None, "name":"data", "type":"exp"}], # create(type: public, @l:bazinga, data: "stuff\nstuff\nstuff") or data: load("data.txt") ... create(type: public, @d:costumes, data: load("costumes.json"))
                },
                "import": {
                    "opcode": "sys_import",
                    "type": "stack",
                    "args": [{"section": None, "name":"filepath", "type":"str"}], # import("costume.png")
                },
                "alias": {
                    "opcode": "sys_alias",
                    "type": "stack",
                    "args": [{"section": None, "name":"cmdPath", "type":"str"},
                             {"section": None, "name":"alias", "type":"str"}],
                }
            },
            "const": {
                "true": {
                    "opcode": None,
                    "type": "reporter",
                    "args": [],
                    "macro": True,
                    "template": ['op.equals(1,1)']
                },
                "false": {
                    "opcode": None,
                    "type": "reporter",
                    "args": [],
                    "macro": True,
                    "template": ['op.equals(1,0)']
                },
                "pi": {
                    "opcode": None,
                    "type": "reporter",
                    "args": [],
                    "macro": True,
                    "template": ['3.141592653589793']
                },
                "e": {
                    "opcode": None,
                    "type": "reporter",
                    "args": [],
                    "macro": True,
                    "template": ['2.718281828459045']
                },
                "phi": {
                    "opcode": None,
                    "type": "reporter",
                    "args": [],
                    "macro": True,
                    "template": ['1.618033988749895']
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
        self.aliases: Dict[str, str] = {}


    def get_command(self, command: str) -> Optional[CommandInfo]:
        """
        Returns the command dictionary given a command reference

        Args:
          command (str): Command reference (e.g. "motion.move")

        Returns:
          command (dict): Command dictionary (or None if not found)
        """

        # Check for alias
        while command in self.aliases:
            command = self.aliases[command]

        # Split the command into keys
        keys = command.split(".")
        
        # Get the command by traversing the dictionary
        result: Any = self.commands
        for key in keys:
            result = result.get(key, None)

        if not result:
            return None

        return result