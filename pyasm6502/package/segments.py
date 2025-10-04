"""
Segment Management for pyasm6502
Handles !pseudopc, !initmem, !xor, and segment overlap detection.
"""

from typing import List, Dict, Optional, Tuple, Union
from .datastructures import AssemblerError, Token
from .evaluator import evaluate_expression

# Forward declaration for type hinting
class Assembler6502:
    pass

class Segment:
    """Represents a memory segment."""
    def __init__(self, start_addr: int, end_addr: int, data: Dict[int, int], segment_type: str = 'normal'):
        self.start_addr = start_addr
        self.end_addr = end_addr
        self.data = data.copy()  # addr -> byte mapping
        self.segment_type = segment_type  # 'normal', 'overlay', 'invisible'
        self.name = f"segment_{start_addr:04X}_{end_addr:04X}"

    def overlaps_with(self, other: 'Segment') -> bool:
        """Check if this segment overlaps with another segment."""
        if self.segment_type == 'invisible' or other.segment_type == 'invisible':
            return False  # Invisible segments don't count as overlaps

        if self.segment_type == 'overlay' or other.segment_type == 'overlay':
            return False  # Overlay segments are allowed to overlap

        return not (self.end_addr < other.start_addr or self.start_addr > other.end_addr)

class SegmentManager:
    """Handles segment management, pseudopc, and memory initialization."""

    def __init__(self):
        self.segments: List[Segment] = []
        self.pseudopc_stack: List[Tuple[int, int]] = []  # (real_pc, pseudo_pc)
        self.init_memory_value: Optional[int] = None  # Default memory fill value
        self.xor_value: int = 0  # XOR encryption value
        self.current_pseudo_pc: Optional[int] = None

    def set_init_memory(self, value: int) -> None:
        """Set the default memory initialization value (!initmem directive)."""
        self.init_memory_value = value & 0xFF

    def set_xor_value(self, value: int) -> None:
        """Set the XOR encryption value (!xor directive)."""
        self.xor_value = value & 0xFF

    def enter_pseudopc(self, asm: 'Assembler6502', pseudo_addr: int) -> None:
        """
        Enter pseudopc mode (!pseudopc directive).
        Assembly continues at the pseudo address while the real PC advances normally.
        """
        # Save current real and pseudo PC
        self.pseudopc_stack.append((asm.pc, self.current_pseudo_pc or asm.pc))

        # Set new pseudo PC
        self.current_pseudo_pc = pseudo_addr

    def exit_pseudopc(self, asm: 'Assembler6502') -> None:
        """
        Exit pseudopc mode (end of !pseudopc block or explicit exit).
        """
        if not self.pseudopc_stack:
            raise AssemblerError("No !pseudopc block to exit", asm.current_line)

        # Restore previous PC state
        real_pc, prev_pseudo_pc = self.pseudopc_stack.pop()
        self.current_pseudo_pc = prev_pseudo_pc if self.pseudopc_stack else None

    def get_effective_pc(self, asm: 'Assembler6502') -> int:
        """
        Get the effective program counter.
        Returns pseudo PC if in pseudopc mode, otherwise real PC.
        """
        return self.current_pseudo_pc if self.current_pseudo_pc is not None else asm.pc

    def get_unpseudo_address(self, asm: 'Assembler6502', pseudo_addr: int) -> int:
        """
        Convert a pseudo address to real address (& operator functionality).
        """
        if not self.pseudopc_stack:
            return pseudo_addr  # Not in pseudopc mode

        # Calculate the offset from the start of the pseudopc block
        real_pc, pseudo_start = self.pseudopc_stack[-1]
        offset = pseudo_addr - pseudo_start

        return real_pc + offset

    def emit_byte_with_segments(self, asm: 'Assembler6502', value: int) -> None:
        """
        Emit a byte with segment management.
        Handles pseudopc, memory initialization, and XOR encryption.
        """
        effective_pc = self.get_effective_pc(asm)

        # Apply XOR encryption if enabled
        if self.xor_value != 0:
            value ^= self.xor_value

        # Store in output at effective address
        asm.output_dict[effective_pc] = value & 0xFF

        # Advance both real and pseudo PC
        if self.current_pseudo_pc is not None:
            self.current_pseudo_pc += 1
        asm.pc += 1

    def process_pseudopc_directive(self, asm: 'Assembler6502', tokens: List[Token], start: int) -> None:
        """
        Process !pseudopc directive.
        Syntax: !pseudopc address
        """
        if start >= len(tokens):
            raise AssemblerError("!pseudopc requires an address", asm.current_line)

        # Evaluate the pseudo address
        pseudo_addr, _ = evaluate_expression(asm, tokens, start)
        self.enter_pseudopc(asm, int(pseudo_addr))

    def process_initmem_directive(self, asm: 'Assembler6502', tokens: List[Token], start: int) -> None:
        """
        Process !initmem directive.
        Syntax: !initmem value
        """
        if start >= len(tokens):
            raise AssemblerError("!initmem requires a value", asm.current_line)

        # Evaluate the initialization value
        init_value, _ = evaluate_expression(asm, tokens, start)
        self.set_init_memory(int(init_value))

    def process_xor_directive(self, asm: 'Assembler6502', tokens: List[Token], start: int) -> None:
        """
        Process !xor directive.
        Syntax: !xor value
        """
        if start >= len(tokens):
            raise AssemblerError("!xor requires a value", asm.current_line)

        # Evaluate the XOR value
        xor_value, _ = evaluate_expression(asm, tokens, start)
        self.set_xor_value(int(xor_value))

    def analyze_segments(self, asm: 'Assembler6502') -> List[Segment]:
        """
        Analyze the output to create segment information.
        """
        if not asm.output_dict:
            return []

        # Sort addresses
        sorted_addrs = sorted(asm.output_dict.keys())
        if not sorted_addrs:
            return []

        # Group consecutive addresses into segments
        segments = []
        current_start = sorted_addrs[0]
        current_end = sorted_addrs[0]
        current_data = {current_start: asm.output_dict[current_start]}

        for addr in sorted_addrs[1:]:
            if addr == current_end + 1:
                # Consecutive address - extend current segment
                current_end = addr
                current_data[addr] = asm.output_dict[addr]
            else:
                # Gap found - finalize current segment and start new one
                segments.append(Segment(current_start, current_end, current_data))
                current_start = addr
                current_end = addr
                current_data = {addr: asm.output_dict[addr]}

        # Add the last segment
        segments.append(Segment(current_start, current_end, current_data))

        self.segments = segments
        return segments

    def detect_overlaps(self, asm: 'Assembler6502') -> List[str]:
        """
        Detect segment overlaps and return warning messages.
        """
        warnings = []
        segments = self.analyze_segments(asm)

        for i, segment1 in enumerate(segments):
            for segment2 in segments[i + 1:]:
                if segment1.overlaps_with(segment2):
                    warnings.append(
                        f"Segment overlap: "
                        f"${segment1.start_addr:04X}-${segment1.end_addr:04X} "
                        f"overlaps with "
                        f"${segment2.start_addr:04X}-${segment2.end_addr:04X}"
                    )

        return warnings

    def fill_gaps_with_initmem(self, asm: 'Assembler6502', start_addr: int, end_addr: int) -> None:
        """
        Fill gaps in memory with the initialization value if set.
        Only fills small gaps within segments, not large empty areas.
        """
        if self.init_memory_value is None:
            return  # No initialization value set

        # Only fill gaps if they are reasonable size (e.g., < 256 bytes)
        gap_size = end_addr - start_addr + 1
        if gap_size > 256:
            return  # Gap too large, don't fill

        for addr in range(start_addr, end_addr + 1):
            if addr not in asm.output_dict:
                asm.output_dict[addr] = self.init_memory_value

    def get_memory_usage_info(self, asm: 'Assembler6502') -> Dict[str, any]:
        """
        Get information about memory usage for debugging.
        """
        segments = self.analyze_segments(asm)

        total_bytes = sum(len(seg.data) for seg in segments)
        address_range = (min(asm.output_dict.keys()), max(asm.output_dict.keys())) if asm.output_dict else (0, 0)

        return {
            'total_segments': len(segments),
            'total_bytes': total_bytes,
            'address_range': address_range,
            'segments': [
                {
                    'start': seg.start_addr,
                    'end': seg.end_addr,
                    'size': len(seg.data),
                    'type': seg.segment_type
                } for seg in segments
            ],
            'pseudopc_depth': len(self.pseudopc_stack),
            'xor_enabled': self.xor_value != 0,
            'init_memory': self.init_memory_value
        }

    def reset(self) -> None:
        """Reset the segment manager state (for new assembly passes)."""
        self.segments.clear()
        self.pseudopc_stack.clear()
        self.current_pseudo_pc = None
        # Keep init_memory_value and xor_value between passes