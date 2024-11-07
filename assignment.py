from stimpl.expression import *
from stimpl.runtime import *

if __name__=='__main__':
    program = If(BooleanLiteral(True), 
                 Assign(Variable("i"), IntLiteral(7)), 
                 Assign(Variable("j"), IntLiteral(8))) 
    _,_, state = evaluate(program, State())
    run_stimpl(f"{state=}")

