"""
File System Integration for pyasm6502
Handles !source/!src file inclusion and !binary/!bin binary data loading.
"""

import os
from pathlib import Path
from typing import List, Dict, Set, Optional, Tuple
from .datastructures import AssemblerError, Token
from .evaluator import evaluate_expression

# Forward declaration for type hinting
class Assembler6502:
    pass

class FileManager:
    """Manages file inclusion and binary loading with search paths."""

    def __init__(self, search_paths: Optional[List[str]] = None):
        self.search_paths: List[Path] = []
        if search_paths:
            for path in search_paths:
                self.search_paths.append(Path(path).resolve())

        # Always include current directory as first search path
        self.search_paths.insert(0, Path.cwd())

        # Track included files to prevent circular includes
        self.included_files: Set[Path] = set()
        self.include_stack: List[Tuple[Path, int]] = []  # (file_path, line_number)
        self.max_include_depth = 32

    def add_search_path(self, path: str) -> None:
        """Add a search path for file inclusion."""
        resolved_path = Path(path).resolve()
        if resolved_path not in self.search_paths:
            self.search_paths.append(resolved_path)

    def find_file(self, filename: str, current_file_dir: Optional[Path] = None) -> Path:
        """
        Find a file in the search paths.

        Args:
            filename: File to find (can include directory separators)
            current_file_dir: Directory of the file making the include (for relative paths)

        Returns:
            Path to the found file

        Raises:
            AssemblerError: If file is not found
        """
        # Handle different filename syntaxes
        search_name = filename

        # Remove angle brackets if present (<filename> syntax for library files)
        if filename.startswith('<') and filename.endswith('>'):
            search_name = filename[1:-1]
            # For library files, skip the current directory check
            search_paths = self.search_paths[1:] if len(self.search_paths) > 1 else []
        else:
            # Remove quotes if present
            if (filename.startswith('"') and filename.endswith('"')) or \
               (filename.startswith("'") and filename.endswith("'")):
                search_name = filename[1:-1]

            search_paths = self.search_paths

        # Try current file directory first for relative includes
        if current_file_dir and not filename.startswith('<'):
            candidate = current_file_dir / search_name
            if candidate.is_file():
                return candidate.resolve()

        # Search in all search paths
        for search_path in search_paths:
            candidate = search_path / search_name
            if candidate.is_file():
                return candidate.resolve()

        # File not found
        raise AssemblerError(f"File not found: {filename}", 0)

    def process_source_directive(self, asm: 'Assembler6502', tokens: List[Token], start: int) -> List[str]:
        """
        Process !source/!src directive to include another source file.

        Returns:
            List of source lines from the included file
        """
        if start >= len(tokens) or tokens[start].type != 'STRING':
            raise AssemblerError("!source requires a filename string", asm.current_line)

        filename = tokens[start].value[1:-1]  # Remove quotes

        # Get current file directory for relative path resolution
        current_file_dir = None
        if hasattr(asm, 'current_filename') and asm.current_filename:
            current_file_dir = Path(asm.current_filename).parent

        # Find the file
        try:
            file_path = self.find_file(filename, current_file_dir)
        except AssemblerError as e:
            raise AssemblerError(f"In !source directive: {str(e)}", asm.current_line)

        # Check for circular includes
        if file_path in self.included_files:
            include_chain = " -> ".join([str(p) for p, _ in self.include_stack])
            raise AssemblerError(
                f"Circular include detected: {include_chain} -> {file_path}",
                asm.current_line
            )

        # Check include depth
        if len(self.include_stack) >= self.max_include_depth:
            raise AssemblerError(
                f"Include depth exceeded (max {self.max_include_depth})",
                asm.current_line
            )

        # Read and return file contents
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                lines = f.readlines()

            # Remove trailing newlines but preserve empty lines
            lines = [line.rstrip('\n\r') for line in lines]

            # Track this include
            self.included_files.add(file_path)
            self.include_stack.append((file_path, asm.current_line))

            return lines

        except IOError as e:
            raise AssemblerError(f"Cannot read file {file_path}: {str(e)}", asm.current_line)

    def process_binary_directive(self, asm: 'Assembler6502', tokens: List[Token], start: int) -> None:
        """
        Process !binary/!bin directive to include binary data.

        Syntax: !binary "filename" [, size [, skip]]
        """
        if start >= len(tokens) or tokens[start].type != 'STRING':
            raise AssemblerError("!binary requires a filename string", asm.current_line)

        filename = tokens[start].value[1:-1]  # Remove quotes

        # Parse optional size and skip parameters
        size = None
        skip = 0
        token_pos = start + 1

        if token_pos < len(tokens) and tokens[token_pos].type == 'COMMA':
            token_pos += 1
            # Get size parameter
            if token_pos < len(tokens):
                size_value, consumed = evaluate_expression(asm, tokens, token_pos)
                size = int(size_value)
                token_pos += consumed

                # Check for skip parameter
                if token_pos < len(tokens) and tokens[token_pos].type == 'COMMA':
                    token_pos += 1
                    if token_pos < len(tokens):
                        skip_value, _ = evaluate_expression(asm, tokens, token_pos)
                        skip = int(skip_value)

        # Get current file directory for relative path resolution
        current_file_dir = None
        if hasattr(asm, 'current_filename') and asm.current_filename:
            current_file_dir = Path(asm.current_filename).parent

        # Find the file
        try:
            file_path = self.find_file(filename, current_file_dir)
        except AssemblerError as e:
            raise AssemblerError(f"In !binary directive: {str(e)}", asm.current_line)

        # Load and emit binary data
        try:
            with open(file_path, 'rb') as f:
                data = f.read()

            # Apply skip offset
            if skip > 0:
                if skip >= len(data):
                    raise AssemblerError(
                        f"Skip offset {skip} exceeds file size {len(data)}",
                        asm.current_line
                    )
                data = data[skip:]

            # Apply size limit
            if size is not None:
                if size > len(data):
                    raise AssemblerError(
                        f"Requested size {size} exceeds available data {len(data)}",
                        asm.current_line
                    )
                data = data[:size]

            # Emit each byte
            for byte in data:
                asm.emit_byte(byte)

        except IOError as e:
            raise AssemblerError(f"Cannot read binary file {file_path}: {str(e)}", asm.current_line)

    def finish_include(self, file_path: Path) -> None:
        """Mark an include as finished and remove it from the stack."""
        if self.include_stack and self.include_stack[-1][0] == file_path:
            self.include_stack.pop()
        # Keep the file in included_files to track all includes in this assembly

    def reset(self) -> None:
        """Reset the file manager state (for new assembly passes)."""
        self.included_files.clear()
        self.include_stack.clear()

    def get_include_info(self) -> Dict[str, any]:
        """Get information about current includes for debugging."""
        return {
            'search_paths': [str(p) for p in self.search_paths],
            'included_files': [str(p) for p in self.included_files],
            'include_stack': [(str(p), line) for p, line in self.include_stack],
            'include_depth': len(self.include_stack)
        }