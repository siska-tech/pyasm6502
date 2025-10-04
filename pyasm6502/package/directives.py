from typing import List

from .datastructures import AssemblerError, Token, OutputFormat
from .evaluator import evaluate_expression, parse_number
from .conditionals import ConditionalProcessor
from .loops import LoopProcessor
from .macros import MacroSystem
from .filesystem import FileManager
from .segments import SegmentManager
from .debug import DebugSystem

# Forward declaration for type hinting
class Assembler6502:
    pass

def _process_data_directive(asm: 'Assembler6502', tokens: List[Token], start: int, size: int, little_endian: bool = True):
    """Process data directive with specified size and endianness."""
    i = start
    while i < len(tokens):
        if tokens[i].type in ['STRING', 'CHAR']:
            # String literal - each character becomes a byte
            string_val = tokens[i].value[1:-1]  # Remove quotes
            for char in string_val:
                if size == 1:
                    asm.emit_byte(ord(char))
                else:
                    # For multi-byte, just emit the character as byte
                    asm.emit_byte(ord(char))
        else:
            value, consumed = evaluate_expression(asm, tokens, i)
            value = int(value)

            # Emit value with specified size and endianness
            if size == 1:
                asm.emit_byte(value & 0xFF)
            elif size == 2:
                if little_endian:
                    asm.emit_byte(value & 0xFF)
                    asm.emit_byte((value >> 8) & 0xFF)
                else:  # big-endian
                    asm.emit_byte((value >> 8) & 0xFF)
                    asm.emit_byte(value & 0xFF)
            elif size == 3:
                if little_endian:
                    asm.emit_byte(value & 0xFF)
                    asm.emit_byte((value >> 8) & 0xFF)
                    asm.emit_byte((value >> 16) & 0xFF)
                else:  # big-endian
                    asm.emit_byte((value >> 16) & 0xFF)
                    asm.emit_byte((value >> 8) & 0xFF)
                    asm.emit_byte(value & 0xFF)
            elif size == 4:
                if little_endian:
                    asm.emit_byte(value & 0xFF)
                    asm.emit_byte((value >> 8) & 0xFF)
                    asm.emit_byte((value >> 16) & 0xFF)
                    asm.emit_byte((value >> 24) & 0xFF)
                else:  # big-endian
                    asm.emit_byte((value >> 24) & 0xFF)
                    asm.emit_byte((value >> 16) & 0xFF)
                    asm.emit_byte((value >> 8) & 0xFF)
                    asm.emit_byte(value & 0xFF)

            i += consumed - 1

        i += 1
        if i < len(tokens) and tokens[i].type == 'COMMA':
            i += 1

def _process_hex_directive(asm: 'Assembler6502', tokens: List[Token], start: int):
    """Process !hex directive with raw hex input."""
    i = start
    while i < len(tokens):
        if tokens[i].type == 'STRING':
            # String containing hex data
            hex_string = tokens[i].value[1:-1]  # Remove quotes
            # Remove whitespace and convert to bytes
            hex_string = ''.join(hex_string.split())

            if len(hex_string) % 2 != 0:
                raise AssemblerError("Hex string must have even number of characters", asm.current_line, filename=asm.current_filename)

            for j in range(0, len(hex_string), 2):
                hex_byte = hex_string[j:j+2]
                try:
                    byte_value = int(hex_byte, 16)
                    asm.emit_byte(byte_value)
                except ValueError:
                    raise AssemblerError(f"Invalid hex byte: {hex_byte}", asm.current_line, filename=asm.current_filename)

        elif tokens[i].type == 'HEX_NUMBER':
            # Single hex number
            value = parse_number(tokens[i])
            asm.emit_byte(int(value) & 0xFF)

        i += 1
        if i < len(tokens) and tokens[i].type == 'COMMA':
            i += 1

def _process_align_directive(asm: 'Assembler6502', tokens: List[Token], start: int):
    """Process !align directive for memory alignment."""
    if start >= len(tokens):
        raise AssemblerError("!align requires alignment boundary", asm.current_line, filename=asm.current_filename)

    # Get alignment boundary
    alignment, consumed = evaluate_expression(asm, tokens, start)
    alignment = int(alignment)

    if alignment <= 0 or (alignment & (alignment - 1)) != 0:
        raise AssemblerError("Alignment boundary must be a positive power of 2", asm.current_line, filename=asm.current_filename)

    # Get optional fill value (default 0)
    fill_value = 0
    if start + consumed < len(tokens) and tokens[start + consumed].type == 'COMMA':
        fill_value, _ = evaluate_expression(asm, tokens, start + consumed + 1)
        fill_value = int(fill_value) & 0xFF

    # Calculate padding needed
    current_addr = asm.pc
    aligned_addr = (current_addr + alignment - 1) & ~(alignment - 1)
    padding = aligned_addr - current_addr

    # Emit padding bytes
    for _ in range(padding):
        asm.emit_byte(fill_value)

def process_acme_directive(asm: 'Assembler6502', directive: str, tokens: List[Token], start: int) -> int:
    """Process ACME pseudo opcodes. Returns number of tokens consumed."""
    directive = directive.lower()

    consumed = len(tokens) - start # Default: consume rest of line

    if directive == '!to':
        # Set output filename and format
        if start < len(tokens):
            filename_token = tokens[start]
            if filename_token.type == 'STRING':
                asm.output_filename = filename_token.value[1:-1]  # Remove quotes

                # Check for format parameter
                if start + 1 < len(tokens) and tokens[start + 1].type == 'COMMA':
                    if start + 2 < len(tokens):
                        format_token = tokens[start + 2]
                        if format_token.type == 'IDENTIFIER':
                            format_name = format_token.value.lower()
                            try:
                                asm.output_format = OutputFormat(format_name)
                            except ValueError:
                                raise AssemblerError(f"Unknown output format: {format_name}", asm.current_line, filename=asm.current_filename)

    elif directive in ['!byte', '!8']:
        _process_data_directive(asm, tokens, start, 1, True)

    elif directive in ['!word', '!16', '!le16']:
        _process_data_directive(asm, tokens, start, 2, True)

    elif directive == '!be16':
        _process_data_directive(asm, tokens, start, 2, False)

    elif directive in ['!24', '!le24']:
        _process_data_directive(asm, tokens, start, 3, True)

    elif directive == '!be24':
        _process_data_directive(asm, tokens, start, 3, False)

    elif directive in ['!32', '!le32']:
        _process_data_directive(asm, tokens, start, 4, True)

    elif directive == '!be32':
        _process_data_directive(asm, tokens, start, 4, False)

    elif directive == '!pet':
        # Emit PETSCII string using text converter
        if start < len(tokens) and tokens[start].type == 'STRING':
            string_val = tokens[start].value[1:-1]  # Remove quotes
            petscii_bytes = asm.text_converter.convert_string(string_val, 'pet')
            for byte_val in petscii_bytes:
                asm.emit_byte(byte_val)

    elif directive == '!text' or directive == '!raw':
        # Emit raw text string using current conversion table
        if start < len(tokens) and tokens[start].type == 'STRING':
            string_val = tokens[start].value[1:-1]  # Remove quotes
            text_bytes = asm.text_converter.convert_string(string_val, 'raw')
            for byte_val in text_bytes:
                asm.emit_byte(byte_val)

    elif directive == '!convtab' or directive == '!ct':
        # Set character conversion table
        if start < len(tokens):
            if tokens[start].type == 'STRING':
                table_name = tokens[start].value[1:-1]  # Remove quotes
                if not asm.text_converter.set_conversion_table(table_name):
                    raise AssemblerError(f"Unknown conversion table: {table_name}", asm.current_line, filename=asm.current_filename)
            elif tokens[start].type == 'IDENTIFIER':
                table_name = tokens[start].value
                if not asm.text_converter.set_conversion_table(table_name):
                    raise AssemblerError(f"Unknown conversion table: {table_name}", asm.current_line, filename=asm.current_filename)

    elif directive == '!scr':
        # Emit string using screen code conversion
        if start < len(tokens) and tokens[start].type == 'STRING':
            string_val = tokens[start].value[1:-1]  # Remove quotes
            screen_bytes = asm.text_converter.convert_string(string_val, 'scr')
            for byte_val in screen_bytes:
                asm.emit_byte(byte_val)

    elif directive == '!scrxor':
        # Emit string using screen code conversion with XOR mask
        if start + 2 < len(tokens) and tokens[start].type == 'STRING':
            string_val = tokens[start].value[1:-1]  # Remove quotes
            # Expect comma then XOR value
            if tokens[start + 1].type == 'COMMA':
                xor_value, _ = evaluate_expression(asm, tokens, start + 2)
                screen_bytes = asm.text_converter.convert_string_with_xor(string_val, int(xor_value), 'scr')
                for byte_val in screen_bytes:
                    asm.emit_byte(byte_val)

    elif directive == '!fill':
        # Fill memory with value
        if start + 2 < len(tokens):
            count, _ = evaluate_expression(asm, tokens, start)
            # Skip comma
            value, _ = evaluate_expression(asm, tokens, start + 2)
            for _ in range(int(count)):
                asm.emit_byte(int(value))

    elif directive == '!hex' or directive == '!h':
        # Raw hex data input
        _process_hex_directive(asm, tokens, start)

    elif directive == '!skip':
        # Advance PC without output
        if start < len(tokens):
            count, _ = evaluate_expression(asm, tokens, start)
            asm.pc += int(count)

    elif directive == '!align':
        # Memory alignment
        _process_align_directive(asm, tokens, start)

    elif directive == '!zone':
        # Create new zone for local symbols
        zone_name = ""
        if start < len(tokens) and tokens[start].type in ['IDENTIFIER', 'STRING']:
            if tokens[start].type == 'STRING':
                zone_name = tokens[start].value[1:-1]
            else:
                zone_name = tokens[start].value
        asm.create_zone(zone_name)

    elif directive == '!address' or directive == '!addr':
        # Mark symbols as addresses (for type checking)
        # This is handled during symbol definition
        pass

    elif directive == '!cpu':
        # Set CPU type and update instruction set
        if start < len(tokens):
            # Handle CPU identifiers that might be split into multiple tokens (e.g., "65c02" -> "65" + "c02")
            cpu_parts = []
            i = start
            while i < len(tokens) and tokens[i].type in ['IDENTIFIER', 'DEC_NUMBER']:
                cpu_parts.append(tokens[i].value)
                i += 1

            if cpu_parts:
                asm.cpu_type = ''.join(cpu_parts)
                asm._update_instructions()
            else:
                raise AssemblerError("Expected CPU type identifier after !cpu", asm.current_line, filename=asm.current_filename)
        else:
            raise AssemblerError("Expected CPU type identifier after !cpu", asm.current_line)

    # Conditional assembly directives
    elif directive == '!if':
        _, consumed = asm.conditional_processor.process_if_directive(asm, tokens, start)
        return consumed

    elif directive == '!ifdef':
        _, consumed = asm.conditional_processor.process_ifdef_directive(asm, tokens, start)
        return consumed

    elif directive == '!ifndef':
        _, consumed = asm.conditional_processor.process_ifndef_directive(asm, tokens, start)
        return consumed

    elif directive == '!else':
        asm.conditional_processor.process_else_directive(asm)

    elif directive == '!fi':
        asm.conditional_processor.process_fi_directive(asm)

    # Loop and variable directives
    elif directive == '!set':
        asm.loop_processor.process_set_directive(asm, tokens, start)

    elif directive == '!for':
        # This will be handled specially in the assembler to collect loop body
        asm.loop_processor.process_for_directive(asm, tokens, start)

    elif directive == '!while':
        # This will be handled specially in the assembler to collect loop body
        asm.loop_processor.process_while_directive(asm, tokens, start)

    elif directive == '!do':
        # This will be handled specially in the assembler to collect loop body
        asm.loop_processor.process_do_directive(asm)

    elif directive == '!od':
        asm.loop_processor.process_od_directive(asm)

    elif directive == '!until':
        asm.loop_processor.process_until_directive(asm, tokens, start)

    # Macro directives
    elif directive == '!macro':
        asm.macro_system.process_macro_directive(asm, tokens, start)

    # File system directives
    elif directive == '!source' or directive == '!src':
        # File inclusion will be handled specially by the assembler
        # to integrate included lines into the assembly process
        pass  # Placeholder - actual processing in assembler

    elif directive == '!binary' or directive == '!bin':
        asm.file_manager.process_binary_directive(asm, tokens, start)

    # Segment management directives
    elif directive == '!pseudopc':
        asm.segment_manager.process_pseudopc_directive(asm, tokens, start)

    elif directive == '!realpc':
        asm.segment_manager.exit_pseudopc(asm)

    elif directive == '!initmem':
        asm.segment_manager.process_initmem_directive(asm, tokens, start)

    elif directive == '!xor':
        asm.segment_manager.process_xor_directive(asm, tokens, start)

    # Debug and error handling directives
    elif directive == '!warn':
        asm.debug_system.process_warn_directive(asm, tokens, start)

    elif directive == '!error':
        asm.debug_system.process_error_directive(asm, tokens, start)

    elif directive == '!serious':
        asm.debug_system.process_serious_directive(asm, tokens, start)

    elif directive == '!symbollist' or directive == '!sl':
        asm.debug_system.process_symbollist_directive(asm, tokens, start)

    else:
        raise AssemblerError(f"Unknown ACME directive: {directive}", asm.current_line, filename=asm.current_filename)
    
    return consumed

def process_directive(asm: 'Assembler6502', directive: str, tokens: List[Token], start: int):
    """Process traditional assembler directives."""
    directive = directive.lower()

    if directive == '.byte' or directive == '.db':
        # Same as !byte
        process_acme_directive(asm, '!byte', tokens, start)

    elif directive == '.word' or directive == '.dw':
        # Same as !word
        process_acme_directive(asm, '!word', tokens, start)

    elif directive == '.text':
        # Same as !text
        process_acme_directive(asm, '!text', tokens, start)

    elif directive == '.org':
        # Set origin address
        if start < len(tokens):
            address, _ = evaluate_expression(asm, tokens, start)
            asm.pc = int(address)
        else:
            raise AssemblerError("Expected address after .org", asm.current_line, filename=asm.current_filename)

    elif directive == '.equ':
        # Handled in process_line
        pass

    elif directive == '.ds':
        # Define storage (reserve bytes)
        if start < len(tokens):
            count, _ = evaluate_expression(asm, tokens, start)
            for _ in range(int(count)):
                asm.emit_byte(0)
        else:
            raise AssemblerError("Expected count after .ds", asm.current_line, filename=asm.current_filename)

    elif directive == '.end':
        # End of assembly
        pass

    else:
        raise AssemblerError(f"Unknown directive: {directive}", asm.current_line, filename=asm.current_filename)
