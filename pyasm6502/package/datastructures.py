from enum import Enum
from typing import Dict, Union

class OutputFormat(Enum):
    """Output file formats."""
    PLAIN = "plain"
    CBM = "cbm"
    APPLE = "apple"
    HEX = "hex"  # Intel HEX format


class AssemblerError(Exception):
    """Assembler error with line number information."""
    def __init__(self, message: str, line_num: int = 0, line_text: str = "", filename: str = ""):
        self.message = message
        self.line_num = line_num
        self.line_text = line_text
        self.filename = filename
        # Format filename display - show "unknown" if empty
        display_filename = filename if filename else "unknown"

        # Enhanced error message with code line display
        error_msg = f"Error - File {display_filename}, line {line_num}: {message}"
        if line_text.strip():
            error_msg += f"\n  {line_text.strip()}"
            # Add a pointer to highlight the error location
            error_msg += f"\n  {'^' * len(line_text.strip())}"

        super().__init__(error_msg)


class Token:
    """Represents a token in the assembly source."""
    def __init__(self, type_: str, value: str, line: int, column: int):
        self.type = type_
        self.value = value
        self.line = line
        self.column = column

    def __repr__(self):
        return f"Token({self.type}, '{self.value}', {self.line}:{self.column})"


class Symbol:
    """Symbol with type information (ACME compatible)."""
    def __init__(self, name: str, value: Union[int, float], is_address: bool = False, is_local: bool = False):
        self.name = name
        self.value = value
        self.is_address = is_address
        self.is_local = is_local


class Zone:
    """Zone for local symbol scoping."""
    def __init__(self, name: str = ""):
        self.name = name
        self.local_symbols: Dict[str, Symbol] = {}
