# Standard 6502 instruction set
INSTRUCTIONS_6502 = {
    # Load/Store Operations
    'LDA': {
        'IMM': (0xA9, 2), 'ZP': (0xA5, 2), 'ZPX': (0xB5, 2), 'ABS': (0xAD, 3),
        'ABSX': (0xBD, 3), 'ABSY': (0xB9, 3), 'INDX': (0xA1, 2), 'INDY': (0xB1, 2)
    },
    'LDX': {
        'IMM': (0xA2, 2), 'ZP': (0xA6, 2), 'ZPY': (0xB6, 2), 'ABS': (0xAE, 3), 'ABSY': (0xBE, 3)
    },
    'LDY': {
        'IMM': (0xA0, 2), 'ZP': (0xA4, 2), 'ZPX': (0xB4, 2), 'ABS': (0xAC, 3), 'ABSX': (0xBC, 3)
    },
    'STA': {
        'ZP': (0x85, 2), 'ZPX': (0x95, 2), 'ABS': (0x8D, 3),
        'ABSX': (0x9D, 3), 'ABSY': (0x99, 3), 'INDX': (0x81, 2), 'INDY': (0x91, 2)
    },
    'STX': {'ZP': (0x86, 2), 'ZPY': (0x96, 2), 'ABS': (0x8E, 3)},
    'STY': {'ZP': (0x84, 2), 'ZPX': (0x94, 2), 'ABS': (0x8C, 3)},

    # Transfer Operations
    'TAX': {'IMP': (0xAA, 1)}, 'TAY': {'IMP': (0xA8, 1)}, 'TXA': {'IMP': (0x8A, 1)},
    'TYA': {'IMP': (0x98, 1)}, 'TSX': {'IMP': (0xBA, 1)}, 'TXS': {'IMP': (0x9A, 1)},

    # Stack Operations
    'PHA': {'IMP': (0x48, 1)}, 'PLA': {'IMP': (0x68, 1)},
    'PHP': {'IMP': (0x08, 1)}, 'PLP': {'IMP': (0x28, 1)},

    # Arithmetic Operations
    'ADC': {
        'IMM': (0x69, 2), 'ZP': (0x65, 2), 'ZPX': (0x75, 2), 'ABS': (0x6D, 3),
        'ABSX': (0x7D, 3), 'ABSY': (0x79, 3), 'INDX': (0x61, 2), 'INDY': (0x71, 2)
    },
    'SBC': {
        'IMM': (0xE9, 2), 'ZP': (0xE5, 2), 'ZPX': (0xF5, 2), 'ABS': (0xED, 3),
        'ABSX': (0xFD, 3), 'ABSY': (0xF9, 3), 'INDX': (0xE1, 2), 'INDY': (0xF1, 2)
    },

    # Increment/Decrement
    'INC': {'ZP': (0xE6, 2), 'ZPX': (0xF6, 2), 'ABS': (0xEE, 3), 'ABSX': (0xFE, 3)},
    'DEC': {'ZP': (0xC6, 2), 'ZPX': (0xD6, 2), 'ABS': (0xCE, 3), 'ABSX': (0xDE, 3)},
    'INX': {'IMP': (0xE8, 1)}, 'INY': {'IMP': (0xC8, 1)},
    'DEX': {'IMP': (0xCA, 1)}, 'DEY': {'IMP': (0x88, 1)},

    # Logical Operations
    'AND': {
        'IMM': (0x29, 2), 'ZP': (0x25, 2), 'ZPX': (0x35, 2), 'ABS': (0x2D, 3),
        'ABSX': (0x3D, 3), 'ABSY': (0x39, 3), 'INDX': (0x21, 2), 'INDY': (0x31, 2)
    },
    'ORA': {
        'IMM': (0x09, 2), 'ZP': (0x05, 2), 'ZPX': (0x15, 2), 'ABS': (0x0D, 3),
        'ABSX': (0x1D, 3), 'ABSY': (0x19, 3), 'INDX': (0x01, 2), 'INDY': (0x11, 2)
    },
    'EOR': {
        'IMM': (0x49, 2), 'ZP': (0x45, 2), 'ZPX': (0x55, 2), 'ABS': (0x4D, 3),
        'ABSX': (0x5D, 3), 'ABSY': (0x59, 3), 'INDX': (0x41, 2), 'INDY': (0x51, 2)
    },

    # Shift Operations
    'ASL': {'ACC': (0x0A, 1), 'ZP': (0x06, 2), 'ZPX': (0x16, 2), 'ABS': (0x0E, 3), 'ABSX': (0x1E, 3)},
    'LSR': {'ACC': (0x4A, 1), 'ZP': (0x46, 2), 'ZPX': (0x56, 2), 'ABS': (0x4E, 3), 'ABSX': (0x5E, 3)},
    'ROL': {'ACC': (0x2A, 1), 'ZP': (0x26, 2), 'ZPX': (0x36, 2), 'ABS': (0x2E, 3), 'ABSX': (0x3E, 3)},
    'ROR': {'ACC': (0x6A, 1), 'ZP': (0x66, 2), 'ZPX': (0x76, 2), 'ABS': (0x6E, 3), 'ABSX': (0x7E, 3)},

    # Compare Operations
    'CMP': {
        'IMM': (0xC9, 2), 'ZP': (0xC5, 2), 'ZPX': (0xD5, 2), 'ABS': (0xCD, 3),
        'ABSX': (0xDD, 3), 'ABSY': (0xD9, 3), 'INDX': (0xC1, 2), 'INDY': (0xD1, 2)
    },
    'CPX': {'IMM': (0xE0, 2), 'ZP': (0xE4, 2), 'ABS': (0xEC, 3)},
    'CPY': {'IMM': (0xC0, 2), 'ZP': (0xC4, 2), 'ABS': (0xCC, 3)},

    # Branch Operations
    'BCC': {'REL': (0x90, 2)}, 'BCS': {'REL': (0xB0, 2)}, 'BEQ': {'REL': (0xF0, 2)},
    'BMI': {'REL': (0x30, 2)}, 'BNE': {'REL': (0xD0, 2)}, 'BPL': {'REL': (0x10, 2)},
    'BVC': {'REL': (0x50, 2)}, 'BVS': {'REL': (0x70, 2)},

    # Jump Operations
    'JMP': {'ABS': (0x4C, 3), 'IND': (0x6C, 3)},
    'JSR': {'ABS': (0x20, 3)},
    'RTS': {'IMP': (0x60, 1)},

    # Interrupt Operations
    'BRK': {'IMP': (0x00, 1)}, 'RTI': {'IMP': (0x40, 1)},

    # Flag Operations
    'CLC': {'IMP': (0x18, 1)}, 'SEC': {'IMP': (0x38, 1)}, 'CLI': {'IMP': (0x58, 1)},
    'SEI': {'IMP': (0x78, 1)}, 'CLV': {'IMP': (0xB8, 1)}, 'CLD': {'IMP': (0xD8, 1)},
    'SED': {'IMP': (0xF8, 1)},

    # Test Operations
    'BIT': {'ZP': (0x24, 2), 'ABS': (0x2C, 3)},

    # No Operation
    'NOP': {'IMP': (0xEA, 1)},
}

# 65C02 CMOS extensions (standard R65C02 and W65C02)
INSTRUCTIONS_65C02 = {
    'STZ': {'ZP': (0x64, 2), 'ZPX': (0x74, 2), 'ABS': (0x9C, 3), 'ABSX': (0x9E, 3)},
    'BRA': {'REL': (0x80, 2)},
    'PHX': {'IMP': (0xDA, 1)}, 'PLX': {'IMP': (0xFA, 1)},
    'PHY': {'IMP': (0x5A, 1)}, 'PLY': {'IMP': (0x7A, 1)},
    'TSB': {'ZP': (0x04, 2), 'ABS': (0x0C, 3)},
    'TRB': {'ZP': (0x14, 2), 'ABS': (0x1C, 3)},
    # 65C02 specific addressing modes for existing instructions
    'ORA': {'ZP_IND': (0x12, 2)},  # (zp)
    'AND': {'ZP_IND': (0x32, 2)},  # (zp)
    'EOR': {'ZP_IND': (0x52, 2)},  # (zp)
    'ADC': {'ZP_IND': (0x72, 2)},  # (zp)
    'STA': {'ZP_IND': (0x92, 2)},  # (zp)
    'LDA': {'ZP_IND': (0xB2, 2)},  # (zp)
    'CMP': {'ZP_IND': (0xD2, 2)},  # (zp)
    'SBC': {'ZP_IND': (0xF2, 2)},  # (zp)
    # 65C02 specific addressing modes for BIT instruction
    'BIT': {'ZPX': (0x34, 2), 'ABSX': (0x3C, 3), 'IMM': (0x89, 2)},
    # 65C02 specific addressing modes for JMP
    'JMP': {'ABS_X_IND': (0x7C, 3)},  # jmp ($nnnn,x)
    # 65C02 accumulator addressing modes
    'INC': {'IMP': (0x1A, 1)},  # inc a
    'DEC': {'IMP': (0x3A, 1)},  # dec a
}

# NMOS 6502 undocumented instructions
INSTRUCTIONS_NMOS6502 = {
    # Undocumented NMOS 6502 opcodes
    'SLO': {  # Shift Left then OR
        'ZP': (0x07, 2), 'ZPX': (0x17, 2), 'ABS': (0x0F, 3), 'ABSX': (0x1F, 3),
        'ABSY': (0x1B, 3), 'INDX': (0x03, 2), 'INDY': (0x13, 2)
    },
    'RLA': {  # Rotate Left then AND
        'ZP': (0x27, 2), 'ZPX': (0x37, 2), 'ABS': (0x2F, 3), 'ABSX': (0x3F, 3),
        'ABSY': (0x3B, 3), 'INDX': (0x23, 2), 'INDY': (0x33, 2)
    },
    'SRE': {  # Shift Right then EOR
        'ZP': (0x47, 2), 'ZPX': (0x57, 2), 'ABS': (0x4F, 3), 'ABSX': (0x5F, 3),
        'ABSY': (0x5B, 3), 'INDX': (0x43, 2), 'INDY': (0x53, 2)
    },
    'RRA': {  # Rotate Right then ADC
        'ZP': (0x67, 2), 'ZPX': (0x77, 2), 'ABS': (0x6F, 3), 'ABSX': (0x7F, 3),
        'ABSY': (0x7B, 3), 'INDX': (0x63, 2), 'INDY': (0x73, 2)
    },
    'SAX': {  # Store A AND X
        'ZP': (0x87, 2), 'ZPY': (0x97, 2), 'ABS': (0x8F, 3), 'INDX': (0x83, 2)
    },
    'LAX': {  # Load A and X
        'ZP': (0xA7, 2), 'ZPY': (0xB7, 2), 'ABS': (0xAF, 3), 'ABSY': (0xBF, 3),
        'INDX': (0xA3, 2), 'INDY': (0xB3, 2)
    },
    'DCP': {  # Decrement then Compare
        'ZP': (0xC7, 2), 'ZPX': (0xD7, 2), 'ABS': (0xCF, 3), 'ABSX': (0xDF, 3),
        'ABSY': (0xDB, 3), 'INDX': (0xC3, 2), 'INDY': (0xD3, 2)
    },
    'ISC': {  # Increment then SBC (also known as ISB)
        'ZP': (0xE7, 2), 'ZPX': (0xF7, 2), 'ABS': (0xEF, 3), 'ABSX': (0xFF, 3),
        'ABSY': (0xFB, 3), 'INDX': (0xE3, 2), 'INDY': (0xF3, 2)
    },
    'ANC': {'IMM': (0x0B, 2)},  # AND with Carry
    'ALR': {'IMM': (0x4B, 2)},  # AND then LSR (also ASR)
    'ASR': {'IMM': (0x4B, 2)},  # Alias for ALR
    'ARR': {'IMM': (0x6B, 2)},  # AND then ROR
    'SBX': {'IMM': (0xCB, 2)},  # Compare X register (also AXS)
    'LXA': {'IMM': (0xAB, 2)},  # Load X and A (unstable)
    'ANE': {'IMM': (0x8B, 2)},  # AND X with immediate (unstable)
    'SHA': {  # Store A AND X AND high byte of address + 1
        'ABSY': (0x9F, 3), 'INDY': (0x93, 2)
    },
    'SHX': {'ABSY': (0x9E, 3)},  # Store X AND high byte of address + 1
    'SHY': {'ABSX': (0x9C, 3)},  # Store Y AND high byte of address + 1
    'TAS': {'ABSY': (0x9B, 3)},  # Transfer A AND X to S, then SHA
    'LAS': {'ABSY': (0xBB, 3)},  # Load A, X, S with memory AND S
    'JAM': {'IMP': (0x02, 1)},   # Halt processor (also KIL, HLT)
    'NOP': {  # Undocumented NOPs with different addressing modes
        'ZP': (0x04, 2), 'ZPX': (0x14, 2), 'ABS': (0x0C, 3), 'ABSX': (0x1C, 3),
        'IMM': (0x80, 2)
    },
    'DOP': {  # Double NOP (ACME compatible)
        'ZP': (0x04, 2), 'ZPX': (0x14, 2), 'IMM': (0x80, 2)
    },
    'TOP': {  # Triple NOP (ACME compatible)
        'ABS': (0x0C, 3), 'ABSX': (0x1C, 3)
    },
}

# W65C02S specific instruction extensions
INSTRUCTIONS_W65C02S = {
    'STZ': {'ZP': (0x64, 2), 'ZPX': (0x74, 2), 'ABS': (0x9C, 3), 'ABSX': (0x9E, 3)},
    'BRA': {'REL': (0x80, 2)},
    'PHX': {'IMP': (0xDA, 1)}, 'PLX': {'IMP': (0xFA, 1)},
    'PHY': {'IMP': (0x5A, 1)}, 'PLY': {'IMP': (0x7A, 1)},
    'TSB': {'ZP': (0x04, 2), 'ABS': (0x0C, 3)},
    'TRB': {'ZP': (0x14, 2), 'ABS': (0x1C, 3)},
    'BBR0': {'ZP_REL': (0x0F, 3)}, 'BBR1': {'ZP_REL': (0x1F, 3)},
    'BBR2': {'ZP_REL': (0x2F, 3)}, 'BBR3': {'ZP_REL': (0x3F, 3)},
    'BBR4': {'ZP_REL': (0x4F, 3)}, 'BBR5': {'ZP_REL': (0x5F, 3)},
    'BBR6': {'ZP_REL': (0x6F, 3)}, 'BBR7': {'ZP_REL': (0x7F, 3)},
    'BBS0': {'ZP_REL': (0x8F, 3)}, 'BBS1': {'ZP_REL': (0x9F, 3)},
    'BBS2': {'ZP_REL': (0xAF, 3)}, 'BBS3': {'ZP_REL': (0xBF, 3)},
    'BBS4': {'ZP_REL': (0xCF, 3)}, 'BBS5': {'ZP_REL': (0xDF, 3)},
    'BBS6': {'ZP_REL': (0xEF, 3)}, 'BBS7': {'ZP_REL': (0xFF, 3)},
    'RMB0': {'ZP': (0x07, 2)}, 'RMB1': {'ZP': (0x17, 2)},
    'RMB2': {'ZP': (0x27, 2)}, 'RMB3': {'ZP': (0x37, 2)},
    'RMB4': {'ZP': (0x47, 2)}, 'RMB5': {'ZP': (0x57, 2)},
    'RMB6': {'ZP': (0x67, 2)}, 'RMB7': {'ZP': (0x77, 2)},
    'SMB0': {'ZP': (0x87, 2)}, 'SMB1': {'ZP': (0x97, 2)},
    'SMB2': {'ZP': (0xA7, 2)}, 'SMB3': {'ZP': (0xB7, 2)},
    'SMB4': {'ZP': (0xC7, 2)}, 'SMB5': {'ZP': (0xD7, 2)},
    'SMB6': {'ZP': (0xE7, 2)}, 'SMB7': {'ZP': (0xF7, 2)},
    'STP': {'IMP': (0xDB, 1)},
    'WAI': {'IMP': (0xCB, 1)},
}
