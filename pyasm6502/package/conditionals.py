"""
Conditional Assembly Processing for pyasm6502
Handles !if, !ifdef, !ifndef, !else, !fi conditional assembly blocks.
"""

from typing import List, Dict, Any, Optional, Tuple, Union
from .datastructures import AssemblerError, Token
from .evaluator import evaluate_expression

# Forward declaration for type hinting
class Assembler6502:
    pass

class ConditionalBlock:
    """Represents a conditional assembly block."""
    def __init__(self, condition_type: str, condition: Union[bool, str], start_line: int, uses_braces: bool = False):
        self.condition_type = condition_type  # 'if', 'ifdef', 'ifndef'
        self.condition = condition
        self.start_line = start_line
        self.has_else = False
        self.else_line: Optional[int] = None
        self.end_line: Optional[int] = None
        self.is_active = False  # Whether this block is currently being assembled
        self.uses_braces = uses_braces # ACME brace style: !if condition {

class ConditionalProcessor:
    """Handles conditional assembly processing."""

    def __init__(self):
        self.stack: List[ConditionalBlock] = []  # Stack of nested conditional blocks
        self.skip_level = 0  # How many levels deep we're skipping

    def is_skipping(self) -> bool:
        """Return True if we're currently skipping assembly."""
        return self.skip_level > 0

    def get_current_depth(self) -> int:
        """Get the current nesting depth."""
        return len(self.stack)

    def process_if_directive(self, asm: 'Assembler6502', tokens: List[Token], start: int) -> Tuple[bool, int]:
        """
        Process !if directive.
        Returns (is_true, consumed_tokens).
        """
        if start >= len(tokens):
            raise AssemblerError("!if requires a condition expression", asm.current_line)

        # Evaluate the condition expression
        condition_value, consumed = evaluate_expression(asm, tokens, start)

        # Check for optional opening brace
        uses_braces = False
        brace_consumed = 0
        next_token_idx = start + consumed
        if next_token_idx < len(tokens) and tokens[next_token_idx].type == 'LBRACE':
            uses_braces = True
            brace_consumed = 1

        # Convert to boolean (ACME treats non-zero as true)
        is_true = bool(condition_value) if condition_value != 0 else False

        # Create new conditional block
        block = ConditionalBlock('if', is_true, asm.current_line, uses_braces=uses_braces)

        # Determine if we should assemble this block
        if self.is_skipping():
            # We're already skipping - increment skip level regardless of condition
            block.is_active = False
            self.skip_level += 1
        else:
            # We're not skipping - check condition
            block.is_active = is_true
            if not is_true:
                self.skip_level = 1

        self.stack.append(block)
        return block.is_active, consumed + brace_consumed

    def process_ifdef_directive(self, asm: 'Assembler6502', tokens: List[Token], start: int) -> Tuple[bool, int]:
        """
        Process !ifdef directive.
        Returns (is_true, consumed_tokens).
        """
        if start >= len(tokens) or tokens[start].type != 'IDENTIFIER':
            raise AssemblerError("!ifdef requires a symbol name", asm.current_line)

        symbol_name = tokens[start].value
        consumed = 1

        # Check for optional opening brace
        uses_braces = False
        brace_consumed = 0
        next_token_idx = start + consumed
        if next_token_idx < len(tokens) and tokens[next_token_idx].type == 'LBRACE':
            uses_braces = True
            brace_consumed = 1

        # Check if symbol exists in any scope
        is_defined = self._is_symbol_defined(asm, symbol_name)

        # Create new conditional block
        block = ConditionalBlock('ifdef', symbol_name, asm.current_line, uses_braces=uses_braces)

        # Determine if we should assemble this block
        if self.is_skipping():
            # We're already skipping - increment skip level regardless of condition
            block.is_active = False
            self.skip_level += 1
        else:
            # We're not skipping - check condition
            block.is_active = is_defined
            if not is_defined:
                self.skip_level = 1

        self.stack.append(block)
        return block.is_active, consumed + brace_consumed

    def process_ifndef_directive(self, asm: 'Assembler6502', tokens: List[Token], start: int) -> Tuple[bool, int]:
        """
        Process !ifndef directive.
        Returns (is_true, consumed_tokens).
        """
        if start >= len(tokens) or tokens[start].type != 'IDENTIFIER':
            raise AssemblerError("!ifndef requires a symbol name", asm.current_line)

        symbol_name = tokens[start].value
        consumed = 1

        # Check for optional opening brace
        uses_braces = False
        brace_consumed = 0
        next_token_idx = start + consumed
        if next_token_idx < len(tokens) and tokens[next_token_idx].type == 'LBRACE':
            uses_braces = True
            brace_consumed = 1

        # Check if symbol exists in any scope (opposite of ifdef)
        is_defined = self._is_symbol_defined(asm, symbol_name)
        is_not_defined = not is_defined

        # Create new conditional block
        block = ConditionalBlock('ifndef', symbol_name, asm.current_line, uses_braces=uses_braces)

        # Determine if we should assemble this block
        if self.is_skipping():
            # We're already skipping - increment skip level regardless of condition
            block.is_active = False
            self.skip_level += 1
        else:
            # We're not skipping - check condition
            block.is_active = is_not_defined
            if not is_not_defined:
                self.skip_level = 1

        self.stack.append(block)
        return block.is_active, consumed + brace_consumed

    def process_else_directive(self, asm: 'Assembler6502') -> bool:
        """
        Process !else directive.
        Returns True if we should assemble the else block.
        """
        if not self.stack:
            raise AssemblerError("!else without matching !if/!ifdef/!ifndef", asm.current_line)

        current_block = self.stack[-1]

        if current_block.uses_braces:
            raise AssemblerError("!else cannot be used with brace-style conditionals", asm.current_line)

        if current_block.has_else:
            raise AssemblerError("Multiple !else clauses in conditional block", asm.current_line)

        current_block.has_else = True
        current_block.else_line = asm.current_line

        # Switch the active state if we're at the current level
        if len(self.stack) == 1:  # Top level conditional
            if self.skip_level == 1:
                # We were skipping the if block, now assemble else block
                current_block.is_active = True
                self.skip_level = 0
            elif self.skip_level == 0:
                # We were assembling the if block, now skip else block
                current_block.is_active = False
                self.skip_level = 1
        # For nested blocks, don't change anything - parent controls skipping

        return current_block.is_active

    def process_fi_directive(self, asm: 'Assembler6502') -> None:
        """Process !fi directive (end of conditional block)."""
        if not self.stack:
            raise AssemblerError("!fi without matching !if/!ifdef/!ifndef", asm.current_line)

        current_block = self.stack[-1]

        if current_block.uses_braces:
            raise AssemblerError("Expected '}' to close conditional block started with '{'", asm.current_line)

        self.stack.pop()
        current_block.end_line = asm.current_line

        # Adjust skip level
        if len(self.stack) == 0:
            # Closing top-level conditional
            self.skip_level = 0
        elif self.skip_level > 0:
            # Closing nested conditional while skipping
            self.skip_level -= 1

    def process_rbrace_directive(self, asm: 'Assembler6502') -> None:
        """Process a '}' token as a potential end of a conditional block."""
        if not self.stack or not self.stack[-1].uses_braces:
            raise AssemblerError("Unexpected '}'", asm.current_line)

        current_block = self.stack.pop()
        current_block.end_line = asm.current_line

        # Adjust skip level
        if len(self.stack) == 0:
            # Closing top-level conditional
            self.skip_level = 0
        elif self.skip_level > 0:
            # Closing nested conditional while skipping
            self.skip_level -= 1

    def _is_symbol_defined(self, asm: 'Assembler6502', symbol_name: str) -> bool:
        """Check if a symbol is defined in any scope."""
        # Check global symbols
        if symbol_name in asm.global_symbols:
            return True

        # Check current zone's local symbols
        current_zone = asm.zones[asm.current_zone]
        if symbol_name in current_zone.local_symbols:
            return True

        # Check cheap locals (@ symbols)
        if symbol_name in asm.cheap_locals:
            return True

        return False

    def validate_nesting(self, asm: 'Assembler6502') -> None:
        """Validate that all conditional blocks are properly closed."""
        if self.stack:
            unclosed = self.stack[-1]
            raise AssemblerError(
                f"Unclosed conditional block starting at line {unclosed.start_line}",
                asm.current_line
            )

    def reset(self) -> None:
        """Reset the conditional processor state (for new assembly passes)."""
        self.stack.clear()
        self.skip_level = 0