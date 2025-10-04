"""
Debug and Error Handling for pyasm6502
Handles !warn, !error, !serious, !symbollist directives and enhanced error reporting.
"""

import sys
from typing import List, Dict, Any, Optional, TextIO, Tuple
from .datastructures import AssemblerError, Token
from .evaluator import evaluate_expression

# Forward declaration for type hinting
class Assembler6502:
    pass

class DebugLevel:
    """Debug/warning levels."""
    WARN = "warn"
    ERROR = "error"
    SERIOUS = "serious"

class DebugSystem:
    """Handles debugging output, warnings, errors, and symbol table generation."""

    def __init__(self):
        self.warnings: List[Tuple[str, int, str]] = []  # (message, line, filename)
        self.errors: List[Tuple[str, int, str]] = []    # (message, line, filename)
        self.verbosity_level = 1  # 0-3
        self.output_stream: TextIO = sys.stdout
        self.suppress_warnings = False

    def set_verbosity(self, level: int) -> None:
        """Set verbosity level (0-3)."""
        self.verbosity_level = max(0, min(3, level))

    def set_output_stream(self, stream: TextIO) -> None:
        """Set output stream for debug messages."""
        self.output_stream = stream

    def process_warn_directive(self, asm: 'Assembler6502', tokens: List[Token], start: int) -> None:
        """
        Process !warn directive.
        Syntax: !warn "message" [, expression1, expression2, ...]
        """
        if start >= len(tokens):
            raise AssemblerError("!warn requires at least a message string", asm.current_line)

        # Parse the message string
        if tokens[start].type != 'STRING':
            raise AssemblerError("!warn requires a message string as first argument", asm.current_line)

        message = tokens[start].value[1:-1]  # Remove quotes
        current_pos = start + 1

        # Parse optional expressions after comma
        expressions = []
        while current_pos < len(tokens):
            if tokens[current_pos].type == 'COMMA':
                current_pos += 1
                # Parse expression until next comma or end
                expr_end = current_pos
                while expr_end < len(tokens) and tokens[expr_end].type != 'COMMA':
                    expr_end += 1

                if current_pos < len(tokens):
                    try:
                        # Create a slice of tokens for this expression
                        expr_tokens = tokens[current_pos:expr_end]
                        value, _ = evaluate_expression(asm, expr_tokens, 0)
                        expressions.append(str(value))
                    except Exception as e:
                        expressions.append(f"<error: {e}>")
                current_pos = expr_end
            else:
                break

        # Construct final message
        if expressions:
            final_message = message + " " + " ".join(expressions)
        else:
            final_message = message

        self.generate_warning(final_message, asm.current_line, asm.current_filename)

    def process_error_directive(self, asm: 'Assembler6502', tokens: List[Token], start: int) -> None:
        """
        Process !error directive.
        Syntax: !error "message"
        """
        if start >= len(tokens) or tokens[start].type != 'STRING':
            raise AssemblerError("!error requires a message string", asm.current_line)

        message = tokens[start].value[1:-1]  # Remove quotes
        self.generate_error(message, asm.current_line, asm.current_filename)

    def process_serious_directive(self, asm: 'Assembler6502', tokens: List[Token], start: int) -> None:
        """
        Process !serious directive.
        Syntax: !serious "message"
        """
        if start >= len(tokens) or tokens[start].type != 'STRING':
            raise AssemblerError("!serious requires a message string", asm.current_line)

        message = tokens[start].value[1:-1]  # Remove quotes
        self.generate_serious_error(message, asm.current_line, asm.current_filename)

    def process_symbollist_directive(self, asm: 'Assembler6502', tokens: List[Token], start: int) -> None:
        """
        Process !symbollist/!sl directive.
        Syntax: !symbollist [filename]
        """
        filename = None
        if start < len(tokens) and tokens[start].type == 'STRING':
            filename = tokens[start].value[1:-1]  # Remove quotes

        self.export_symbol_table(asm, filename)

    def generate_warning(self, message: str, line: int, filename: str = "") -> None:
        """Generate a warning message."""
        if self.suppress_warnings:
            return

        self.warnings.append((message, line, filename))

        if self.verbosity_level >= 1:
            location = f"File {filename}, line {line}: " if filename else f"Line {line}: "
            warning_msg = f"Warning - {location}{message}"
            print(warning_msg, file=self.output_stream)

    def generate_error(self, message: str, line: int, filename: str = "") -> None:
        """Generate a non-fatal error message."""
        self.errors.append((message, line, filename))

        location = f"File {filename}, line {line}: " if filename else f"Line {line}: "
        error_msg = f"Error - {location}{message}"
        print(error_msg, file=self.output_stream)

    def generate_serious_error(self, message: str, line: int, filename: str = "") -> None:
        """Generate a serious (fatal) error and raise exception."""
        self.errors.append((message, line, filename))

        location = f"File {filename}, line {line}: " if filename else f"Line {line}: "
        error_msg = f"Serious Error - {location}{message}"
        print(error_msg, file=self.output_stream)

        # Serious errors are fatal
        raise AssemblerError(f"Serious error: {message}", line)

    def export_symbol_table(self, asm: 'Assembler6502', filename: Optional[str] = None) -> None:
        """
        Export symbol table to file or stdout.
        """
        symbols = asm.get_symbol_table()

        # Format symbol table
        lines = []
        lines.append("; Symbol table generated by pyasm6502")
        lines.append("")

        # Sort symbols by name
        sorted_symbols = sorted(symbols.items())

        for name, value in sorted_symbols:
            lines.append(f"{name:20} = ${value:04X} ({value})")

        # Add statistics
        lines.append("")
        lines.append(f"; Total symbols: {len(symbols)}")

        # Output to file or stdout
        if filename:
            try:
                with open(filename, 'w', encoding='utf-8') as f:
                    for line in lines:
                        f.write(line + '\n')
                if self.verbosity_level >= 1:
                    print(f"Symbol table written to {filename}", file=self.output_stream)
            except IOError as e:
                self.generate_error(f"Cannot write symbol table to {filename}: {str(e)}", 0)
        else:
            # Output to stdout
            for line in lines:
                print(line, file=self.output_stream)

    def export_vice_labels(self, asm: 'Assembler6502', filename: str) -> None:
        """
        Export symbols in VICE label format.
        Format: add_label $address .label_name
        """
        symbols = asm.get_symbol_table()

        try:
            with open(filename, 'w', encoding='utf-8') as f:
                f.write("# VICE label file generated by pyasm6502\n")

                # Sort symbols by address, then by name
                sorted_symbols = sorted(symbols.items(), key=lambda x: (x[1], x[0]))

                for name, value in sorted_symbols:
                    # Convert symbol names to VICE format (prefix with .)
                    vice_name = name if name.startswith('.') else f".{name}"
                    f.write(f"add_label ${value:04X} {vice_name}\n")

            if self.verbosity_level >= 1:
                print(f"VICE labels written to {filename}", file=self.output_stream)

        except IOError as e:
            self.generate_error(f"Cannot write VICE labels to {filename}: {str(e)}", 0)

    def get_enhanced_error_message(self, error: AssemblerError, source_lines: List[str]) -> str:
        """
        Generate enhanced error message with context.
        """
        if not source_lines or error.line_num <= 0 or error.line_num > len(source_lines):
            return str(error)

        # Get the error line and surrounding context
        error_line_idx = error.line_num - 1
        context_lines = []

        # Add lines before error (up to 2)
        start_idx = max(0, error_line_idx - 2)
        for i in range(start_idx, error_line_idx):
            context_lines.append(f"  {i + 1:4}: {source_lines[i].rstrip()}")

        # Add error line with highlight
        error_text = source_lines[error_line_idx].rstrip()
        context_lines.append(f"> {error.line_num:4}: {error_text}")

        # Add lines after error (up to 1)
        end_idx = min(len(source_lines), error_line_idx + 2)
        for i in range(error_line_idx + 1, end_idx):
            context_lines.append(f"  {i + 1:4}: {source_lines[i].rstrip()}")

        # Combine with original error message
        enhanced_msg = f"{str(error)}\n"
        enhanced_msg += "Context:\n"
        enhanced_msg += "\n".join(context_lines)

        return enhanced_msg

    def get_diagnostic_info(self, asm: 'Assembler6502') -> Dict[str, Any]:
        """
        Get diagnostic information for debugging.
        """
        info = {
            'warnings_count': len(self.warnings),
            'errors_count': len(self.errors),
            'verbosity_level': self.verbosity_level,
            'warnings': self.warnings,
            'errors': self.errors
        }

        # Add assembler state info
        if hasattr(asm, 'segment_manager'):
            info['memory_usage'] = asm.segment_manager.get_memory_usage_info(asm)

        if hasattr(asm, 'file_manager'):
            info['file_includes'] = asm.file_manager.get_include_info()

        if hasattr(asm, 'conditional_processor'):
            info['conditional_depth'] = asm.conditional_processor.get_current_depth()

        if hasattr(asm, 'macro_system'):
            info['macro_count'] = len(asm.macro_system.macros)

        return info

    def reset(self) -> None:
        """Reset debug system state (for new assembly passes)."""
        self.warnings.clear()
        self.errors.clear()

    def finalize(self, asm: 'Assembler6502') -> bool:
        """
        Finalize debug output and return success status.
        Returns False if there were serious errors.
        """
        success = len(self.errors) == 0

        if self.verbosity_level >= 2:
            # Show summary
            print(f"\nAssembly summary:", file=self.output_stream)
            print(f"  Warnings: {len(self.warnings)}", file=self.output_stream)
            print(f"  Errors: {len(self.errors)}", file=self.output_stream)

            if hasattr(asm, 'segment_manager'):
                info = asm.segment_manager.get_memory_usage_info(asm)
                print(f"  Segments: {info['total_segments']}", file=self.output_stream)
                print(f"  Total bytes: {info['total_bytes']}", file=self.output_stream)

        return success