from .datastructures import OutputFormat

# Forward declaration for type hinting
class Assembler6502:
    pass

def generate_output(asm: 'Assembler6502') -> bytearray:
    """Generate output in the specified format."""
    if asm.output_format == OutputFormat.PLAIN:
        return _generate_plain_output(asm)
    elif asm.output_format == OutputFormat.CBM:
        return _generate_cbm_output(asm)
    elif asm.output_format == OutputFormat.HEX:
        return _generate_hex_output(asm)
    else:
        return _generate_plain_output(asm)

def _generate_plain_output(asm: 'Assembler6502') -> bytearray:
    """Generate plain binary output (sparse-aware)."""
    if not hasattr(asm, 'output_dict') or not asm.output_dict:
        return bytearray()

    # Find the largest contiguous block of data to avoid huge sparse files
    addresses = sorted(asm.output_dict.keys())

    # Find the main program block (skip isolated bytes like reset vectors)
    blocks = []
    current_block_start = addresses[0]
    current_block_end = addresses[0]

    for i in range(1, len(addresses)):
        if addresses[i] - addresses[i-1] <= 256:  # Allow small gaps
            current_block_end = addresses[i]
        else:
            blocks.append((current_block_start, current_block_end))
            current_block_start = addresses[i]
            current_block_end = addresses[i]

    blocks.append((current_block_start, current_block_end))

    # Find the largest block
    largest_block = max(blocks, key=lambda x: x[1] - x[0])
    min_addr, max_addr = largest_block

    size = max_addr - min_addr + 1
    output = bytearray(size)

    for addr, value in asm.output_dict.items():
        if min_addr <= addr <= max_addr:
            output[addr - min_addr] = value

    return output

def _generate_cbm_output(asm: 'Assembler6502') -> bytearray:
    """Generate CBM format output (with load address)."""
    plain_output = _generate_plain_output(asm)
    if not hasattr(asm, 'output_dict') or not asm.output_dict:
        return bytearray()

    min_addr = min(asm.output_dict.keys())

    # CBM format: little-endian load address followed by data
    cbm_output = bytearray()
    cbm_output.append(min_addr & 0xFF)
    cbm_output.append((min_addr >> 8) & 0xFF)
    cbm_output.extend(plain_output)

    return cbm_output

def _generate_hex_output(asm: 'Assembler6502') -> bytes:
    """Generate Intel HEX format output."""
    if not hasattr(asm, 'output_dict') or not asm.output_dict:
        return b''

    hex_lines = []

    # Sort addresses
    addresses = sorted(asm.output_dict.keys())

    # Group consecutive addresses into records (max 16 bytes per record)
    i = 0
    while i < len(addresses):
        start_addr = addresses[i]
        record_data = [asm.output_dict[start_addr]]
        record_addr = start_addr
        i += 1

        # Add consecutive bytes (up to 16 per record)
        while (i < len(addresses) and
               len(record_data) < 16 and
               addresses[i] == addresses[i-1] + 1):
            record_data.append(asm.output_dict[addresses[i]])
            i += 1

        # Generate Intel HEX record
        data_count = len(record_data)
        record_type = 0x00  # Data record

        # Calculate checksum
        checksum = data_count + ((record_addr >> 8) & 0xFF) + (record_addr & 0xFF) + record_type
        for byte_val in record_data:
            checksum += byte_val
        checksum = (-checksum) & 0xFF

        # Format record
        hex_line = f":{data_count:02X}{record_addr:04X}{record_type:02X}"
        for byte_val in record_data:
            hex_line += f"{byte_val:02X}"
        hex_line += f"{checksum:02X}\n"

        hex_lines.append(hex_line)

    # Add end-of-file record
    hex_lines.append(":00000001FF\n")

    return ''.join(hex_lines).encode('ascii')
