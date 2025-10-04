# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- GitHub Actions CI/CD workflow
- Comprehensive test suite with ACME compatibility testing
- Enhanced error reporting with source line display
- Complete ACME directive support
- Multiple CPU support (6502, 65C02, NMOS6502, W65C02S)
- Advanced expression system with mathematical functions
- Macro system with parameter substitution
- Conditional assembly with nested support
- Loop structures (!for, !while, !do)
- File inclusion with recursive processing
- Text conversion and encoding support
- Segment management and debug system
- Multiple output formats (binary, CBM, Intel HEX)
- VICE debugger integration

### Changed
- Improved modular architecture
- Enhanced symbol management with zone system
- Better error handling and recovery

### Fixed
- All known ACME compatibility issues
- Symbol resolution for forward references
- Expression evaluation edge cases

## [1.0.0] - 2025-10-04

### Added
- Initial release of pyasm6502
- Complete ACME compatibility (100% test coverage)
- Production-ready assembler with enhanced error reporting
- Comprehensive documentation and examples
- Full 6502 family processor support
- Advanced features including macros, conditionals, and loops
- Professional GitHub repository setup with CI/CD

### Technical Achievements
- **Compatibility**: 100% ACME compatibility achieved (215/215 tests passing)
- **Test Success Rate**: All test suites passing
- **Expression Engine**: Complete mathematical function support
- **Error Handling**: Enhanced diagnostic reporting with source line display
- **Code Quality**: Modular, maintainable architecture

### Repository Setup
- MIT License
- Comprehensive README.md
- Contributing guidelines
- Issue and pull request templates
- GitHub Actions workflow for CI/CD
- Proper Python packaging with pyproject.toml
- Complete .gitignore for Python projects

---

## Development Phases

### Phase 1: Core Functionality
- Basic 6502 instruction set support
- Two-pass assembly with symbol resolution
- Output generation (binary, CBM, HEX formats)

### Phase 2: Advanced Expression System
- Mathematical operations and functions
- Variable system with !set directive
- Operator precedence and associativity

### Phase 3: Control Structures
- Conditional assembly (!if/!else/!fi)
- Loop structures (!for, !while, !do)
- Macro system with parameter substitution

### Phase 4: File System Integration
- File inclusion with !source/!src
- Recursive processing and search paths
- Text processing and encoding

### Phase 5: Advanced Features
- Segment management (!pseudopc/!realpc)
- Debug system with VICE integration
- Enhanced error reporting

### Phase 6: Production Readiness
- Complete ACME compatibility testing
- Enhanced error reporting with source line display
- Professional repository setup
- Comprehensive documentation

## Contributing

Please see [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines on contributing to this project.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
