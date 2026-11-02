##!HERE## Define the grammar of a proof by induction. This will be read by tatsu
INDUCTION = r"""
proof_begin
    = 
    'Proof:' ~ {hspace} induction_declaration
    ;

# 'Induction(' over:(n | m) ')' {line}+
#     '\tStatement:' {hspace} te
induction_declaration::Induction
    =
    'Induction(n)' {line}+
    'IH:' {line}+ '\t' ih:ih {line}+
    'Base:' {hspace} 'n=' basen:integer {line}+ '\t' ih:ih {line}+
    'IS:' {hspace} 'n=>n+' step_size:integer {line}+ '\t' 
    proof:equality
    ;

ih::InductionHypothesis
    =
    lhs:arithmetic_expression {hspace} = {hspace} rhs:arithmetic_expression
    ;

equality::Equality
    =
    lhs: lhs:arithmetic_expression {hspace} = {hspace} rhs:arithmetic_expression
    | lhs: lhs:arithmetic_expression {hspace} = {hspace} rhs:equality

# text_with_n::TextN
#     =
#     '$n' textAfter:/[a-zA-Z ]/
#     | textBefore:/[a-zA-Z ]/ '$n'
# 
"""