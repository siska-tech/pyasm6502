"""
Text Conversion System for pyasm6502
Handles character encoding conversions (PetSCII, screen codes, etc.)
"""

from typing import Dict, List, Optional, Union


class TextConverter:
    """Manages text conversion tables and character encoding."""

    # Built-in conversion tables
    BUILTIN_TABLES = {
        'raw': None,  # No conversion (ASCII)
        'pet': 'petscii',  # PetSCII conversion
        'scr': 'screencode',  # C64 screen codes
    }

    def __init__(self):
        """Initialize the text converter with default tables."""
        self.current_table = 'raw'  # Default to raw ASCII
        self.custom_tables: Dict[str, List[int]] = {}
        self._init_builtin_tables()

    def _init_builtin_tables(self):
        """Initialize built-in conversion tables."""
        # PetSCII conversion table (simplified version)
        # Maps ASCII characters to PetSCII byte values
        petscii_table = list(range(256))  # Start with 1:1 mapping

        # Convert uppercase ASCII to PetSCII
        for i in range(65, 91):  # A-Z
            petscii_table[i] = i - 64  # Maps A-Z to 1-26

        # Convert lowercase ASCII to PetSCII
        for i in range(97, 123):  # a-z
            petscii_table[i] = i - 32  # Maps a-z to 65-90

        # Special characters
        petscii_table[64] = 0    # @ -> 0
        petscii_table[91] = 27   # [ -> 27
        petscii_table[92] = 28   # \ -> 28
        petscii_table[93] = 29   # ] -> 29
        petscii_table[94] = 30   # ^ -> 30
        petscii_table[95] = 31   # _ -> 31

        self.custom_tables['petscii'] = petscii_table

        # Screen code conversion table
        # Maps ASCII characters to C64 screen codes
        screen_table = list(range(256))  # Start with 1:1 mapping

        # Uppercase letters A-Z map to 1-26
        for i in range(65, 91):
            screen_table[i] = i - 64

        # Lowercase letters a-z map to 1-26 (same as uppercase)
        for i in range(97, 123):
            screen_table[i] = i - 96

        # Numbers 0-9 map to 48-57
        for i in range(48, 58):
            screen_table[i] = i - 48 + 16  # 0-9 -> 16-25

        # Space
        screen_table[32] = 32

        self.custom_tables['screencode'] = screen_table

    def set_conversion_table(self, table_name: str) -> bool:
        """Set the current conversion table."""
        if table_name in self.BUILTIN_TABLES:
            self.current_table = table_name
            return True
        elif table_name in self.custom_tables:
            self.current_table = table_name
            return True
        else:
            return False

    def get_current_table(self) -> str:
        """Get the name of the current conversion table."""
        return self.current_table

    def convert_string(self, text: str, table_override: Optional[str] = None) -> List[int]:
        """Convert a string using the specified or current conversion table."""
        table_name = table_override if table_override else self.current_table

        if table_name == 'raw' or self.BUILTIN_TABLES.get(table_name) is None:
            # Raw ASCII conversion
            return [ord(c) for c in text]

        # Look up the conversion table
        table_key = self.BUILTIN_TABLES.get(table_name, table_name)
        conversion_table = self.custom_tables.get(table_key, None)

        if conversion_table is None:
            # Fallback to raw ASCII
            return [ord(c) for c in text]

        # Apply conversion
        result = []
        for char in text:
            ascii_val = ord(char)
            if ascii_val < len(conversion_table):
                result.append(conversion_table[ascii_val])
            else:
                result.append(ascii_val)  # Fallback to ASCII value

        return result

    def convert_string_with_xor(self, text: str, xor_mask: int, table_override: Optional[str] = None) -> List[int]:
        """Convert a string and apply XOR mask to each byte."""
        converted = self.convert_string(text, table_override)
        return [(byte ^ xor_mask) & 0xFF for byte in converted]

    def load_custom_table(self, name: str, table_data: Union[List[int], str]) -> bool:
        """Load a custom conversion table."""
        if isinstance(table_data, str):
            # Assume it's a file path (for future implementation)
            # For now, just return False
            return False
        elif isinstance(table_data, list) and len(table_data) == 256:
            self.custom_tables[name] = table_data.copy()
            return True
        else:
            return False


# Global text converter instance
text_converter = TextConverter()