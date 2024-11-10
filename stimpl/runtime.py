from typing import Any, Tuple, Optional

from stimpl.expression import *
from stimpl.types import *
from stimpl.errors import *

"""
Interpreter State
"""


class State(object):
    def __init__(self, variable_name: str, variable_value: Expr, variable_type: Type, next_state: 'State') -> None:
        self.variable_name = variable_name
        self.value = (variable_value, variable_type)
        self.next_state = next_state

    def copy(self) -> 'State':
        variable_value, variable_type = self.value
        return State(self.variable_name, variable_value, variable_type, self.next_state)

    def set_value(self, variable_name, variable_value, variable_type):
        return State(variable_name, variable_value, variable_type, self)

    def get_value(self, variable_name) -> Any:
        """ TODO: Implement. 
         The get_value method traverses the tuple to find the most recent state of a specified variable.
         """
        current_state = self
        while not isinstance(current_state, EmptyState):
            if current_state.variable_name == variable_name:
                variable_value, variable_type = current_state.value
                return (variable_value, variable_type)
            current_state = current_state.next_state
        return None

    def __repr__(self) -> str:
        return f"{self.variable_name}: {self.value}, " + repr(self.next_state)


class EmptyState(State):
    def __init__(self):
        pass

    def copy(self) -> 'EmptyState':
        return EmptyState()

    def get_value(self, variable_name) -> None:
        return None

    def __repr__(self) -> str:
        return ""


"""
Main evaluation logic!
"""


def evaluate(expression: Expr, state: State) -> Tuple[Optional[Any], Type, State]:
    match expression:
        case Ren():
            return (None, Unit(), state)

        case IntLiteral(literal=l):
            return (l, Integer(), state)

        case FloatingPointLiteral(literal=l):
            return (l, FloatingPoint(), state)

        case StringLiteral(literal=l):
            return (l, String(), state)

        case BooleanLiteral(literal=l):
            return (l, Boolean(), state)

        case Print(to_print=to_print):
            printable_value, printable_type, new_state = evaluate(
                to_print, state)

            match printable_type:
                case Unit():
                    print("Unit")
                case _:
                    print(f"{printable_value}")

            return (printable_value, printable_type, new_state)

        case Sequence(exprs=exprs) | Program(exprs=exprs):
            """ TODO: Implement. 
            The Sequence and Program cases involve evaluating a list of expressions in order. 
            The state is updated as each expression is evaluated.
            """
            current_state = state
            final_value = None
            final_type = Unit()
            for expr in exprs:
                final_value, final_type, current_state = evaluate(expr, current_state)
            return (final_value, final_type, current_state)

        case Variable(variable_name=variable_name):
            value = state.get_value(variable_name)
            if value == None:
                raise InterpSyntaxError(
                    f"Cannot read from {variable_name} before assignment.")
            variable_value, variable_type = value
            return (variable_value, variable_type, state)

        case Assign(variable=variable, value=value):

            value_result, value_type, new_state = evaluate(value, state)

            variable_from_state = new_state.get_value(variable.variable_name)
            _, variable_type = variable_from_state if variable_from_state else (
                None, None)

            if value_type != variable_type and variable_type != None:
                raise InterpTypeError(f"""Mismatched types for Assignment:
            Cannot assign {value_type} to {variable_type}""")

            new_state = new_state.set_value(
                variable.variable_name, value_result, value_type)
            return (value_result, value_type, new_state)

        case Add(left=left, right=right):
            result = 0
            left_result, left_type, new_state = evaluate(left, state)
            right_result, right_type, new_state = evaluate(right, new_state)

            if left_type != right_type:
                raise InterpTypeError(f"""Mismatched types for Add:
            Cannot add {left_type} to {right_type}""")

            match left_type:
                case Integer() | String() | FloatingPoint():
                    result = left_result + right_result
                case _:
                    raise InterpTypeError(f"""Cannot add {left_type}s""")

            return (result, left_type, new_state)

        case Subtract(left=left, right=right):
            """ TODO: Implement. 
            The Subtract case is similar to Add, but it performs subtraction.
            """
            result = 0
            left_result, left_type, new_state = evaluate(left, state)
            right_result, right_type, new_state = evaluate(right, new_state)

            if left_type != right_type:
                raise InterpTypeError(f"""Mismatched types for Subtract:
            Cannot subtract {left_type} from {right_type}""")

            match left_type:
                case Integer() | FloatingPoint():
                    result = left_result - right_result
                case _:
                    raise InterpTypeError(f"""Cannot subtract {left_type}s""")

            return (result, left_type, new_state)

        case Multiply(left=left, right=right):
            """ TODO: Implement. 
            Same case as Add but Multiply no special cases
            """
            result = 0
            left_result, left_type, new_state = evaluate(left, state)
            right_result, right_type, new_state = evaluate(right, new_state)

            if left_type != right_type:
                raise InterpTypeError(f"""Mismatched types for Multiply:
            Cannot multiply {left_type} with {right_type}""")

            match left_type:
                case Integer() | FloatingPoint():
                    result = left_result * right_result
                case _:
                    raise InterpTypeError(f"""Cannot multiply {left_type}s""")

            return (result, left_type, new_state)

        case Divide(left=left, right=right):
            """ TODO: Implement. 
            Same case as Add but Divide needs to check if it is dividing by zero as well.
            """
            left_result, left_type, new_state = evaluate(left, state)
            right_result, right_type, new_state = evaluate(right, new_state)

            if left_type != right_type:
                raise InterpTypeError(f"""Mismatched types for Divide:
            Cannot divide {left_type} by {right_type}""")

            if right_result == 0:
                raise InterpMathError("Division by zero is not allowed")

            result = 0
            match left_type:
                case Integer():
                    result = left_result // right_result
                case FloatingPoint():
                    result = left_result / right_result
                case _:
                    raise InterpTypeError(f"""Cannot divide {left_type}s""")

            return (result, left_type, new_state)

        case And(left=left, right=right):
            left_value, left_type, new_state = evaluate(left, state)
            right_value, right_type, new_state = evaluate(right, new_state)

            if left_type != right_type:
                raise InterpTypeError(f"""Mismatched types for And:
            Cannot evaluate {left_type} and {right_type}""")
            match left_type:
                case Boolean():
                    result = left_value and right_value
                case _:
                    raise InterpTypeError(
                        "Cannot perform logical and on non-boolean operands.")

            return (result, left_type, new_state)

        case Or(left=left, right=right):
            """ TODO: Implement. 
            The OR logic falls the same as AND but with the right accomidations
            """
            left_value, left_type, new_state = evaluate(left, state)
            right_value, right_type, new_state = evaluate(right, new_state)

            if left_type != right_type:
                raise InterpTypeError(f"""Mismatched types for Or:
            Cannot evaluate {left_type} or {right_type}""")
            match left_type:
                case Boolean():
                    result = left_value or right_value
                case _:
                    raise InterpTypeError(
                        "Cannot perform logical or on non-boolean operands.")

            return (result, left_type, new_state)

        case Not(expr=expr):
            """ TODO: Implement. 
            The Not case evaluates the logical negation of a boolean expression as long as it 
            validates its type as a boolean
            """
            value, value_type, new_state = evaluate(expr, state)
    
            if value_type != Boolean():
                raise InterpTypeError("Cannot perform logical not on non-boolean operand.")
            
            result = not value
            return (result, Boolean(), new_state)

        case If(condition=condition, true=true, false=false):
            """ TODO: Implement. 
            The If case evaluates a conditional expression,
             executing one branch if the condition is a boolean 
            """
            condition_value, condition_type, new_state = evaluate(condition, state)
    
            if condition_type != Boolean():
                raise InterpTypeError("Condition in If expression must be a boolean.")
            
            if condition_value:
                return evaluate(true, new_state)
            else:
                return evaluate(false, new_state)

        case Lt(left=left, right=right):
            left_value, left_type, new_state = evaluate(left, state)
            right_value, right_type, new_state = evaluate(right, new_state)

            result = None

            if left_type != right_type:
                raise InterpTypeError(f"""Mismatched types for Lt:
            Cannot compare {left_type} and {right_type}""")

            match left_type:
                case Integer() | Boolean() | String() | FloatingPoint():
                    result = left_value < right_value
                case Unit():
                    result = False
                case _:
                    raise InterpTypeError(
                        f"Cannot perform < on {left_type} type.")

            return (result, Boolean(), new_state)

        case Lte(left=left, right=right):
            """ TODO: Implement. 
            Same thing as the Lessthan or equal to function but I need to 
            check if the right side is also a Unit() for the accomidation of 
            """
            
            left_value, left_type, new_state = evaluate(left, state)
            right_value, right_type, new_state = evaluate(right, new_state)

            result = None

            if left_type != right_type:
                raise InterpTypeError(f"""Mismatched types for Lte:
            Cannot compare {left_type} and {right_type}""")

            match left_type:
                case Integer() | Boolean() | String() | FloatingPoint():
                    result = left_value <= right_value
                case Unit():
                    match right_type:
                        case Unit():
                            result = True
                        case _:
                            result = False
                case _:
                    raise InterpTypeError(
                        f"Cannot perform <= on {left_type} type.")

            return (result, Boolean(), new_state)

        case Gt(left=left, right=right):
            """ TODO: Implement.
            Same thing as the Lt section but greater than instead 
            """
            
            left_value, left_type, new_state = evaluate(left, state)
            right_value, right_type, new_state = evaluate(right, new_state)

            result = None

            if left_type != right_type:
                raise InterpTypeError(f"""Mismatched types for Gt:
            Cannot compare {left_type} and {right_type}""")

            match left_type:
                case Integer() | Boolean() | String() | FloatingPoint():
                    result = left_value > right_value
                case Unit():
                    result = False
                case _:
                    raise InterpTypeError(
                        f"Cannot perform > on {left_type} type.")

            return (result, Boolean(), new_state)

        case Gte(left=left, right=right):
            """ TODO: Implement. 
            Greater than Equal: should be same as Gt but with the accomidations on the right side as well
            """
            
            left_value, left_type, new_state = evaluate(left, state)
            right_value, right_type, new_state = evaluate(right, new_state)

            result = None

            if left_type != right_type:
                raise InterpTypeError(f"""Mismatched types for Gte:
            Cannot compare {left_type} and {right_type}""")

            match left_type:
                case Integer() | Boolean() | String() | FloatingPoint():
                    result = left_value >= right_value
                case Unit():
                    match right_type:
                        case Unit():
                            result = True
                        case _:
                            result = False
                case _:
                    raise InterpTypeError(
                        f"Cannot perform >= on {left_type} type.")

            return (result, Boolean(), new_state)

        case Eq(left=left, right=right):
            """ TODO: Implement. 
            Equal: needs to check if right and left side types are units and if 
            they are then the result should be true
            """
            
            left_value, left_type, new_state = evaluate(left, state)
            right_value, right_type, new_state = evaluate(right, new_state)

            result = None

            if left_type != right_type:
                raise InterpTypeError(f"""Mismatched types for Eq:
            Cannot compare {left_type} and {right_type}""")

            match left_type:
                case Integer() | Boolean() | String() | FloatingPoint():
                    result = left_value == right_value
                case Unit():
                    match right_type:
                        case Unit():
                            result = True
                        case _:
                            result = False
                case _:
                    raise InterpTypeError(
                        f"Cannot perform == on {left_type} type.")

            return (result, Boolean(), new_state)

        case Ne(left=left, right=right):
            """ TODO: Implement. 
            Not Equal: same gist as Equal but negated instead
            """
            
            left_value, left_type, new_state = evaluate(left, state)
            right_value, right_type, new_state = evaluate(right, new_state)

            if left_type != right_type:
                raise InterpTypeError(f"""Mismatched types for Ne:
                Cannot compare {left_type} and {right_type}""")

            result = None

            match left_type:
                case Integer() | Boolean() | String() | FloatingPoint():
                    result = left_value != right_value
                case Unit():
                    result = False  # Both are Unit, hence they are not different.
                case _:
                    raise InterpTypeError(
                        f"Cannot perform != on {left_type} type.")

            return (result, Boolean(), new_state)

        case While(condition=condition, body=body):
            """ TODO: Implement. 
            The basic idea behind the While function is that it continuously checks the condition, and if the condition is True,
              it runs the body of the loop again and again. Once the condition evaluates to False
            """
            while True:
                condition_value, condition_type, new_state = evaluate(condition, state)
                
                if condition_type != Boolean():
                    raise InterpTypeError("Condition in While expression must be a boolean.")
                
                if not condition_value:
                    return (False, Boolean(), new_state)
                
                _, _, new_state = evaluate(body, new_state)
                
                state = new_state


def run_stimpl(program, debug=False):
    state = EmptyState()
    program_value, program_type, program_state = evaluate(program, state)

    if debug:
        print(f"program: {program}")
        print(f"final_value: ({program_value}, {program_type})")
        print(f"final_state: {program_state}")

    return program_value, program_type, program_state
