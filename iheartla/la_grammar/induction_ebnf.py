##!HERE## Define the grammar of a proof by induction. This will be read by tatsu
INDUCTION = r"""
proof_begin
    = 
    'Proof:' ~ {hspace} induction_declaration
    ;
    
induction_declaration::Induction
    =
    'Induction(' over:(n | m) ')' {line}+
    '\tStatement:' {hspace} te
    ;
"""