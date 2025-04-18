# Standard Library
from typing import Optional, List, Dict, TypedDict, Any, NotRequired

# Third Party

# Local

class CommandArg(TypedDict):
    section: str
    name: str
    type: Optional[str]
    options: Optional[List[str]]

class CommandInfo(TypedDict):
    name: str
    opcode: str
    type: str
    args: List[CommandArg]
    macro: Optional[str]
    template: Optional[List[str]]

class Token(TypedDict):
    name: str
    type: NotRequired[Optional[str]]
    value: Any
    
class ASTStack(TypedDict):
    opcode: str
    type: str
    args: Dict[CommandArg, Token]
    stack: Optional[List['ASTStack']]