#!/usr/bin/env python3
"""
pyasm6502 - ACME-Compatible 6502 Assembler
Entry point for the assembler
"""

import sys
import argparse
from pathlib import Path

from .assembler import Assembler6502
from .package.datastructures import AssemblerError, OutputFormat

def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(description='pyasm6502 - ACME-Compatible 6502 Assembler')
    parser.add_argument('input', help='Input assembly file')
    parser.add_argument('-o', '--output', help='Output binary file')
    parser.add_argument('-f', '--format', choices=['plain', 'cbm', 'apple', 'hex'],
                        default='plain', help='Output file format')
    parser.add_argument('-l', '--list', help='Generate listing file')
    parser.add_argument('-s', '--symbols', action='store_true', help='Show symbol table')
    parser.add_argument('--setpc', type=str, help='Set program counter (e.g., $C000)')
    parser.add_argument('-I', '--include', action='append', help='Add include search path')
    parser.add_argument('-v', '--verbose', type=int, default=1, help='Set verbosity level (1=normal, 2=verbose, 3=debug)')
    parser.add_argument('--vicelabels', type=str, help='Generate VICE label file')

    args = parser.parse_args()

    try:
        # Read input file
        input_path = Path(args.input)
        if not input_path.exists():
            print(f"Error: Input file '{args.input}' not found")
            return 1

        with open(input_path, 'r', encoding='utf-8') as f:
            source_lines = f.readlines()

        # Create assembler
        assembler = Assembler6502()
        assembler.output_format = OutputFormat(args.format)

        # Add include paths if specified
        if args.include:
            for include_path in args.include:
                assembler.file_manager.add_search_path(include_path)

        # Set debug verbosity level
        assembler.debug_system.set_verbosity(args.verbose)

        # Set program counter if specified
        if args.setpc:
            if args.setpc.startswith('$'):
                assembler.pc = int(args.setpc[1:], 16)
            elif args.setpc.startswith('0x'):
                assembler.pc = int(args.setpc[2:], 16)
            else:
                assembler.pc = int(args.setpc)

        # Assemble
        binary_output = assembler.assemble(source_lines, str(input_path.absolute()))

        # Determine output filename
        if args.output:
            output_path = Path(args.output)
        elif assembler.output_filename:
            output_path = Path(assembler.output_filename)
        else:
            if args.format == 'hex':
                output_path = input_path.with_suffix('.hex')
            else:
                output_path = input_path.with_suffix('.bin')

        # Write output
        if args.format == 'hex':
            with open(output_path, 'wb') as f:
                f.write(binary_output)
        else:
            with open(output_path, 'wb') as f:
                f.write(binary_output)

        print(f"Assembly completed: {len(binary_output)} bytes written to {output_path}")

        # Show symbol table if requested
        if args.symbols:
            symbols = assembler.get_symbol_table()
            if symbols:
                print("\nSymbol Table:")
                for symbol, value in sorted(symbols.items()):
                    print(f"  {symbol:16} = ${value:04X} ({value})")

        # Generate listing file if requested
        if args.list:
            listing_path = Path(args.list)
            with open(listing_path, 'w') as f:
                f.write(f"pyasm6502 - Listing File\n")
                f.write(f"Source: {input_path}\n")
                f.write(f"Output: {output_path} ({len(binary_output)} bytes)\n")
                f.write(f"Format: {args.format}\n\n")

                for line_num, line in enumerate(source_lines, 1):
                    f.write(f"{line_num:4d}: {line}")

            print(f"Listing file written to {listing_path}")

        # Generate VICE labels if requested
        if args.vicelabels:
            vice_path = Path(args.vicelabels)
            assembler.debug_system.export_vice_labels(assembler, str(vice_path))

        return 0

    except Exception as e:
        print(f"Error: {e}")
        return 1


if __name__ == '__main__':
    sys.exit(main())