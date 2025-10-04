"""
pyasm6502 - ACME-Compatible 6502 Assembler
Core assembler class.
"""

from typing import Dict, List, Tuple, Optional, Any, Union

from package.constants import INSTRUCTIONS_6502, INSTRUCTIONS_65C02, INSTRUCTIONS_NMOS6502, INSTRUCTIONS_W65C02S
from package.datastructures import AssemblerError, OutputFormat, Symbol, Token, Zone
from package.directives import process_acme_directive, process_directive
from package.evaluator import evaluate_expression
from package.output import generate_output
from package.tokenizer import tokenize
from package.text_conversion import TextConverter
from package.conditionals import ConditionalProcessor
from package.loops import LoopProcessor
from package.macros import MacroSystem
from package.filesystem import FileManager
from package.segments import SegmentManager
from package.debug import DebugSystem


class Assembler6502:
    """6502 Assembly Language Assembler with ACME compatibility."""

    def __init__(self):
        self.global_symbols: Dict[str, Symbol] = {}
        self.zones: List[Zone] = [Zone("global")]  # Global zone first
        self.current_zone = 0
        self.pc = 0
        self.output = bytearray()
        self.lines = []
        self.current_line = 0
        self.current_filename = ""
        self.pass_number = 1
        self.output_format = OutputFormat.PLAIN
        self.output_filename = ""
        self.cpu_type = "6502"  # Default CPU type
        self.INSTRUCTIONS = {}
        self._update_instructions()

        # Anonymous label tracking
        self.anonymous_forward: Dict[str, List[int]] = {}  # "+", "++", etc -> [addresses]
        self.anonymous_backward: Dict[str, List[int]] = {}  # "-", "--", etc -> [addresses]

        # Cheap locals (@ symbols) - reset at each global label
        self.cheap_locals: Dict[str, Symbol] = {}
        
        # This will hold the output bytes before final generation
        self.output_dict: Dict[int, int] = {}

        # Text conversion system
        self.text_converter = TextConverter()

        # Conditional assembly processor
        self.conditional_processor = ConditionalProcessor()

        # Loop and variable processor
        self.loop_processor = LoopProcessor()

        # Macro system
        self.macro_system = MacroSystem()

        # File manager
        self.file_manager = FileManager()

        # Segment manager
        self.segment_manager = SegmentManager()

        # Debug system
        self.debug_system = DebugSystem()

        # Macro collection state
        self.collecting_macro = False
        self.current_macro_name = ""
        self.current_macro_params = []
        self.current_macro_body = []
        self.macro_brace_depth = 0
        # Track duplicates within a single pass
        self._defined_names_this_pass: set[str] = set()

    def _get_current_line_text(self) -> str:
        """Get the current line text for error reporting."""
        if self.lines and 1 <= self.current_line <= len(self.lines):
            return self.lines[self.current_line - 1].strip()
        return ""

    def _raise_error(self, message: str) -> None:
        """Helper method to raise AssemblerError with current context."""
        line_text = self._get_current_line_text()
        raise AssemblerError(message, self.current_line, line_text, self.current_filename)

    def _update_instructions(self):
        """Set the active instruction set based on the current CPU type."""
        self.INSTRUCTIONS = INSTRUCTIONS_6502.copy()

        cpu_type_lower = self.cpu_type.lower()

        # Helper function to merge instruction sets without overwriting existing addressing modes
        def merge_instructions(source_dict):
            for mnemonic, modes in source_dict.items():
                if mnemonic in self.INSTRUCTIONS:
                    # Merge addressing modes, not replace entirely
                    self.INSTRUCTIONS[mnemonic].update(modes)
                else:
                    # New instruction
                    self.INSTRUCTIONS[mnemonic] = modes.copy()

        # W65C02S includes all 65C02 instructions plus Rockwell/WDC extensions
        if cpu_type_lower in ["w65c02s", "w65c02"]:
            merge_instructions(INSTRUCTIONS_65C02)
            merge_instructions(INSTRUCTIONS_W65C02S)

        # Standard 65C02 (R65C02, etc.)
        elif cpu_type_lower == "65c02":
            merge_instructions(INSTRUCTIONS_65C02)

        # NMOS 6502 with undocumented opcodes
        elif cpu_type_lower == "nmos6502":
            merge_instructions(INSTRUCTIONS_NMOS6502)

    def create_zone(self, name: str = ""):
        """Create a new zone for local symbols."""
        zone = Zone(name)
        self.zones.append(zone)
        self.current_zone = len(self.zones) - 1

    def resolve_symbol(self, name: str) -> Optional[Symbol]:
        """Resolve a symbol in the current scope."""
        # Anonymous labels
        if all(c == '+' for c in name):
            # Forward anonymous label
            if name in self.anonymous_forward and self.anonymous_forward[name]:
                return Symbol(name, self.anonymous_forward[name][0])
            elif self.pass_number == 1:
                return Symbol(name, 0)  # Forward reference
            else:
                self._raise_error(f"Undefined anonymous forward label: {name}")

        elif all(c == '-' for c in name):
            # Backward anonymous label
            if name in self.anonymous_backward and self.anonymous_backward[name]:
                return Symbol(name, self.anonymous_backward[name][-1])
            else:
                self._raise_error(f"Undefined anonymous backward label: {name}")

        # Cheap local (@symbol)
        if name.startswith('@'):
            if name in self.cheap_locals:
                return self.cheap_locals[name]
            elif self.pass_number == 1:
                return Symbol(name, 0)  # Forward reference
            else:
                self._raise_error(f"Undefined cheap local: {name}")

        # Local symbol (.symbol)
        if name.startswith('.'):
            current_zone = self.zones[self.current_zone]
            if name in current_zone.local_symbols:
                return current_zone.local_symbols[name]
            elif self.pass_number == 1:
                return Symbol(name, 0, is_local=True)  # Forward reference
            else:
                self._raise_error(f"Undefined local symbol: {name}")

        # Global symbol
        if name in self.global_symbols:
            return self.global_symbols[name]
        elif self.pass_number == 1:
            return Symbol(name, 0)  # Forward reference
        else:
            self._raise_error(f"Undefined symbol: {name}")

    def define_symbol(self, name: str, value: Union[int, float], is_address: bool = False):
        """Define a symbol in the appropriate scope."""
        symbol = Symbol(name, value, is_address)

        # Anonymous labels
        if all(c == '+' for c in name):
            if name not in self.anonymous_forward:
                self.anonymous_forward[name] = []
            self.anonymous_forward[name].append(value)
            return

        elif all(c == '-' for c in name):
            if name not in self.anonymous_backward:
                self.anonymous_backward[name] = []
            self.anonymous_backward[name].append(value)
            return

        # Cheap local (@symbol)
        if name.startswith('@'):
            self.cheap_locals[name] = symbol
            return

        # Local symbol (.symbol)
        if name.startswith('.'):
            symbol.is_local = True
            current_zone = self.zones[self.current_zone]
            # If already exists from previous pass, just update value
            if name in current_zone.local_symbols and name not in self._defined_names_this_pass:
                current_zone.local_symbols[name] = symbol
                self._defined_names_this_pass.add(name)
                return
            # Duplicate within same pass
            if name in self._defined_names_this_pass:
                self._raise_error(f"Symbol already defined: {name}")
            current_zone.local_symbols[name] = symbol
            self._defined_names_this_pass.add(name)
            return

        # Global symbol (also resets cheap locals)
        # If already exists from previous pass, just update value
        if name in self.global_symbols and name not in self._defined_names_this_pass:
            self.global_symbols[name] = symbol
            self.cheap_locals.clear()
            self._defined_names_this_pass.add(name)
            return
        # Duplicate within same pass
        if name in self._defined_names_this_pass:
            self._raise_error(f"Symbol already defined: {name}")
        self.global_symbols[name] = symbol
        self._defined_names_this_pass.add(name)
        self.cheap_locals.clear()  # Reset cheap locals at global label

    def determine_addressing_mode(self, mnemonic: str, tokens: List[Token], start: int) -> Tuple[str, Any, int]:
        """Determine addressing mode and return (mode, operand(s), tokens_consumed)."""
        if start >= len(tokens):
            # Could be accumulator or implied
            if 'ACC' in self.INSTRUCTIONS[mnemonic]:
                return 'ACC', 'A', 0
            # Special case for NMOS 6502 undocumented instructions (ACME compatibility)
            if mnemonic == 'TOP':
                # TOP without arguments outputs single 0x0C byte (ACME behavior)
                return 'IMPLIED_SINGLE', 0x0C, 0
            if mnemonic == 'DOP':
                # DOP without arguments outputs single 0x80 byte (ACME behavior)
                return 'IMPLIED_SINGLE', 0x80, 0
            return 'IMP', 0, 0

        # Handle accumulator addressing explicitly
        if tokens[start].value.upper() == 'A':
            if 'ACC' in self.INSTRUCTIONS[mnemonic]:
                return 'ACC', 'A', 1
            # Fallthrough for cases like "LDA A", which is not valid

        token = tokens[start]

        # Immediate addressing: #value
        if token.type == 'IMMEDIATE':
            if start + 1 >= len(tokens):
                raise AssemblerError("Expected value after '#'", self.current_line, filename=self.current_filename)
            value, consumed = evaluate_expression(self, tokens, start + 1)
            return 'IMM', int(value) & 0xFF, consumed + 1

        # Indirect addressing: (address) or (address,X)
        elif token.type == 'LPAREN':
            value, consumed = evaluate_expression(self, tokens, start + 1)
            next_idx = start + 1 + consumed

            if next_idx < len(tokens) and tokens[next_idx].type == 'COMMA':
                # Check for (address,X)
                if next_idx + 1 < len(tokens) and tokens[next_idx + 1].value.upper() == 'X':
                    if next_idx + 2 < len(tokens) and tokens[next_idx + 2].type == 'RPAREN':
                        # Distinguish between INDX (zp,X) and ABS_X_IND ($nnnn,X) for 65C02
                        if value <= 0xFF and 'INDX' in self.INSTRUCTIONS.get(mnemonic, {}):
                            return 'INDX', int(value), consumed + 4
                        elif 'ABS_X_IND' in self.INSTRUCTIONS.get(mnemonic, {}):
                            return 'ABS_X_IND', int(value), consumed + 4
                        else:
                            return 'INDX', int(value), consumed + 4
                    else:
                        raise AssemblerError("Expected ')' after (addr,X)", self.current_line, filename=self.current_filename)

            elif next_idx < len(tokens) and tokens[next_idx].type == 'RPAREN':
                next_idx += 1
                # Check for (address),Y
                if next_idx < len(tokens) and tokens[next_idx].type == 'COMMA':
                    if next_idx + 1 < len(tokens) and tokens[next_idx + 1].value.upper() == 'Y':
                        return 'INDY', int(value), consumed + 4
                    elif next_idx + 1 < len(tokens) and tokens[next_idx + 1].value.upper() == 'X':
                        # JMP ($nnnn,X) - 65C02 indexed indirect jump
                        return 'ABS_X_IND', int(value), consumed + 4
                else:
                    # Just (address) - check if zero page indirect (65C02) or absolute indirect
                    if value <= 0xFF and 'ZP_IND' in self.INSTRUCTIONS.get(mnemonic, {}):
                        return 'ZP_IND', int(value), consumed + 2
                    else:
                        return 'IND', int(value), consumed + 2

            raise AssemblerError("Invalid indirect addressing", self.current_line, filename=self.current_filename)

        # ZP_REL for W65C02S (BBR, BBS)
        is_zp_rel_mnemonic = mnemonic.startswith(('BBR', 'BBS'))
        if is_zp_rel_mnemonic:
            val1, consumed1 = evaluate_expression(self, tokens, start)
            next_idx = start + consumed1
            if next_idx < len(tokens) and tokens[next_idx].type == 'COMMA':
                val2, consumed2 = evaluate_expression(self, tokens, next_idx + 1)
                return 'ZP_REL', (int(val1), int(val2)), consumed1 + 1 + consumed2
            else:
                raise AssemblerError(f"Expected two comma-separated operands for {mnemonic}", self.current_line, filename=self.current_filename)

        # Standard addressing (Direct, Indexed, Relative)
        # Capture simple size hints for 65816 tests: '<', '>', '^' before primary
        hint_size = None  # 1,2,3 bytes if hinted
        if start < len(tokens) and tokens[start].type in ['LESS_THAN','GREATER_THAN','CARET']:
            t = tokens[start].type
            if t == 'LESS_THAN':
                hint_size = 1
            elif t == 'GREATER_THAN':
                hint_size = 2
            elif t == 'CARET':
                hint_size = 3
            value, consumed = evaluate_expression(self, tokens, start)
        else:
            value, consumed = evaluate_expression(self, tokens, start)
        next_idx = start + consumed

        # Indexed addressing
        if next_idx < len(tokens) and tokens[next_idx].type == 'COMMA':
            if next_idx + 1 < len(tokens):
                index_reg = tokens[next_idx + 1].value.upper()
                if index_reg == 'X':
                    if value <= 0xFF and 'ZPX' in self.INSTRUCTIONS[mnemonic]:
                        return 'ZPX', int(value), consumed + 2
                    else:
                        return 'ABSX', int(value), consumed + 2
                elif index_reg == 'Y':
                    if value <= 0xFF and 'ZPY' in self.INSTRUCTIONS[mnemonic]:
                        return 'ZPY', int(value), consumed + 2
                    else:
                        return 'ABSY', int(value), consumed + 2
                else:
                    raise AssemblerError(f"Invalid index register: {index_reg}", self.current_line, filename=self.current_filename)

        # JMP and JSR only have Absolute mode, not Zero Page.
        if mnemonic in ['JMP', 'JSR']:
            return 'ABS', int(value), consumed

        # Branch instructions are always relative
        if mnemonic.startswith('B') and mnemonic != 'BIT':
             return 'REL', int(value), consumed

        # Non-indexed addressing (ZP or ABS)
        if hint_size == 1 and 'ZP' in self.INSTRUCTIONS[mnemonic]:
            return 'ZP', int(value), consumed
        if hint_size == 2 and 'ABS' in self.INSTRUCTIONS[mnemonic]:
            return 'ABS', int(value), consumed
        if hint_size == 3 and 'ABS' in self.INSTRUCTIONS[mnemonic]:
            return 'ABS', int(value), consumed  # 24-bit absolute not modeled; map to ABS for length tests upstream
        if value <= 0xFF and 'ZP' in self.INSTRUCTIONS[mnemonic]:
            return 'ZP', int(value), consumed
        else:
            return 'ABS', int(value), consumed

    def assemble_instruction(self, mnemonic: str, tokens: List[Token], operand_start: int):
        """Assemble an instruction."""
        if mnemonic not in self.INSTRUCTIONS:
            self._raise_error(f"Unknown instruction: {mnemonic}")

        instruction_modes = self.INSTRUCTIONS[mnemonic]

        # Determine addressing mode
        mode, operand, consumed = self.determine_addressing_mode(mnemonic, tokens, operand_start)

        # Special case: if mode is None, skip this instruction (ACME compatibility)
        if mode is None:
            return

        # Special case: IMPLIED_SINGLE for NMOS 6502 DOP/TOP (ACME compatibility)
        if mode == 'IMPLIED_SINGLE':
            self.output_dict[self.pc] = operand
            self.pc += 1
            return

        # Find matching instruction mode
        if mode not in instruction_modes:
            # Try to auto-upgrade ZP to ABS if ZP not available
            if mode == 'ZP' and 'ABS' in instruction_modes:
                mode = 'ABS'
            elif mode == 'ZPX' and 'ABSX' in instruction_modes:
                mode = 'ABSX'
            elif mode == 'ZPY' and 'ABSY' in instruction_modes:
                mode = 'ABSY'
            else:
                self._raise_error(f"Invalid addressing mode '{mode}' for {mnemonic}")

        opcode, size = instruction_modes[mode]
        self.emit_byte(opcode)

        # Emit operand bytes
        if size == 2:
            if mode == 'REL':
                offset = operand - (self.pc + 1)
                if self.pass_number == 2 and (offset < -128 or offset > 127):
                    raise AssemblerError(f"Branch target too far: {offset}", self.current_line, filename=self.current_filename)
                self.emit_byte(offset & 0xFF)
            else:
                self.emit_byte(operand & 0xFF)
        elif size == 3:
            if mode == 'ZP_REL':
                zp_addr, branch_target = operand
                rel_offset = branch_target - (self.pc + 2)
                if self.pass_number == 2 and (rel_offset < -128 or rel_offset > 127):
                    raise AssemblerError(f"Branch target too far: {rel_offset}", self.current_line, filename=self.current_filename)
                self.emit_byte(zp_addr & 0xFF)
                self.emit_byte(rel_offset & 0xFF)
            else:
                self.emit_word(operand)

    def emit_byte(self, value: int):
        """Emit a byte to the output."""
        # Use segment manager for advanced emission handling
        if hasattr(self, 'segment_manager'):
            self.segment_manager.emit_byte_with_segments(self, int(value))
        else:
            # Fallback for basic emission
            self.output_dict[self.pc] = int(value) & 0xFF
            self.pc += 1

    def emit_word(self, value: int):
        """Emit a word (little-endian) to the output."""
        self.emit_byte(value & 0xFF)
        self.emit_byte((value >> 8) & 0xFF)

    def expand_and_process_macro(self, macro_call: str, arguments_line: str):
        """Expand a macro call and process the resulting lines."""
        # Parse macro name and arguments
        macro_name, arguments = self.macro_system.parse_macro_call(macro_call + ' ' + arguments_line)

        # Expand the macro
        try:
            expanded_lines = self.macro_system.expand_macro(self, macro_name, arguments)

            # Process each expanded line
            for expanded_line in expanded_lines:
                if self.debug_system.verbosity_level >= 3:
                    print(f"DEBUG: Processing expanded line: '{expanded_line}'")
                tokens = tokenize(expanded_line, self.current_line, self.INSTRUCTIONS)
                if self.debug_system.verbosity_level >= 3:
                    print(f"DEBUG: Tokens: {[f'{t.type}:{t.value}' for t in tokens]}")
                self.process_line(tokens)

        except AssemblerError as e:
            # Re-raise with macro call context
            raise AssemblerError(f"In macro {macro_name}: {str(e)}", self.current_line, filename=self.current_filename)

    def process_included_lines(self, included_lines: List[str]):
        """Process lines from an included file."""
        saved_filename = self.current_filename
        saved_line = self.current_line

        try:
            # Process each line from the included file
            for line_num, line in enumerate(included_lines, 1):
                self.current_line = line_num
                try:
                    tokens = tokenize(line, line_num, self.INSTRUCTIONS)
                    self.process_line(tokens)
                except AssemblerError as e:
                    # If error doesn't have line information, add it
                    if e.line_num == 0:
                        # Create new error with proper line information
                        new_error = AssemblerError(e.message, line_num, line.strip(), self.current_filename)
                        raise new_error from e
                    raise

        finally:
            # Restore original context
            self.current_filename = saved_filename
            self.current_line = saved_line

    def _collect_macro_line(self, tokens: List[Token]):
        """Collect a line as part of a macro definition."""
        line_text = ' '.join([t.value for t in tokens])

        # Count braces to track nesting
        brace_count = line_text.count('{') - line_text.count('}')
        self.macro_brace_depth += brace_count

        # If we hit zero depth, we've found the end of the macro
        if self.macro_brace_depth <= 0:
            # Don't include the final closing brace line if it's just "}"
            if line_text.strip() != '}':
                self.current_macro_body.append(line_text)

            # ACME compatibility: auto-close conditionals at end of macro
            if_directives = ['!if', '!ifdef', '!ifndef']
            unclosed_count = 0
            for body_line in self.current_macro_body:
                # Basic parsing to find conditional directives
                line_content = body_line.split(';')[0].strip()
                parts = line_content.split()
                if not parts:
                    continue
                
                directive = parts[0].lower()
                if directive in if_directives:
                    # Don't auto-close brace-style conditionals
                    if '{' not in line_content:
                        unclosed_count += 1
                elif directive == '!fi':
                    unclosed_count -= 1
            
            if unclosed_count > 0:
                self.current_macro_body.extend(['!fi'] * unclosed_count)

            # Finalize the macro definition
            self.macro_system.define_macro(
                self.current_macro_name,
                self.current_macro_params,
                self.current_macro_body,
                self.current_line
            )

            # Reset collection state
            self.collecting_macro = False
            self.current_macro_name = ""
            self.current_macro_params = []
            self.current_macro_body = []
            self.macro_brace_depth = 0
        else:
            # Continue collecting the macro body
            self.current_macro_body.append(line_text)

    def start_macro_collection(self, name: str, params: List[str]):
        """Start collecting a multi-line macro definition."""
        self.collecting_macro = True
        self.current_macro_name = name
        self.current_macro_params = params
        self.current_macro_body = []
        self.macro_brace_depth = 1  # We've seen the opening brace

    def process_line(self, tokens: List[Token]):
        """Process a line of tokens."""
        if not tokens:
            return

        # Check if we should skip this line due to conditional assembly
        # But always process conditional directives themselves
        is_cond_directive = (len(tokens) > 0 and tokens[0].type == 'ACME_DIRECTIVE' and
                             tokens[0].value in ['!if', '!ifdef', '!ifndef', '!else', '!fi'])
        is_rbrace = len(tokens) > 0 and tokens[0].type == 'RBRACE'

        if self.conditional_processor.is_skipping() and not is_cond_directive and not is_rbrace:
            return

        # Handle macro collection mode
        if self.collecting_macro:
            self._collect_macro_line(tokens)
            return

        i = 0

        # Support bare label definitions without ':'
        if len(tokens) == 1 and tokens[0].type == 'IDENTIFIER':
            name = tokens[0].value
            if name.startswith('.'):  # local label
                self.define_symbol(name, self.pc)
                return
            # Global label (avoid treating directives/instructions as labels)
            upper = name.upper()
            if upper not in self.INSTRUCTIONS and not name.startswith('!'):
                self.define_symbol(name, self.pc)
                return
        while i < len(tokens):
            token = tokens[i]

            # Handle RBRACE for conditionals
            if token.type == 'RBRACE':
                self.conditional_processor.process_rbrace_directive(self)
                i += 1
                continue

            # Handle labels
            if token.type == 'LABEL':
                self.define_symbol(token.value, self.pc)
                i += 1
                continue

            # Handle origin directive (*= address)
            if token.type == 'STAR':
                if i + 1 < len(tokens) and tokens[i + 1].type == 'EQUALS':
                    if i + 2 < len(tokens):
                        address, _ = evaluate_expression(self, tokens, i + 2)
                        self.pc = int(address)
                        return # Consumes rest of line
                    else:
                        raise AssemblerError("Expected address after '*='", self.current_line, filename=self.current_filename)

            # Handle symbol assignment (symbol = value)
            # Support ACME-style LHS flags: IDENTIFIER [+ DEC_NUMBER] = expr
            if token.type == 'IDENTIFIER':
                # Direct form: symbol = expr
                if i + 1 < len(tokens) and tokens[i + 1].type == 'EQUALS':
                    symbol = token.value
                    value, _ = evaluate_expression(self, tokens, i + 2)
                    self.define_symbol(symbol, value)
                    return # Consumes rest of line
                # Flagged form: symbol + N = expr  (ignore flag for now)
                if (i + 3 < len(tokens) and
                    tokens[i + 1].type == 'PLUS' and
                    tokens[i + 2].type in ['DEC_NUMBER','HEX_NUMBER','BIN_NUMBER','OCT_NUMBER'] and
                    tokens[i + 3].type == 'EQUALS'):
                    symbol = token.value
                    # flags_value, _ = evaluate_expression(self, tokens, i + 2)  # reserved for future use
                    value, _ = evaluate_expression(self, tokens, i + 4)
                    self.define_symbol(symbol, value)
                    return # Consumes rest of line

            # Handle .equ directive
            if (i + 1 < len(tokens) and
                token.type == 'IDENTIFIER' and
                tokens[i + 1].type == 'DIRECTIVE' and
                tokens[i + 1].value.lower() == '.equ'):
                symbol = token.value
                if i + 2 < len(tokens):
                    value, _ = evaluate_expression(self, tokens, i + 2)
                    self.define_symbol(symbol, value)
                    return # Consumes rest of line
                else:
                    raise AssemblerError("Expected value after .equ", self.current_line, filename=self.current_filename)

            # Handle ACME directives
            if token.type == 'ACME_DIRECTIVE':
                directive_val = token.value
                # Special handling for !source directive
                if directive_val in ['!source', '!src']:
                    included_lines = self.file_manager.process_source_directive(self, tokens, i + 1)
                    self.process_included_lines(included_lines)
                    return # Consumes rest of line
                
                consumed = process_acme_directive(self, directive_val, tokens, i + 1)
                i += 1 + consumed
                continue

            # Handle traditional directives
            if token.type == 'DIRECTIVE':
                process_directive(self, token.value, tokens, i + 1)
                return # Consumes rest of line

            # Handle macro calls
            if token.type == 'MACRO_CALL':
                macro_call = token.value
                # Reconstruct line preserving proper spacing for function calls
                remaining_tokens = tokens[i+1:]
                remaining_line = ""
                for j, t in enumerate(remaining_tokens):
                    if j > 0:
                        prev_token = remaining_tokens[j-1]
                        # No space before these tokens (except after operators)
                        if t.type in ['RPAREN', 'COMMA']:
                            pass
                        # No space after these tokens
                        elif prev_token.type in ['LPAREN', 'FUNCTION']:
                            pass
                        # Always add space around operators and comparisons
                        elif (prev_token.type in ['OR', 'AND', 'XOR', 'NOT', 'EQUAL_EQUAL', 'NOT_EQUAL',
                                                  'LESS_THAN', 'GREATER_THAN', 'LESS_EQUAL', 'GREATER_EQUAL'] or
                              t.type in ['OR', 'AND', 'XOR', 'NOT', 'EQUAL_EQUAL', 'NOT_EQUAL',
                                        'LESS_THAN', 'GREATER_THAN', 'LESS_EQUAL', 'GREATER_EQUAL']):
                            remaining_line += " "
                        # Space before opening parentheses (except for function calls)
                        elif t.type == 'LPAREN' and prev_token.type not in ['FUNCTION', 'IDENTIFIER']:
                            remaining_line += " "
                        else:
                            remaining_line += " "
                    remaining_line += t.value
                self.expand_and_process_macro(macro_call, remaining_line)
                return # Consumes rest of line

            # Handle instructions
            if token.type == 'INSTRUCTION':
                self.assemble_instruction(token.value, tokens, i + 1)
                return # Consumes rest of line

            # If we are here, it's an unexpected token
            self._raise_error(f"Unexpected token: {token.value}")

    def assemble(self, source_lines: List[str], filename: str = "") -> bytearray:
        """Assemble source code and return binary output."""
        self.lines = source_lines
        self.current_filename = filename
        self.output = bytearray()
        self.output_dict = {}

        # Two-pass assembly
        for pass_num in [1, 2]:
            self.pass_number = pass_num
            self.pc = 0
            if pass_num == 2:
                self.output_dict = {}

            # Reset anonymous label tracking for each pass
            self.anonymous_forward.clear()
            self.anonymous_backward.clear()

            # Reset conditional processor for each pass
            self.conditional_processor.reset()

            # Reset loop processor for each pass
            self.loop_processor.reset()

            # Reset macro system counter for each pass
            self.macro_system.local_label_counter = 0

            # Reset file manager for each pass
            self.file_manager.reset()

            # Reset segment manager for each pass
            self.segment_manager.reset()

            # Reset debug system for each pass
            self.debug_system.reset()

            # Reset macro collection state for each pass
            self.collecting_macro = False
            self.current_macro_name = ""
            self.current_macro_params = []
            self.current_macro_body = []
            self.macro_brace_depth = 0
            # Reset per-pass duplicate tracking
            self._defined_names_this_pass.clear()

            for line_num, line in enumerate(source_lines, 1):
                self.current_line = line_num
                try:
                    tokens = tokenize(line, line_num, self.INSTRUCTIONS)
                    self.process_line(tokens)
                except AssemblerError as e:
                    # If error doesn't have line information, add it
                    if e.line_num == 0:
                        # Create new error with proper line information
                        new_error = AssemblerError(e.message, line_num, line.strip(), filename)
                        raise new_error from e
                    raise

            # Validate that all conditional blocks are properly closed
            self.conditional_processor.validate_nesting(self)

        return generate_output(self)

    def generate_output(self) -> bytearray:
        """Generate output in the specified format."""
        return generate_output(self)

    def get_symbol_table(self) -> Dict[str, int]:
        """Get the symbol table."""
        symbols = {}

        # Global symbols
        for name, symbol in self.global_symbols.items():
            symbols[name] = symbol.value

        # Local symbols from all zones
        for zone in self.zones:
            for name, symbol in zone.local_symbols.items():
                symbols[f"{zone.name}:{name}" if zone.name else name] = symbol.value

        # Cheap locals
        for name, symbol in self.cheap_locals.items():
            symbols[name] = symbol.value

        return symbols