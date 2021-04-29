import ply.lex as lex
import ply.yacc as yacc
import math

class Lexer:
    def __init__(self):
        self.lexer = lex.lex(module=self)
        self.parser = yacc.yacc(module=self)
    tokens = [
    
        'INT',
        'FLOAT',
        'PLUS',
        'MINUS',
        'DIVIDE',
        'MULTIPLY',
        'ROOT',
        'POWER',
        'SB_OPEN',
        'SB_CLOSE',
        'MB_OPEN',
        'MB_CLOSE',
        'BB_OPEN',
        'BB_CLOSE',
        'POWERS',
        'CONSTANTS',
        'FUNCTIONS'
    
    ]
    precedence = (
    
        ('left', 'PLUS', 'MINUS'),
        ('left', 'MULTIPLY', 'DIVIDE'),
        ('left', 'POWER','POWERS', 'ROOT'),
        ('left', 'SB_OPEN', 'SB_CLOSE', 'MB_OPEN', 'MB_CLOSE', 'BB_OPEN', 'BB_CLOSE'),
        ('left', 'CONSTANTS', 'FUNCTIONS')
    
    )
    CONSTANTS= {
            "π": math.pi,
            "é": math.e
    }
    FUNCTIONS= {
    
            "sinh": math.sinh,
            "cosh": math.cosh,
            "tanh": math.tanh,
            "sin": math.sin,
            "cos": math.cos,
            "tan": math.tan,
            "log": math.log
            
    }
    powers = {
            '¹':1, '²':2, '³':3,
            '⁴':4, '⁵':5, '⁶':6,
            '⁷':7, '⁸':8, '⁹':9,
                    '⁰':0
    }
    
    t_PLUS = r'\+'
    t_MINUS = r'\-'
    t_MULTIPLY = r'\*'
    t_DIVIDE = r'\/'
    t_ignore = r' '
    t_ROOT =r'\√'
    t_POWER=r'\^'
    t_POWERS= r'|'.join(fr'{C}' for C in powers.keys())
    t_SB_OPEN=r'\('
    t_SB_CLOSE=r'\)'
    t_MB_OPEN=r'\{'
    t_MB_CLOSE=r'\}'
    t_BB_OPEN=r'\['
    t_BB_CLOSE=r'\]'
    t_CONSTANTS=r'|'.join(fr'{C}' for C in CONSTANTS.keys())
    t_FUNCTIONS = r'|'.join(fr'{C}' for C in FUNCTIONS.keys())
    def t_FLOAT(self, t):
        r'\d+\.\d+'
        t.value = float(t.value)
        return t
    
    def t_INT(self, t):
        r'\d+'
        t.value = int(t.value)
        return t
    
    def t_error(self, t):
        t.lexer.skip(1)
        raise ValueError("Illegal characters!")

    def p_calc(self, p):
        '''
        calc : expression
             | empty
        '''
        a=self.run(p[1])
        if a is None:
            pass
        elif int(a)==a:
            p[0]= int(a)
        else:
            p[0]=a
            
    def p_expression(self, p):
        '''
        expression : expression POWER expression
                   | expression MULTIPLY expression
                   | expression DIVIDE expression
                   | expression PLUS expression
                   | expression MINUS expression
        '''

        p[0] = (p[2], p[1], p[3])
    
    def p_expression_short(self, p):
        '''
        expression : MINUS expression
                   | ROOT expression
        '''
        p[0]=(p[1], p[2])
    
    def p_expression_powers(self, p):
        '''
        expression : expression POWERS
        '''
        p[0]= ("^", p[1], self.powers[p[2]])
    
    def p_expression_brackets(self, p):
        '''
        expression : SB_OPEN expression SB_CLOSE expression
                   | SB_OPEN expression SB_CLOSE
                   | expression SB_OPEN expression SB_CLOSE
                   | MB_OPEN expression MB_CLOSE expression
                   | MB_OPEN expression MB_CLOSE
                   | expression MB_OPEN expression MB_CLOSE
                   | BB_OPEN expression BB_CLOSE expression
                   | BB_OPEN expression BB_CLOSE
                   | expression BB_OPEN expression BB_CLOSE
        '''
        if p[1] in ("(", "{", "["):
            if len(p)==5:
                p[0]=("*", p[4], (p[2], p[1], p[3]))
            elif len(p)==4:
                p[0]=(p[2], p[1], p[3])
        if p[2] in ("(", "{", "["):
            p[0]=("*", p[1], (p[3], p[2], p[4]))
            
    def p_expression_int_float(self, p):
        '''
        expression : INT
                   | FLOAT
        '''
        p[0] = p[1]
        
    def p_expression_constants(self, p):
        '''
        expression : CONSTANTS
                   | expression CONSTANTS
        '''
        if p[1] in self.CONSTANTS.keys():
            p[0]=self.CONSTANTS[p[1]]
        elif p[2] in self.CONSTANTS.keys():
            p[0]=("*", p[1], self.CONSTANTS[p[2]])
            
    def p_expression_functions(self, p):
        '''
        expression : FUNCTIONS expression
                   | FUNCTIONS POWERS expression
        '''
        if len(p)==4:
            p[0]=("^", (p[1], p[3]), self.powers[p[2]])
        if len(p)==3:
            p[0]=(p[1], p[2])
    
    
    def p_error(self, p):
        raise SyntaxError("Syntax error found!")
    
    def p_empty(self, p):
        '''
        empty :
        '''
        p[0] = None
    

    def run(self, p):
        if type(p) == tuple:
            if p[0] == '+':
                return self.run(p[1]) + self.run(p[2])
            elif p[0] == '-':
                if len(p)==3:
                    return self.run(p[1]) - self.run(p[2])
                elif len(p)==2:
                    return -(self.run(p[1]))
            elif p[0] == '*':
                return self.run(p[1]) * self.run(p[2])
            elif p[0] == '/':
                return self.run(p[1]) / self.run(p[2])
            elif p[0] == '^':
                return self.run(p[1]) ** self.run(p[2])
            elif p[0] == '√':
                return math.sqrt(self.run(p[1]))
            elif p[1] in ('(', '{', '['):
                return self.run(p[0])
            elif p[0] in self.FUNCTIONS.keys():
                if p[0] in ["sin", "cos", "tan"]:
                    return self.FUNCTIONS[p[0]](self.run(p[1])*math.pi/180)
                return self.FUNCTIONS[p[0]](self.run(p[1]))
        else:
            return p
    def parse(self, p):
        return self.parser.parse(p)
        

if __name__=="__main__":
    lexer = Lexer()
    try:
        print(lexer.parse(input(">> ")))
    except:
        print("Error")