##!HERE## Define the grammar of a proof by induction. This will be read by tatsu
INDUCTION = r"""
proof_begin
    = 
    PROOF ':' ~ {hspace} induction_declaration
    ;

# 'Induction(' over:(n | m) ')' {line}+
#     '\tStatement:' {hspace} te
induction_declaration::Induction
    =
    'Induction(n)' {line}+ '\t'
    'IH:' {line}+ '\t\t' ih:ih {line}+ '\t'
    'Base:' {hspace} 'n=' basen:integer {line}+ '\t\t' ih:ih {line}+ '\t'
    'IS:' {hspace} 'n=>n+' step_size:integer {line}+ '\t\t' 
    proof:equality
    ;

ih::InductionHypothesis
    =
    lhs:arithmetic_expression {hspace} '=' {hspace} rhs:arithmetic_expression
    ;

equality::Equality
    =
    lhs:arithmetic_expression {hspace} '=' {hspace} rhs:arithmetic_expression
    | lhs:arithmetic_expression {hspace} '=' {hspace} rhs:equality
    ;

# text_with_n::TextN
#     =
#     '$n' textAfter:/[a-zA-Z ]/
#     | textBefore:/[a-zA-Z ]/ '$n'
# 
"""