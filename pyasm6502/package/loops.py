"""
Loop Processing for pyasm6502
Handles !for, !while, !do, !set loop and variable assignment directives.
"""

from typing import List, Dict, Any, Optional, Tuple, Union
from .datastructures import AssemblerError, Token
from .evaluator import evaluate_expression
from .tokenizer import tokenize

# Forward declaration for type hinting
class Assembler6502:
    pass

class LoopVariable:
    """Represents a loop variable with its current value."""
    def __init__(self, name: str, value: Any):
        self.name = name
        self.value = value

class ForLoop:
    """Represents a !for loop block."""
    def __init__(self, variable: str, start: int, end: int, step: int, start_line: int):
        self.variable = variable
        self.start = start
        self.end = end
        self.step = step
        self.current_value = start
        self.start_line = start_line
        self.body_lines: List[str] = []
        self.is_iterable = False
        self.iterable_data: Optional[Union[str, List]] = None

class WhileLoop:
    """Represents a !while loop block."""
    def __init__(self, condition_tokens: List[Token], start_line: int):
        self.condition_tokens = condition_tokens
        self.start_line = start_line
        self.body_lines: List[str] = []

class DoLoop:
    """Represents a !do loop block."""
    def __init__(self, start_line: int):
        self.start_line = start_line
        self.body_lines: List[str] = []
        self.condition_tokens: Optional[List[Token]] = None
        self.loop_type: Optional[str] = None  # 'while' or 'until'

class LoopProcessor:
    """Handles loop processing and variable assignment."""

    def __init__(self):
        self.variables: Dict[str, Any] = {}  # !set variables
        self.for_loops: List[ForLoop] = []  # Stack of nested for loops
        self.while_loops: List[WhileLoop] = []  # Stack of nested while loops
        self.do_loops: List[DoLoop] = []  # Stack of nested do loops
        self.current_loop_depth = 0
        self.max_iterations = 1000  # Safety limit to prevent infinite loops

    def set_variable(self, name: str, value: Any) -> None:
        """Set a variable value (!set directive)."""
        self.variables[name] = value

    def get_variable(self, name: str) -> Any:
        """Get a variable value."""
        return self.variables.get(name, 0)

    def is_in_loop(self) -> bool:
        """Check if we're currently inside any loop."""
        return (len(self.for_loops) > 0 or
                len(self.while_loops) > 0 or
                len(self.do_loops) > 0)

    def process_set_directive(self, asm: 'Assembler6502', tokens: List[Token], start: int) -> None:
        """Process !set directive for variable assignment."""
        if start >= len(tokens) or tokens[start].type != 'IDENTIFIER':
            raise AssemblerError("!set requires a variable name", asm.current_line)

        var_name = tokens[start].value

        if start + 1 >= len(tokens) or tokens[start + 1].type != 'EQUALS':
            raise AssemblerError("!set requires '=' after variable name", asm.current_line)

        # Evaluate the expression
        value, _ = evaluate_expression(asm, tokens, start + 2)
        self.set_variable(var_name, value)

    def process_for_directive(self, asm: 'Assembler6502', tokens: List[Token], start: int) -> ForLoop:
        """
        Process !for directive.
        Supports both traditional syntax: !for var, start, end [, step]
        And iterable syntax: !for var in iterable
        """
        if start >= len(tokens) or tokens[start].type != 'IDENTIFIER':
            raise AssemblerError("!for requires a variable name", asm.current_line)

        var_name = tokens[start].value

        # Check for iterable syntax (!for var in iterable)
        if (start + 1 < len(tokens) and
            tokens[start + 1].type == 'IDENTIFIER' and
            tokens[start + 1].value.lower() == 'in'):

            # Iterable syntax
            if start + 2 >= len(tokens):
                raise AssemblerError("!for in requires iterable", asm.current_line)

            # Handle string literals as iterables
            if tokens[start + 2].type == 'STRING':
                iterable_str = tokens[start + 2].value[1:-1]  # Remove quotes
                for_loop = ForLoop(var_name, 0, len(iterable_str) - 1, 1, asm.current_line)
                for_loop.is_iterable = True
                for_loop.iterable_data = iterable_str

            # Handle identifiers as iterables (assume they're strings or lists)
            elif tokens[start + 2].type == 'IDENTIFIER':
                iterable_name = tokens[start + 2].value
                # Try to get the value from variables or symbols
                iterable_value = self.get_variable(iterable_name)
                if isinstance(iterable_value, (str, list)):
                    for_loop = ForLoop(var_name, 0, len(iterable_value) - 1, 1, asm.current_line)
                    for_loop.is_iterable = True
                    for_loop.iterable_data = iterable_value
                else:
                    raise AssemblerError(f"Variable '{iterable_name}' is not iterable", asm.current_line)
            else:
                raise AssemblerError("!for in requires string or identifier", asm.current_line)

        else:
            # Traditional syntax (!for var, start, end [, step])
            if start + 1 >= len(tokens) or tokens[start + 1].type != 'COMMA':
                raise AssemblerError("!for requires ',' after variable name", asm.current_line)

            # Get start value
            start_value, consumed = evaluate_expression(asm, tokens, start + 2)
            token_pos = start + 2 + consumed

            if token_pos >= len(tokens) or tokens[token_pos].type != 'COMMA':
                raise AssemblerError("!for requires ',' after start value", asm.current_line)

            token_pos += 1

            # Get end value
            end_value, consumed = evaluate_expression(asm, tokens, token_pos)
            token_pos += consumed

            # Get step value (optional, default is 1)
            step_value = 1
            if token_pos < len(tokens) and tokens[token_pos].type == 'COMMA':
                token_pos += 1
                step_value, _ = evaluate_expression(asm, tokens, token_pos)

            for_loop = ForLoop(var_name, int(start_value), int(end_value), int(step_value), asm.current_line)

        self.for_loops.append(for_loop)
        return for_loop

    def process_while_directive(self, asm: 'Assembler6502', tokens: List[Token], start: int) -> WhileLoop:
        """Process !while directive."""
        if start >= len(tokens):
            raise AssemblerError("!while requires a condition", asm.current_line)

        # Store the condition tokens for later evaluation
        condition_tokens = tokens[start:]
        while_loop = WhileLoop(condition_tokens, asm.current_line)
        self.while_loops.append(while_loop)
        return while_loop

    def process_do_directive(self, asm: 'Assembler6502') -> DoLoop:
        """Process !do directive (start of do-while/do-until loop)."""
        do_loop = DoLoop(asm.current_line)
        self.do_loops.append(do_loop)
        return do_loop

    def process_until_directive(self, asm: 'Assembler6502', tokens: List[Token], start: int) -> None:
        """Process !until directive (end of do-until loop)."""
        if not self.do_loops:
            raise AssemblerError("!until without matching !do", asm.current_line)

        if start >= len(tokens):
            raise AssemblerError("!until requires a condition", asm.current_line)

        current_loop = self.do_loops[-1]
        current_loop.condition_tokens = tokens[start:]
        current_loop.loop_type = 'until'

        # Execute the loop
        self._execute_do_loop(asm, current_loop)
        self.do_loops.pop()

    def process_while_end_directive(self, asm: 'Assembler6502', tokens: List[Token], start: int) -> None:
        """Process !while at the end of a do-while loop."""
        if not self.do_loops:
            raise AssemblerError("!while without matching !do", asm.current_line)

        if start >= len(tokens):
            raise AssemblerError("!while requires a condition", asm.current_line)

        current_loop = self.do_loops[-1]
        current_loop.condition_tokens = tokens[start:]
        current_loop.loop_type = 'while'

        # Execute the loop
        self._execute_do_loop(asm, current_loop)
        self.do_loops.pop()

    def process_od_directive(self, asm: 'Assembler6502') -> None:
        """Process !od directive (end of for/while loop)."""
        if self.for_loops:
            current_loop = self.for_loops[-1]
            self._execute_for_loop(asm, current_loop)
            self.for_loops.pop()
        elif self.while_loops:
            current_loop = self.while_loops[-1]
            self._execute_while_loop(asm, current_loop)
            self.while_loops.pop()
        else:
            raise AssemblerError("!od without matching !for or !while", asm.current_line)

    def _execute_for_loop(self, asm: 'Assembler6502', for_loop: ForLoop) -> None:
        """Execute a for loop by repeating its body."""
        iteration_count = 0

        if for_loop.is_iterable:
            # Iterable-based loop
            for i, item in enumerate(for_loop.iterable_data):
                if iteration_count >= self.max_iterations:
                    raise AssemblerError("Loop exceeded maximum iterations (safety limit)", asm.current_line)

                # Set loop variable to current item
                if isinstance(item, str):
                    self.set_variable(for_loop.variable, ord(item))
                else:
                    self.set_variable(for_loop.variable, item)

                # Execute loop body
                self._execute_loop_body(asm, for_loop.body_lines)
                iteration_count += 1

        else:
            # Traditional numeric loop
            current = for_loop.start
            while ((for_loop.step > 0 and current <= for_loop.end) or
                   (for_loop.step < 0 and current >= for_loop.end)):

                if iteration_count >= self.max_iterations:
                    raise AssemblerError("Loop exceeded maximum iterations (safety limit)", asm.current_line)

                # Set loop variable to current value
                self.set_variable(for_loop.variable, current)

                # Execute loop body
                self._execute_loop_body(asm, for_loop.body_lines)

                current += for_loop.step
                iteration_count += 1

    def _execute_while_loop(self, asm: 'Assembler6502', while_loop: WhileLoop) -> None:
        """Execute a while loop by repeating its body while condition is true."""
        iteration_count = 0

        while True:
            if iteration_count >= self.max_iterations:
                raise AssemblerError("Loop exceeded maximum iterations (safety limit)", asm.current_line)

            # Evaluate condition
            condition_value, _ = evaluate_expression(asm, while_loop.condition_tokens, 0)
            if not bool(condition_value):
                break

            # Execute loop body
            self._execute_loop_body(asm, while_loop.body_lines)
            iteration_count += 1

    def _execute_do_loop(self, asm: 'Assembler6502', do_loop: DoLoop) -> None:
        """Execute a do-while/do-until loop."""
        iteration_count = 0

        while True:
            if iteration_count >= self.max_iterations:
                raise AssemblerError("Loop exceeded maximum iterations (safety limit)", asm.current_line)

            # Execute loop body
            self._execute_loop_body(asm, do_loop.body_lines)
            iteration_count += 1

            # Evaluate condition
            condition_value, _ = evaluate_expression(asm, do_loop.condition_tokens, 0)

            if do_loop.loop_type == 'while':
                # Continue while condition is true
                if not bool(condition_value):
                    break
            elif do_loop.loop_type == 'until':
                # Continue until condition is true
                if bool(condition_value):
                    break

    def _execute_loop_body(self, asm: 'Assembler6502', body_lines: List[str]) -> None:
        """Execute the lines in a loop body."""
        saved_line = asm.current_line

        try:
            for line in body_lines:
                tokens = tokenize(line, saved_line, asm.INSTRUCTIONS)
                asm.process_line(tokens)
        except AssemblerError as e:
            # Re-raise with proper line context
            raise e
        finally:
            asm.current_line = saved_line

    def is_loop_start(self) -> bool:
        """Check if we're at the start of a new loop."""
        return len(self.for_loops) > 0 or len(self.while_loops) > 0 or len(self.do_loops) > 0

    def get_current_loop_variable_value(self, name: str) -> Any:
        """Get the current value of a loop variable (for loops)."""
        # Check for loop variables from active for loops
        for for_loop in reversed(self.for_loops):
            if for_loop.variable == name:
                if for_loop.is_iterable:
                    if isinstance(for_loop.iterable_data, str):
                        return ord(for_loop.iterable_data[for_loop.current_value])
                    else:
                        return for_loop.iterable_data[for_loop.current_value]
                else:
                    return for_loop.current_value

        # Check !set variables
        return self.get_variable(name)

    def reset(self) -> None:
        """Reset the loop processor state (for new assembly passes)."""
        self.variables.clear()
        self.for_loops.clear()
        self.while_loops.clear()
        self.do_loops.clear()
        self.current_loop_depth = 0