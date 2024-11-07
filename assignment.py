from stimpl.expression import *
from stimpl.runtime import *

if __name__=='__main__':
    program = If(BooleanLiteral(True), 
                 Assign(Variable("i"), IntLiteral(7)), 
                 Assign(Variable("j"), IntLiteral(8)))
    \
    
    _,_, state = evaluate(program, State())
    print(f"{state=}")

    program = If(Lt(IntLiteral(5), IntLiteral(10)),
                 Print(StringLiteral("Hello")),
                 Print(StringLiteral("Goodbye")))
    run_stimpl(program)