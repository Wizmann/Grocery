
reserved = {
    'for' : 'FOR',
    'end' : 'END',
    'print': 'PRINT',
    'in': 'IN',
}

tokens = [
    'NAME','NUMBER',
    'PLUS','EQUALS', 'COMMA',
    'NEWLINE',
    ] + list(reserved.values())

t_PLUS    = r'\+'
t_EQUALS  = r'='
t_COMMA   = r','

def t_NAME(t):
    r'[a-zA-Z_][a-zA-Z0-9_]*'
    t.type = reserved.get(t.value, 'NAME')
    return t

def t_NUMBER(t):
    r'\d+'
    try:
        t.value = int(t.value)
    except ValueError:
        print("Integer value too large %d", t.value)
        t.value = 0
    return t

# Ignored characters
t_ignore = " \t"

def t_NEWLINE(t):
    r'\n+'
    t.lexer.lineno += t.value.count("\n")
    return t
    
def t_error(t):
    print("Illegal character '%s'" % t.value[0])
    t.lexer.skip(1)
    
# Build the lexer
import ply.lex as lex
lexer = lex.lex()

def p_statements(t):
    '''
    statements : statement statements
               | statement
    '''
    if len(t) == 2:
        t[0] = [ t[1] ]
    else:
        t[0] = [ t[1] ] + t[2]

def p_statement_empty(t):
    'statement : NEWLINE'
    pass

def p_statement_assign(t):
    'statement : NAME EQUALS expression NEWLINE'
    t[0] = ('assign', t[1], t[3])

def p_expression_binop(t):
    '''
    expression : expression PLUS expression
    '''
    t[0] = ('plus', t[1], t[3])

def p_expression_number(t):
    'expression : NUMBER'
    t[0] = ('number', t[1])

def p_expression_name(t):
    'expression : NAME'
    try:
        t[0] = ('variable', t[1])
    except LookupError:
        print("Undefined name '%s'" % t[1])
        t[0] = 0

def p_for_statement(t):
    '''
    statement : FOR NAME IN expression COMMA expression NEWLINE statements END NEWLINE
    '''
    t[0] = ('for', t[2], t[4], t[6], t[8])

def p_print(t):
    'statement : PRINT expression NEWLINE'
    t[0] = ('print', t[2])

def p_error(t):
    print("Syntax error at '%s'" % t.value)

import ply.yacc as yacc
parser = yacc.yacc()

s = '''
a = 1
b = 1
for i in 1, 10
    c = a + b
    a = b
    b = c
    print a
end
'''

names = {}

def evaluate(expr):
    if expr[0] == 'number':
        return expr[1]
    elif expr[0] == 'variable':
        return names[expr[1]]
    elif expr[0] == 'plus':
        return evaluate(expr[1]) + evaluate(expr[2])
    else:
        assert False

def execute(tree):
    for item in tree:
        if not item:
            continue
        if item[0] == 'assign':
            name = item[1]
            value = evaluate(item[2])
            names[name] = value
        elif item[0] == 'print':
            print evaluate(item[1])
        elif item[0] == 'for':
            name = item[1]
            range_l, range_r = evaluate(item[2]), evaluate(item[3])
            names[name] = range_l
            while names[name] < range_r:
                execute(item[4])
                names[name] += 1
        else:
            assert False

ast = parser.parse(s)
execute(ast)
