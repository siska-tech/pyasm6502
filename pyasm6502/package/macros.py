"""
Macro System for pyasm6502
Handles !macro definition and +macro expansion.
"""

from typing import List, Dict, Any, Optional, Tuple
from .datastructures import AssemblerError, Token
from .tokenizer import tokenize

# Forward declaration for type hinting
class Assembler6502:
    pass

class Macro:
    """Represents a macro definition."""
    def __init__(self, name: str, parameters: List[str], body_lines: List[str], start_line: int):
        self.name = name
        self.parameters = parameters
        self.body_lines = body_lines
        self.start_line = start_line
        self.local_counter = 0  # For generating unique local labels

class MacroSystem:
    """Handles macro definition, expansion, and parameter substitution."""

    def __init__(self):
        self.macros: Dict[str, Macro] = {}
        self.macro_call_depth = 0
        self.max_macro_depth = 32  # Prevent infinite recursion
        self.local_label_counter = 0

    def define_macro(self, name: str, parameters: List[str], body_lines: List[str], start_line: int) -> None:
        """Define a new macro."""
        if name in self.macros:
            # Allow macro redefinition (ACME behavior)
            pass

        macro = Macro(name, parameters, body_lines, start_line)
        self.macros[name] = macro

    def is_macro_defined(self, name: str) -> bool:
        """Check if a macro is defined."""
        return name in self.macros

    def process_macro_directive(self, asm: 'Assembler6502', tokens: List[Token], start: int) -> None:
        """
        Process !macro directive to define a new macro.
        Syntax: !macro name [param1, param2, ...] { body }
        or:     !macro name [param1, param2, ...]
                body lines...
                } (on separate line)
        """
        if start >= len(tokens) or tokens[start].type != 'IDENTIFIER':
            raise AssemblerError("!macro requires a macro name", asm.current_line)

        macro_name = tokens[start].value
        parameters = []
        body_lines = []

        # Get the original line to check for curly brace syntax
        original_line = ' '.join([t.value for t in tokens])

        # Parse parameters if present
        current_token = start + 1
        while current_token < len(tokens) and tokens[current_token].value != '{':
            if tokens[current_token].type == 'IDENTIFIER':
                param_name = tokens[current_token].value

                # Check for call-by-reference (~parameter or @parameter)
                if param_name.startswith('~'):
                    param_name = param_name[1:]  # Remove ~ prefix
                    # Mark as call-by-reference (for future implementation)
                elif param_name.startswith('@'):
                    param_name = param_name[1:]  # Remove @ prefix for parameter name
                    # But we'll handle @param substitution separately

                parameters.append(param_name)

                # Skip comma if present
                if current_token + 1 < len(tokens) and tokens[current_token + 1].value == ',':
                    current_token += 2
                else:
                    current_token += 1
            else:
                current_token += 1

        # Check for single-line curly brace syntax: !macro name param { body }
        if '{' in original_line:
            brace_start = original_line.find('{')
            brace_end = original_line.rfind('}')

            if brace_start != -1 and brace_end != -1 and brace_end > brace_start:
                # Single-line macro with curly braces
                body_content = original_line[brace_start + 1:brace_end].strip()
                if body_content:
                    body_lines = [body_content]
                self.define_macro(macro_name, parameters, body_lines, asm.current_line)
            elif brace_start != -1 and brace_end == -1:
                # Multi-line macro starting with {
                # Start collection mode in the assembler
                asm.start_macro_collection(macro_name, parameters)
            else:
                raise AssemblerError("Invalid macro syntax with curly braces", asm.current_line)
        else:
            # Traditional multi-line macro without braces
            # The macro body will be collected by the assembler
            self.define_macro(macro_name, parameters, [], asm.current_line)

    def expand_macro(self, asm: 'Assembler6502', macro_name: str, arguments: List[str]) -> List[str]:
        """
        Expand a macro call with the given arguments.
        Returns a list of expanded lines.
        """
        if macro_name not in self.macros:
            raise AssemblerError(f"Undefined macro: {macro_name}", asm.current_line)

        if self.macro_call_depth >= self.max_macro_depth:
            raise AssemblerError("Macro recursion depth exceeded", asm.current_line)

        macro = self.macros[macro_name]

        # Check parameter count
        if len(arguments) != len(macro.parameters):
            raise AssemblerError(
                f"Macro {macro_name} expects {len(macro.parameters)} arguments, got {len(arguments)}",
                asm.current_line
            )

        # Create parameter substitution map
        param_map = {}
        for i, param_name in enumerate(macro.parameters):
            param_map[param_name] = arguments[i] if i < len(arguments) else ""

        # Generate unique local labels for this macro expansion
        self.local_label_counter += 1
        local_suffix = f"_{self.local_label_counter}"

        # Expand macro body with parameter substitution
        expanded_lines = []
        self.macro_call_depth += 1

        try:
            for line in macro.body_lines:
                expanded_line = self._substitute_parameters(line, param_map, local_suffix)
                expanded_lines.append(expanded_line)
        finally:
            self.macro_call_depth -= 1

        return expanded_lines

    def _substitute_parameters(self, line: str, param_map: Dict[str, str], local_suffix: str) -> str:
        """
        Substitute macro parameters and make local labels unique.
        """
        result = line
        import re

        # First, substitute parameters
        for param_name, param_value in param_map.items():
            # Handle @param syntax first (call-by-reference) - replace entire @param with value
            pattern = r'@' + re.escape(param_name) + r'\b'
            # Protect complex expressions with parentheses
            protected_value = self._protect_parameter_value(param_value)
            result = re.sub(pattern, protected_value, result)

            # Then handle plain parameter name
            # For parameters starting with non-word characters (like .), need special handling
            if param_name.startswith('.'):
                # For .param, match precisely .param followed by word boundary or special chars
                pattern = r'\.' + re.escape(param_name[1:]) + r'(?=\W|$)'
            else:
                pattern = r'\b' + re.escape(param_name) + r'\b'
            result = re.sub(pattern, param_value, result)

        # Then handle local labels (after parameter substitution)
        # This ensures we don't modify parameters that have been substituted
        if '.' in result and not result.strip().startswith(';'):
            def local_label_replacer(match):
                label_name = match.group(1)
                # This is a local label, make it unique
                return '.' + label_name + local_suffix

            # Match .labelname but not decimal numbers like 3.14
            # Local labels must start with a letter or underscore, not a digit
            result = re.sub(r'\.([a-zA-Z_]\w*)', local_label_replacer, result)

        # Handle cheap local labels (@labelname) - make them unique within macro expansion
        # Only process @labels that are NOT parameters (already substituted above)
        if '@' in result and not result.strip().startswith(';'):
            def cheap_local_replacer(match):
                label_name = match.group(1)
                colon = match.group(2) if len(match.groups()) > 1 else ''
                # Check if this is a parameter name that was already substituted
                if label_name in param_map:
                    # This is a parameter reference, don't modify
                    return match.group(0)
                # This is a cheap local label, make it unique
                return '@' + label_name + local_suffix + colon

            # Match @labelname where labelname starts with a letter or underscore
            # This handles both @label references and @label: definitions
            result = re.sub(r'@([a-zA-Z_]\w*)(:?)', cheap_local_replacer, result)

        return result

    def _protect_parameter_value(self, param_value: str) -> str:
        """
        Protect parameter values that contain operators by wrapping them in parentheses.
        This prevents operator precedence issues during macro expansion.
        """
        import re

        # Check if the parameter value contains operators that need protection
        # Look for operators like !=, ==, <=, >=, <, >, +, -, *, /, etc.
        operator_pattern = r'[!<>=+\-*/&|^%]'

        if re.search(operator_pattern, param_value.strip()):
            # The parameter contains operators, wrap it in parentheses
            return f"({param_value})"
        else:
            # Simple value, no protection needed
            return param_value

    def collect_macro_body(self, source_lines: List[str], start_line: int) -> Tuple[List[str], int]:
        """
        Collect lines that form the body of a macro until closing brace }.
        Returns (body_lines, end_line_index).
        """
        body_lines = []
        brace_depth = 0
        found_opening_brace = False

        for i, line in enumerate(source_lines[start_line:], start_line):
            stripped = line.strip()

            # Look for opening brace
            if '{' in stripped:
                found_opening_brace = True
                brace_depth += stripped.count('{')
                # Remove the opening brace from the first line
                if brace_depth == 1:
                    line_without_brace = stripped.replace('{', '', 1).strip()
                    if line_without_brace:
                        body_lines.append(line_without_brace)
                    continue

            if not found_opening_brace:
                continue

            # Look for closing brace
            if '}' in stripped:
                brace_depth -= stripped.count('}')
                if brace_depth == 0:
                    # Remove the closing brace from the last line
                    line_without_brace = stripped.replace('}', '', 1).strip()
                    if line_without_brace:
                        body_lines.append(line_without_brace)
                    return body_lines, i

            if brace_depth > 0:
                body_lines.append(line)

        raise AssemblerError(f"Unclosed macro starting at line {start_line + 1}", start_line + 1)

    def parse_macro_call(self, call_line: str) -> Tuple[str, List[str]]:
        """
        Parse a macro call line (+macro_name arg1, arg2, ...).
        Returns (macro_name, arguments_list).
        """
        # Remove the + prefix and split on first whitespace
        call_line = call_line.strip()
        if not call_line.startswith('+'):
            raise AssemblerError("Macro call must start with +", 0)

        call_line = call_line[1:]  # Remove +

        # Split macro name and arguments
        parts = call_line.split(None, 1)
        if not parts:
            raise AssemblerError("Empty macro call", 0)

        macro_name = parts[0]
        arguments = []

        if len(parts) > 1:
            # Parse arguments (simple comma-separated for now)
            arg_string = parts[1].strip()
            if arg_string:
                # Split on commas and strip whitespace
                raw_args = arg_string.split(',')
                arguments = [arg.strip() for arg in raw_args]

        return macro_name, arguments

    def reset(self) -> None:
        """Reset the macro system state (for new assembly passes)."""
        # Don't clear macros between passes - they should persist
        self.macro_call_depth = 0