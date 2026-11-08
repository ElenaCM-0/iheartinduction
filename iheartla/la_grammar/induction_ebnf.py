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
    'Induction(n)' {separator_with_space}+
    'IH:' {separator_with_space}+ ih:ih {separator_with_space}+ 
    'Base:' {hspace} 'n=' basen:integer {separator_with_space}+ basep:chain_equality {separator_with_space}+
    'IS:' {hspace} 'n=>n+' step_size:integer {separator_with_space}+
    proof:chain_equality
    ;

ih::InductionHypothesis
    =
    equality
    ;

chain_equality::ChainEquality
    =
    | lhs:chain_equality {hspace} '=' {hspace} rhs:expression
    | equality
    ;

equality::Equality
    =
    lhs:expression {hspace} '=' {hspace} rhs:expression
    ;

induction_identifier
    =
     $ (induction_word_identifier | induction_variable_identifier)
    ;

induction_variable_identifier::InductionN
    =
     induction_variable:identifier_alone
    ;

induction_word_identifier
    = 'IH-' op:identifier_alone
    ;
# text_with_n::TextN
#     =
#     '$n' textAfter:/[a-zA-Z ]/
#     | textBefore:/[a-zA-Z ]/ '$n'
# 
"""