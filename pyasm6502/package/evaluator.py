import math
from typing import List, Tuple, Union, Dict, Callable, Any

from .datastructures import AssemblerError, Token

# Forward declaration for type hinting
class Assembler6502:
    pass

# --- Custom Functions ---
def _is_number(value: Any) -> int:
    """Check if a value is a number (int or float). Returns 1 if true, 0 if false."""
    return 1 if isinstance(value, (int, float)) else 0

def _is_list(value: Any) -> int:
    """Check if a value is a list. Returns 1 if true, 0 if false."""
    return 1 if isinstance(value, list) else 0

def _is_string(value: Any) -> int:
    """Check if a value is a string. Returns 1 if true, 0 if false."""
    return 1 if isinstance(value, str) else 0

def _len(value: Any) -> int:
    """Get the length of a value (string, list, etc.)."""
    if hasattr(value, '__len__'):
        return len(value)
    else:
        raise ValueError(f"Object of type {type(value).__name__} has no length")

def _address(symbol_name: Any) -> int:
    """Get the address of a symbol. For now, just return the value itself."""
    # In ACME, addr() returns the symbol's address/value
    # For the math1.a test, addr(abcdef) == abcdef should be true
    return int(symbol_name)

def _addr(symbol_name: Any) -> int:
    """Alias for address() function."""
    return _address(symbol_name)

# --- Built-in Functions ---
BUILTIN_FUNCTIONS: Dict[str, Callable[..., Any]] = {
    'sin': math.sin,
    'cos': math.cos,
    'tan': math.tan,
    'arcsin': math.asin,
    'arccos': math.acos,
    'arctan': math.atan,
    'int': int,
    'float': float,
    'is_number': _is_number,
    'is_list': _is_list,
    'is_string': _is_string,
    'len': _len,
    # 'address' and 'addr' handled specially in parser to access asm symbol table
}

def parse_number(token: Token) -> Union[int, float]:
    """Parse a numeric token and return its value."""
    if token.type == 'HEX_NUMBER':
        if token.value.startswith('0x'):
            return int(token.value[2:], 16)
        else:
            return int(token.value[1:], 16)  # Skip '
    elif token.type == 'BIN_NUMBER':
        if token.value.startswith('0b'):
            binary_str = token.value[2:]
        else:
            binary_str = token.value[1:]  # Skip '%'
        binary_str = binary_str.replace('.', '0').replace('#', '1')
        return int(binary_str, 2)
    elif token.type == 'OCT_NUMBER':
        return int(token.value[1:], 8)  # Skip '&'
    elif token.type == 'DEC_NUMBER':
        if '.' in token.value:
            return float(token.value)
        else:
            return int(token.value)
    elif token.type == 'CHAR':
        char_val = token.value[1:-1]
        if len(char_val) == 1:
            return ord(char_val)
        elif len(char_val) <= 4:
            value = 0
            for i, char in enumerate(reversed(char_val)):
                value |= ord(char) << (i * 8)
            return value
        else:
            raise AssemblerError(f"Character constant too long: {token.value}", token.line, filename=asm.current_filename)
    else:
        raise AssemblerError(f"Invalid number: {token.value}", token.line, filename=asm.current_filename)

def evaluate_expression(asm: 'Assembler6502', tokens: List[Token], start: int = 0) -> Tuple[Union[int, float], int]:
    """Evaluate an expression and return (value, tokens_consumed)."""
    return _parse_or_expression(asm, tokens, start)

def _parse_or_expression(asm: 'Assembler6502', tokens: List[Token], start: int) -> Tuple[Union[int, float], int]:
    left, consumed = _parse_xor_expression(asm, tokens, start)
    while start + consumed < len(tokens) and tokens[start + consumed].type == 'OR':
        right, right_consumed = _parse_xor_expression(asm, tokens, start + consumed + 1)
        left = int(left) | int(right)
        consumed += 1 + right_consumed
    return left, consumed

def _parse_xor_expression(asm: 'Assembler6502', tokens: List[Token], start: int) -> Tuple[Union[int, float], int]:
    left, consumed = _parse_and_expression(asm, tokens, start)
    while start + consumed < len(tokens):
        token = tokens[start + consumed]
        if token.type == 'XOR' or token.type == 'CARET':
            # Handle both explicit XOR tokens and CARET (^ is XOR in ACME)
            right, right_consumed = _parse_and_expression(asm, tokens, start + consumed + 1)
            left = int(left) ^ int(right)
            consumed += 1 + right_consumed
        else:
            break
    return left, consumed

def _parse_and_expression(asm: 'Assembler6502', tokens: List[Token], start: int) -> Tuple[Union[int, float], int]:
    left, consumed = _parse_equality_expression(asm, tokens, start)
    while start + consumed < len(tokens) and tokens[start + consumed].type == 'AND':
        right, right_consumed = _parse_equality_expression(asm, tokens, start + consumed + 1)
        left = int(left) & int(right)
        consumed += 1 + right_consumed
    return left, consumed

def _parse_equality_expression(asm: 'Assembler6502', tokens: List[Token], start: int) -> Tuple[Union[int, float], int]:
    left, consumed = _parse_comparison_expression(asm, tokens, start)
    if start + consumed < len(tokens):
        token = tokens[start + consumed]
        if token.type == 'EQUAL_EQUAL' or token.type == 'EQUALS':
            # Right-associative: parse the entire remaining expression as right operand
            right, right_consumed = _parse_equality_expression(asm, tokens, start + consumed + 1)
            left = 1 if left == right else 0
            consumed += 1 + right_consumed
        elif token.type == 'NOT_EQUAL':
            # Right-associative: parse the entire remaining expression as right operand
            right, right_consumed = _parse_equality_expression(asm, tokens, start + consumed + 1)
            left = 1 if left != right else 0
            consumed += 1 + right_consumed
    return left, consumed

def _parse_comparison_expression(asm: 'Assembler6502', tokens: List[Token], start: int) -> Tuple[Union[int, float], int]:
    left, consumed = _parse_byte_unary_expression(asm, tokens, start)
    while start + consumed < len(tokens):
        token = tokens[start + consumed]
        if token.type == 'LESS_THAN':
            right, right_consumed = _parse_byte_unary_expression(asm, tokens, start + consumed + 1)
            left = 1 if left < right else 0
            consumed += 1 + right_consumed
        elif token.type == 'LESS_EQUAL':
            right, right_consumed = _parse_byte_unary_expression(asm, tokens, start + consumed + 1)
            left = 1 if left <= right else 0
            consumed += 1 + right_consumed
        elif token.type == 'GREATER_THAN':
            right, right_consumed = _parse_byte_unary_expression(asm, tokens, start + consumed + 1)
            left = 1 if left > right else 0
            consumed += 1 + right_consumed
        elif token.type == 'GREATER_EQUAL':
            right, right_consumed = _parse_byte_unary_expression(asm, tokens, start + consumed + 1)
            left = 1 if left >= right else 0
            consumed += 1 + right_consumed
        else:
            break
    return left, consumed

def _parse_byte_unary_expression(asm: 'Assembler6502', tokens: List[Token], start: int) -> Tuple[Union[int, float], int]:
    """Parse unary byte operators (<, >, ^) which have lower precedence than shift operators"""
    if start >= len(tokens):
        raise AssemblerError("Expected expression", asm.current_line, getattr(asm, 'current_line_text', ''), asm.current_filename)
    token = tokens[start]
    if token.type == 'LESS_THAN':
        # Parse shift expressions first to give shift operators higher precedence
        value, consumed = _parse_shift_expression(asm, tokens, start + 1)
        return int(value) & 0xFF, consumed + 1
    elif token.type == 'GREATER_THAN':
        # Parse shift expressions first to give shift operators higher precedence
        value, consumed = _parse_shift_expression(asm, tokens, start + 1)
        return (int(value) >> 8) & 0xFF, consumed + 1
    elif token.type == 'CARET' and not _is_binary_caret_context(tokens, start):
        # This is a unary bank byte operator (^value) - parse shifts first
        value, consumed = _parse_shift_expression(asm, tokens, start + 1)
        return (int(value) >> 16) & 0xFF, consumed + 1
    else:
        return _parse_shift_expression(asm, tokens, start)

def _parse_shift_expression(asm: 'Assembler6502', tokens: List[Token], start: int) -> Tuple[Union[int, float], int]:
    left, consumed = _parse_additive_expression(asm, tokens, start)
    while start + consumed < len(tokens):
        token = tokens[start + consumed]
        if token.type == 'LEFT_SHIFT':
            right, right_consumed = _parse_additive_expression(asm, tokens, start + consumed + 1)
            if isinstance(left, float):
                # For floating point left operand, left shift is multiplication by 2^right
                left = left * (2 ** right)
            else:
                # For integer left operand, always use integer shift
                left = int(left) << int(right)
            consumed += 1 + right_consumed
        elif token.type == 'RIGHT_SHIFT':
            right, right_consumed = _parse_additive_expression(asm, tokens, start + consumed + 1)
            if isinstance(left, float):
                # For floating point left operand, right shift is division by 2^right
                left = left / (2 ** right)
            else:
                # For integer left operand, always use integer shift
                left = int(left) >> int(right)
            consumed += 1 + right_consumed
        elif token.type == 'LOGICAL_RIGHT_SHIFT':
            right, right_consumed = _parse_additive_expression(asm, tokens, start + consumed + 1)
            left = (int(left) % (1 << 32)) >> int(right)
            consumed += 1 + right_consumed
        else:
            break
    return left, consumed

def _parse_additive_expression(asm: 'Assembler6502', tokens: List[Token], start: int) -> Tuple[Union[int, float], int]:
    left, consumed = _parse_multiplicative_expression(asm, tokens, start)
    while start + consumed < len(tokens):
        token = tokens[start + consumed]
        if token.type == 'PLUS' or (token.type == 'IDENTIFIER' and token.value == '+'):
            right, right_consumed = _parse_multiplicative_expression(asm, tokens, start + consumed + 1)
            left = left + right
            consumed += 1 + right_consumed
        elif token.type == 'MINUS' or (token.type == 'IDENTIFIER' and token.value == '-'):
            right, right_consumed = _parse_multiplicative_expression(asm, tokens, start + consumed + 1)
            left = left - right
            consumed += 1 + right_consumed
        else:
            break
    return left, consumed

def _parse_multiplicative_expression(asm: 'Assembler6502', tokens: List[Token], start: int) -> Tuple[Union[int, float], int]:
    left, consumed = _parse_power_expression(asm, tokens, start)
    while start + consumed < len(tokens):
        token = tokens[start + consumed]
        if token.type == 'STAR': # Changed from MULTIPLY to STAR for '*' as multiplication
            right, right_consumed = _parse_power_expression(asm, tokens, start + consumed + 1)
            left = left * right
            consumed += 1 + right_consumed
        elif token.type == 'DIVIDE':
            right, right_consumed = _parse_power_expression(asm, tokens, start + consumed + 1)
            if isinstance(left, float) or isinstance(right, float):
                left = left / right
            else:
                left = left // right
            consumed += 1 + right_consumed
        elif token.type == 'DIV':
            right, right_consumed = _parse_power_expression(asm, tokens, start + consumed + 1)
            # DIV always performs integer division (truncation towards zero)
            left = int(left) // int(right)
            consumed += 1 + right_consumed
        elif token.type == 'MODULO' or token.type == 'MOD':
            right, right_consumed = _parse_power_expression(asm, tokens, start + consumed + 1)
            left = left % right
            consumed += 1 + right_consumed
        else:
            break
    return left, consumed

def _parse_unary_expression(asm: 'Assembler6502', tokens: List[Token], start: int) -> Tuple[Union[int, float], int]:
    if start >= len(tokens):
        raise AssemblerError("Expected expression", asm.current_line, getattr(asm, 'current_line_text', ''), asm.current_filename)
    token = tokens[start]
    if token.type == 'MINUS' or (token.type == 'IDENTIFIER' and token.value == '-'):
        value, consumed = _parse_power_expression(asm, tokens, start + 1)
        return -value, consumed + 1
    elif token.type == 'PLUS' or (token.type == 'IDENTIFIER' and token.value == '+'):
        value, consumed = _parse_power_expression(asm, tokens, start + 1)
        return value, consumed + 1
    elif token.type == 'NOT':
        value, consumed = _parse_primary_expression(asm, tokens, start + 1)
        return ~int(value), consumed + 1
    else:
        return _parse_primary_expression(asm, tokens, start)

def _parse_power_expression(asm: 'Assembler6502', tokens: List[Token], start: int) -> Tuple[Union[int, float], int]:
    left, consumed = _parse_unary_expression(asm, tokens, start)
    # Right-associative: if we find ^, parse the entire right side as power expression
    if start + consumed < len(tokens):
        token = tokens[start + consumed]
        if token.type == 'POWER' or token.type == 'CARET':
            # Handle ^ as power by default, XOR is handled at lower precedence level
            right, right_consumed = _parse_power_expression(asm, tokens, start + consumed + 1)
            left = left ** right
            consumed += 1 + right_consumed
    return left, consumed

def _is_binary_caret_context(tokens: List[Token], pos: int) -> bool:
    """Check if ^ at position is binary (XOR) rather than unary (bank byte)"""
    # If there's a value before ^, it's likely binary
    return pos > 0 and tokens[pos - 1].type in ['NUMBER', 'DEC_NUMBER', 'HEX_NUMBER', 'BINARY_NUMBER', 'IDENTIFIER', 'RPAREN']

def _parse_primary_expression(asm: 'Assembler6502', tokens: List[Token], start: int) -> Tuple[Union[int, float], int]:
    if start >= len(tokens):
        raise AssemblerError("Expected expression", asm.current_line, getattr(asm, 'current_line_text', ''), asm.current_filename)
    token = tokens[start]

    if token.type == 'FUNCTION':
        func_name = token.value
        # Special-case functions requiring assembler context
        special_ctx_funcs = ['address', 'addr']
        if func_name not in BUILTIN_FUNCTIONS and func_name not in special_ctx_funcs:
            raise AssemblerError(f"Unknown function: {func_name}", token.line, filename=asm.current_filename)
        
        # Expect LPAREN
        if start + 1 >= len(tokens) or tokens[start + 1].type != 'LPAREN':
            raise AssemblerError(f"Expected '(' after function call {func_name}", token.line, filename=asm.current_filename)
        
        # Parse arguments
        args = []
        current_pos = start + 2
        consumed = 3  # Initialize consumed with default value
        if tokens[current_pos].type == 'RPAREN': # No arguments
            pass  # consumed already set to 3
        else:
            while True:
                arg_val, arg_consumed = evaluate_expression(asm, tokens, current_pos)
                args.append(arg_val)
                current_pos += arg_consumed
                if current_pos >= len(tokens):
                    raise AssemblerError("Missing closing parenthesis for function call", token.line, filename=asm.current_filename)
                
                next_token = tokens[current_pos]
                if next_token.type == 'RPAREN':
                    consumed = current_pos - start + 1
                    break
                elif next_token.type == 'COMMA':
                    current_pos += 1
                else:
                    raise AssemblerError(f"Expected ',' or ')' in function call arguments", next_token.line, filename=asm.current_filename)

        # Call function (with special handling for address/addr)
        if func_name in special_ctx_funcs:
            if len(args) != 1:
                raise AssemblerError(f"{func_name}() expects exactly one argument", token.line, filename=asm.current_filename)
            symbol_name = args[0]
            if isinstance(symbol_name, (int, float)):
                # If numeric passed, just return it
                return int(symbol_name), consumed
            if not isinstance(symbol_name, str):
                # Best effort: try to stringify
                symbol_name = str(symbol_name)
            symbol = asm.resolve_symbol(symbol_name)
            return (symbol.value if symbol else 0), consumed
        else:
            try:
                result = BUILTIN_FUNCTIONS[func_name](*args)
                return result, consumed
            except TypeError as e:
                raise AssemblerError(f"Invalid arguments for function {func_name}: {e}", token.line, filename=asm.current_filename)

    if token.type in ['HEX_NUMBER', 'BIN_NUMBER', 'OCT_NUMBER', 'DEC_NUMBER', 'CHAR']:
        return parse_number(token), 1
    elif token.type == 'STAR':
        return asm.pc, 1
    elif token.type == 'IDENTIFIER':
        # Check loop variables first
        if hasattr(asm, 'loop_processor') and token.value in asm.loop_processor.variables:
            return asm.loop_processor.get_variable(token.value), 1

        # Then check symbols
        symbol = asm.resolve_symbol(token.value)
        return symbol.value if symbol else 0, 1
    elif token.type == 'LPAREN':
        value, consumed = evaluate_expression(asm, tokens, start + 1)
        rparen_pos = start + 1 + consumed
        if rparen_pos < len(tokens) and tokens[rparen_pos].type == 'RPAREN':
            return value, consumed + 2
        else:
            raise AssemblerError("Missing closing parenthesis", asm.current_line, filename=asm.current_filename)
    # Handle unary operators in primary expression as a fallback
    elif token.type in ['NOT', 'MINUS', 'PLUS', 'LESS_THAN', 'GREATER_THAN', 'CARET']:
        return _parse_unary_expression(asm, tokens, start)
    else:
        raise AssemblerError(f"Invalid expression: {token.value}", token.line, filename=asm.current_filename)
