# pyasm6502 Version History

## build 20250928

### Enhanced Error Reporting
- **NEW**: Enhanced error display functionality
  - Error messages now show the actual source code line that caused the error
  - Added visual indicators (carets) to highlight problem lines
  - Improved error context with filename, line number, and line text
- **IMPROVED**: `AssemblerError` class enhanced with better formatting
- **ADDED**: Helper methods `_get_current_line_text()` and `_raise_error()` for consistent error reporting
- **UPDATED**: Error handling throughout assembler core to use enhanced reporting

### Technical Improvements
- **REFACTORED**: Error raising locations updated to use new helper methods
- **ENHANCED**: Error messages provide better debugging context
- **IMPROVED**: User experience with clearer error identification

### Documentation
- **UPDATED**: README.md for GitHub publication
  - Removed project-specific references
  - Added enhanced error reporting examples
  - Updated for general 6502 development use
- **ADDED**: Version history documentation (this file)

---

## build 20250924

### Production Release - 100% ACME Compatibility
- **ACHIEVEMENT**: 100% ACME compatibility achieved (215/215 tests passing)
- **COMPLETE**: Full W65C02S instruction set support
- **COMPLETE**: All ACME directives implemented and tested

### Core Features (Stable)
- **Two-pass assembly**: Complete symbol resolution with forward references
- **Symbol management**: Global, local (.), cheap local (@), and anonymous (+/-) labels
- **Zone system**: Local symbol scoping with `!zone` directive
- **Expression engine**: Complete mathematical operations and functions
- **Output formats**: Plain binary, CBM (with load address), Intel HEX

### ACME Compatibility Features (Complete)
- **Conditional assembly**: `!if`/`!else`/`!fi`, `!ifdef`/`!ifndef` with nested support
- **Loop structures**: `!for`, `!while`, `!do` constructs with safety controls
- **Macro system**: `!macro` definition and `+macro` invocation with parameter substitution
- **File inclusion**: `!source`/`!src` with recursive processing and search paths
- **Text processing**: `!convtab`/`!ct`, `!scr`, `!scrxor` with built-in encoding tables
- **Segment management**: `!pseudopc`/`!realpc`, `!initmem`, `!xor`
- **Debug system**: `!warn`/`!error`/`!serious`, `!symbollist`, VICE debugger integration

### Advanced Features (Complete)
- **Data directives**: `!byte`, `!word`, `!8`/`!16`/`!24`/`!32`, endian-specific variants
- **Mathematical functions**: Complete set including trigonometric functions
- **Variable system**: `!set` directive for variable assignment
- **CPU variants**: 6502, 65C02, NMOS6502, W65C02S support

---

## build 20250920

### Advanced Features Implementation
- **ADDED**: Debug system with `!warn`, `!error`, `!serious` directives
- **ADDED**: VICE debugger integration with `--vicelabels` option
- **ADDED**: Symbol table export functionality
- **IMPLEMENTED**: Segment management with `!pseudopc`/`!realpc`
- **ADDED**: Memory initialization with `!initmem`
- **ADDED**: XOR encoding with `!xor` directive

### Testing and Validation
- **ADDED**: Comprehensive test suites based on ACME test cases
- **TESTED**: Mathematical expression engine (215 test cases)
- **VERIFIED**: W65C02S instruction set compatibility
- **VALIDATED**: Error detection and handling

---

## build 20250918

### File System and Text Processing
- **IMPLEMENTED**: File inclusion system with `!source`/`!src`
- **ADDED**: Include path management with `-I` option
- **IMPLEMENTED**: Text conversion system with `!convtab`/`!ct`
- **ADDED**: Screen code conversion with `!scr`, `!scrxor`
- **ADDED**: Built-in encoding tables (PETSCII, etc.)

### Advanced Data Handling
- **ADDED**: Hexadecimal data input with `!hex` directive
- **IMPLEMENTED**: Memory alignment with `!align`
- **ADDED**: Memory skip with `!skip` directive
- **ENHANCED**: Endian-specific data directives

---

## build 20250915

### Control Structures
- **IMPLEMENTED**: Conditional assembly (`!if`, `!else`, `!fi`)
- **ADDED**: Conditional variants (`!ifdef`, `!ifndef`)
- **IMPLEMENTED**: Loop structures (`!for`, `!while`, `!do`)
- **ADDED**: Loop safety controls and nesting limits
- **IMPLEMENTED**: Macro system with `!macro` and `+macro`
- **ADDED**: Parameter substitution in macros

### Expression System Enhancement
- **ADDED**: Variable system with `!set` directive
- **IMPLEMENTED**: Complex expression evaluation
- **ADDED**: Comparison operators (`<`, `>`, `<=`, `>=`, `==`, `!=`, `<>`)
- **ADDED**: Logical operators (`&`, `|`, `^`, `~`)

---

## build 20250912

### Advanced Expression Engine
- **IMPLEMENTED**: Mathematical functions (sin, cos, tan, etc.)
- **ADDED**: Arithmetic functions (int, float, abs, etc.)
- **IMPLEMENTED**: String and list functions (len, is_string, is_list, etc.)
- **ADDED**: Operator precedence engine
- **IMPLEMENTED**: Power operator (`**`)
- **ADDED**: Complex expression parsing with parentheses

### Data Directives
- **ADDED**: Extended data directives (`!8`, `!16`, `!24`, `!32`)
- **IMPLEMENTED**: Endian-specific variants (`!le16`, `!be16`, etc.)
- **ADDED**: Multi-value data input support
- **ENHANCED**: Expression evaluation in data directives

---

## build 20250910

### Core Assembly Engine
- **INITIAL**: Two-pass assembler implementation
- **ADDED**: W65C02S instruction set support
- **IMPLEMENTED**: All addressing modes (IMP, IMM, ZP, ABS, REL, etc.)
- **ADDED**: Symbol management (global, local, cheap local, anonymous)
- **IMPLEMENTED**: Zone system for local symbol scoping

### Basic Directives
- **ADDED**: Origin directive (`*=` and `.org`)
- **IMPLEMENTED**: Basic data directives (`!byte`, `!word`)
- **ADDED**: Symbol assignment (`=` operator)
- **IMPLEMENTED**: CPU selection (`!cpu` directive)

### Output System
- **IMPLEMENTED**: Plain binary output
- **ADDED**: CBM format with load address
- **ADDED**: Intel HEX format support
- **IMPLEMENTED**: Command-line interface

### Foundation
- **CREATED**: Modular architecture with separate packages
- **IMPLEMENTED**: Tokenizer and lexical analyzer
- **ADDED**: Basic error handling
- **CREATED**: Test framework structure

---

## Development Notes

### Version Numbering
- Format: `build YYYYMMDD`
- Based on significant development milestones
- Each build represents a stable, tested state

### Compatibility
- 100% ACME compatibility achieved in build 20240924
- All 215 mathematical expression tests passing
- Complete W65C02S instruction set support
- Full ACME directive compatibility

### Future Development
- Continued maintenance and bug fixes
- Performance optimizations
- Additional CPU variant support as needed
- Enhanced debugging features