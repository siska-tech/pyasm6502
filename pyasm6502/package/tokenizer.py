from typing import List, Dict
from .datastructures import Token

def _is_operator_context(tokens: List[Token]) -> bool:
    """Check if we're in an operator context (between values) for AND/OR/XOR"""
    if not tokens:
        return False

    # Get the last token type
    last_token = tokens[-1]

    # If the previous token is a value or closing paren, we're in operator context
    value_tokens = {
        'IDENTIFIER', 'HEX_NUMBER', 'BIN_NUMBER', 'OCT_NUMBER',
        'DEC_NUMBER', 'CHAR', 'RPAREN', 'STAR'
    }

    return last_token.type in value_tokens

def tokenize(line: str, line_num: int, instructions: Dict) -> List[Token]:
    """Tokenize a line of assembly source."""
    tokens = []
    i = 0
    column = 0

    # Remove comments (both ; and //)
    comment_pos = line.find(';')
    comment_pos2 = line.find('//')
    if comment_pos != -1 and comment_pos2 != -1:
        comment_pos = min(comment_pos, comment_pos2)
    elif comment_pos2 != -1:
        comment_pos = comment_pos2

    if comment_pos != -1:
        line = line[:comment_pos]

    line = line.strip()
    if not line:
        return tokens

    prev_token_type = None
    while i < len(line):
        column = i
        char = line[i]

        # Skip whitespace
        if char.isspace():
            i += 1
            continue

        # Labels and identifiers
        if char.isalpha() or char == '_':
            start = i
            while i < len(line) and (line[i].isalnum() or line[i] == '_'):
                i += 1

            identifier = line[start:i]

            # Check if it's a label or a function call first
            upper_id = identifier.upper()
            if i < len(line) and line[i] == ':':
                tokens.append(Token('LABEL', identifier, line_num, column))
                i += 1  # Skip colon
            elif i < len(line) and line[i] == '(':
                tokens.append(Token('FUNCTION', identifier, line_num, column))
                # The LPAREN will be tokenized in the next iteration
            else:
                # Special handling for keywords that can be both instructions and operators
                # For AND, OR, XOR: use context to determine if it's an operator or instruction
                if upper_id in ['AND', 'OR', 'XOR'] and _is_operator_context(tokens):
                    # In operator context (between values), treat as logical operator
                    tokens.append(Token(upper_id, upper_id, line_num, column))
                # Check if it's an instruction first (higher priority than other keywords)
                elif upper_id in instructions:
                    tokens.append(Token('INSTRUCTION', upper_id, line_num, column))
                # Then check for keywords (only if not an instruction)
                elif upper_id == 'NOT':
                    tokens.append(Token('NOT', upper_id, line_num, column))
                elif upper_id == 'AND':
                    tokens.append(Token('AND', upper_id, line_num, column))
                elif upper_id == 'OR':
                    tokens.append(Token('OR', upper_id, line_num, column))
                elif upper_id == 'XOR':
                    tokens.append(Token('XOR', upper_id, line_num, column))
                elif upper_id == 'DIV':
                    tokens.append(Token('DIV', upper_id, line_num, column))
                elif upper_id == 'MOD':
                    tokens.append(Token('MOD', upper_id, line_num, column))
                else:
                    tokens.append(Token('IDENTIFIER', identifier, line_num, column))

        # Numbers (hex, decimal, binary)
        elif char.isdigit() or char == '$':
            start = i
            if char == '$':  # Hexadecimal
                i += 1
                while i < len(line) and line[i] in '0123456789ABCDEFabcdef':
                    i += 1
                tokens.append(Token('HEX_NUMBER', line[start:i], line_num, column))
            elif char == '0' and i + 1 < len(line) and line[i + 1] == 'x':  # 0x hexadecimal
                i += 2
                while i < len(line) and line[i] in '0123456789ABCDEFabcdef':
                    i += 1
                tokens.append(Token('HEX_NUMBER', line[start:i], line_num, column))
            elif char == '0' and i + 1 < len(line) and line[i + 1] == 'b':  # 0b binary
                i += 2  # Skip '0b'
                while i < len(line) and line[i] in '01.#':  # ACME supports . and # for 0 and 1
                    i += 1
                tokens.append(Token('BIN_NUMBER', line[start:i], line_num, column))
            else:  # Decimal
                while i < len(line) and (line[i].isdigit() or line[i] == '.'):
                    i += 1
                tokens.append(Token('DEC_NUMBER', line[start:i], line_num, column))
        # Handle % separately for context-sensitive parsing
        elif char == '%':
            # 前のトークンが値系か判定する関数
            def _is_prev_value_token(t):
                return t in (
                    'IDENTIFIER','HEX_NUMBER','BIN_NUMBER','OCT_NUMBER',
                    'DEC_NUMBER','CHAR','RPAREN','STAR'
                )

            # % の次が 0-1 かつ前トークンが値でないときのみ 2進数
            if (i + 1 < len(line)
                and line[i + 1] in '01.#'
                and not _is_prev_value_token(prev_token_type)):

                start = i
                i += 1  # Skip '%'
                while i < len(line) and line[i] in '01.#':  # ACME supports . and # for 0 and 1
                    i += 1

                # % のあとに数字が1文字も無ければ MODULO として扱う
                if i == start + 1:
                    tokens.append(Token('MODULO', '%', line_num, column))
                else:
                    tokens.append(Token('BIN_NUMBER', line[start:i], line_num, column))
            else:
                tokens.append(Token('MODULO', '%', line_num, column))
                i += 1

        # String literals and character constants
        elif char == '"' or char == "'":
            quote_char = char
            start = i
            i += 1
            while i < len(line) and line[i] != quote_char:
                if line[i] == '\\':  # Escape sequence
                    i += 2 if i + 1 < len(line) else 1
                else:
                    i += 1
            if i < len(line):
                i += 1  # Skip closing quote

            if quote_char == "'":
                tokens.append(Token('CHAR', line[start:i], line_num, column))
            else:
                tokens.append(Token('STRING', line[start:i], line_num, column))

        # Anonymous labels and cheap locals
        elif char in ['+', '-', '@']:
            start = i
            if char in ['+', '-']:
                # Check if this is a macro call first (single + or - followed by a letter)
                if char == '+' and i + 1 < len(line) and line[i + 1].isalpha():
                    # Macro call - read the macro name
                    i += 1  # Skip +
                    while i < len(line) and (line[i].isalnum() or line[i] == '_'):
                        i += 1
                    macro_call = line[start:i]
                    tokens.append(Token('MACRO_CALL', macro_call, line_num, column))
                else:
                    # Check if this is an operator in expression context
                    # If preceded by a value token or followed by non-repeated symbol, treat as operator
                    is_operator = False

                    # Check if previous token suggests operator context
                    if tokens and tokens[-1].type in ['DEC_NUMBER', 'HEX_NUMBER', 'IDENTIFIER', 'RPAREN']:
                        is_operator = True

                    # Or if followed by non-repeated symbol (not anonymous label)
                    elif i + 1 < len(line) and line[i + 1] != char:
                        is_operator = True

                    if is_operator:
                        if char == '+':
                            tokens.append(Token('PLUS', char, line_num, column))
                        else:
                            tokens.append(Token('MINUS', char, line_num, column))
                        i += 1
                        continue

                    # Anonymous labels: +, ++, +++, -, --, ---
                    while i < len(line) and line[i] == char:
                        i += 1
                    label = line[start:i]
                    # Check if it's a label definition (followed by :) or reference
                    if i < len(line) and line[i] == ':':
                        tokens.append(Token('LABEL', label, line_num, column))
                        i += 1  # Skip colon
                    else:
                        tokens.append(Token('IDENTIFIER', label, line_num, column))
            else:  # @
                # Cheap local symbol
                i += 1
                while i < len(line) and (line[i].isalnum() or line[i] == '_'):
                    i += 1
                identifier = line[start:i]
                # Check if it's a label
                if i < len(line) and line[i] == ':':
                    tokens.append(Token('LABEL', identifier, line_num, column))
                    i += 1  # Skip colon
                else:
                    tokens.append(Token('IDENTIFIER', identifier, line_num, column))

        # Operators and punctuation
        elif char == '*':
            if i + 1 < len(line) and line[i+1] == '*':
                tokens.append(Token('POWER', '**', line_num, column))
                i += 2
            else:
                tokens.append(Token('STAR', char, line_num, column))
                i += 1
        elif char == '=':
            if i + 1 < len(line) and line[i+1] == '=':
                tokens.append(Token('EQUAL_EQUAL', '==', line_num, column))
                i += 2
            else:
                tokens.append(Token('EQUALS', char, line_num, column))
                i += 1
        elif char == '!':
            if i + 1 < len(line) and line[i+1] == '=':
                tokens.append(Token('NOT_EQUAL', '!=', line_num, column))
                i += 2
            elif i + 1 < len(line) and (line[i+1].isalnum() or line[i+1] == '_'):
                start = i
                i += 1
                while i < len(line) and (line[i].isalnum() or line[i] == '_'):
                    i += 1
                tokens.append(Token('ACME_DIRECTIVE', line[start:i], line_num, column))
            else:
                tokens.append(Token('NOT', char, line_num, column))
                i += 1
        elif char == '<':
            if i + 1 < len(line) and line[i+1] == '<':
                tokens.append(Token('LEFT_SHIFT', '<<', line_num, column))
                i += 2
            elif i + 1 < len(line) and line[i+1] == '=':
                tokens.append(Token('LESS_EQUAL', '<=', line_num, column))
                i += 2
            elif i + 1 < len(line) and line[i+1] == '>':
                tokens.append(Token('NOT_EQUAL', '<>', line_num, column))
                i += 2
            else:
                tokens.append(Token('LESS_THAN', char, line_num, column))
                i += 1
        elif char == '>':
            if i + 2 < len(line) and line[i+1:i+3] == '>>':
                tokens.append(Token('LOGICAL_RIGHT_SHIFT', '>>>', line_num, column))
                i += 3
            elif i + 1 < len(line) and line[i+1] == '>':
                tokens.append(Token('RIGHT_SHIFT', '>>', line_num, column))
                i += 2
            elif i + 1 < len(line) and line[i+1] == '=':
                tokens.append(Token('GREATER_EQUAL', '>=', line_num, column))
                i += 2
            else:
                tokens.append(Token('GREATER_THAN', char, line_num, column))
                i += 1
        elif char == '^':
            tokens.append(Token('CARET', char, line_num, column))
            i += 1
        elif char == '&':
            # 前のトークンが値系か判定する関数
            def _is_prev_value_token(t):
                return t in (
                    'IDENTIFIER','HEX_NUMBER','BIN_NUMBER','OCT_NUMBER',
                    'DEC_NUMBER','CHAR','RPAREN','STAR'
                )

            # & の次が 0-7 かつ前トークンが値でないときのみ 8進数
            if (i + 1 < len(line)
                and line[i + 1] in '01234567'
                and not _is_prev_value_token(prev_token_type)):

                start = i
                i += 1
                while i < len(line) and line[i] in '01234567':
                    i += 1

                # & のあとに数字が1文字も無ければ AND として扱う
                if i == start + 1:
                    tokens.append(Token('AND', '&', line_num, column))
                else:
                    tokens.append(Token('OCT_NUMBER', line[start:i], line_num, column))
            else:
                tokens.append(Token('AND', '&', line_num, column))
                i += 1
        elif char == '#':
            tokens.append(Token('IMMEDIATE', char, line_num, column))
            i += 1
        elif char == ',':
            tokens.append(Token('COMMA', char, line_num, column))
            i += 1
        elif char == '(': 
            tokens.append(Token('LPAREN', char, line_num, column))
            i += 1
        elif char == ')':
            tokens.append(Token('RPAREN', char, line_num, column))
            i += 1
        elif char == '+':
            # Regular plus operator (macro calls are handled earlier)
            tokens.append(Token('PLUS', char, line_num, column))
            i += 1
        elif char == '-':
            tokens.append(Token('MINUS', char, line_num, column))
            i += 1
        elif char == '/':
            tokens.append(Token('DIVIDE', char, line_num, column))
            i += 1
        elif char == '|':
            tokens.append(Token('OR', char, line_num, column))
            i += 1
        elif char == '.':
            # Could be directive, local symbol, or floating point number
            start = i
            i += 1
            if i < len(line) and line[i].isdigit():
                # This is a floating point number starting with .
                while i < len(line) and line[i].isdigit():
                    i += 1
                tokens.append(Token('DEC_NUMBER', line[start:i], line_num, column))
            elif i < len(line) and (line[i].isalpha() or line[i] == '_'):
                # This is a directive or local symbol
                while i < len(line) and (line[i].isalnum() or line[i] == '_'):
                    i += 1
                identifier = line[start:i]
                # Check if next is colon (label) or space/operator (directive/symbol)
                if i < len(line) and line[i] == ':':
                    tokens.append(Token('LABEL', identifier, line_num, column))
                    i += 1
                elif identifier.lower() in ['.byte', '.word', '.text', '.org', '.equ', '.ds', '.end']:
                    tokens.append(Token('DIRECTIVE', identifier, line_num, column))
                else:
                    tokens.append(Token('IDENTIFIER', identifier, line_num, column))
            else:
                tokens.append(Token('DOT', char, line_num, column))
        elif char == '{':
            tokens.append(Token('LBRACE', char, line_num, column))
            i += 1
        elif char == '}':
            tokens.append(Token('RBRACE', char, line_num, column))
            i += 1
        else:
            # Unknown character
            tokens.append(Token('UNKNOWN', char, line_num, column))
            i += 1
        # Track previous token type for context-sensitive decisions
        if tokens:
            prev_token_type = tokens[-1].type

    return tokens