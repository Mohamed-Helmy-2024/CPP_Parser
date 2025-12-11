class Token:
    def __init__(self, token_type, value):
        self.type = token_type
        self.value = value
    
    def __repr__(self):
        return f"Token({self.type}, {self.value})"

def read_tokens_from_file(filename):
    tokens = []
    
    with open(filename, 'r') as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            
            if line.startswith('<') and line.endswith('>'):
                content = line[1:-1]
                parts = content.split(',', 1)
                
                if len(parts) == 2:
                    token_type = parts[0].strip()
                    value = parts[1].strip()
                    tokens.append(Token(token_type, value))
    
    return tokens

class Parser:
    def __init__(self, tokens):
        self.tokens = tokens
        self.pos = 0
        self.errors = []
        self.has_main = False
    
    def current_token(self):
        if self.pos < len(self.tokens):
            return self.tokens[self.pos]
        return None
    
    def peek_token(self, offset=1):
        if self.pos + offset < len(self.tokens):
            return self.tokens[self.pos + offset]
        return None
    
    def consume(self, expected_type=None, expected_value=None):
        token = self.current_token()
        if not token:
            return False
        
        if expected_type and token.type != expected_type:
            return False
        
        if expected_value and token.value != expected_value:
            return False
        
        self.pos += 1
        return True
    
    def expect(self, expected_type=None, expected_value=None, error_msg=None):
        token = self.current_token()
        
        if not token:
            self.add_error(error_msg or "Unexpected end of file")
            return False
        
        if expected_type and token.type != expected_type:
            self.add_error(error_msg or f"Expected type {expected_type}, got {token.type}")
            return False
        
        if expected_value and token.value != expected_value:
            self.add_error(error_msg or f"Expected '{expected_value}', got '{token.value}'")
            return False
        
        self.pos += 1
        return True
    
    def add_error(self, message):
        token = self.current_token()
        if token:
            self.errors.append(f"At token {self.pos} ({token.type}, {token.value}): {message}")
        else:
            self.errors.append(f"At end of file: {message}")
    
    def parse(self):
        try:
            self.program()
            
            if not self.has_main:
                self.add_error("Missing main function")
                return False
            
            return len(self.errors) == 0
        except Exception as e:
            self.add_error(f"Parser exception: {str(e)}")
            return False
    
    def global_declaration(self):
        token = self.current_token()
        if not token:
            return False
        
        if not (token.type == 'KEYWORD' and token.value in ['int', 'float', 'double', 'char']):
            self.add_error("Expected datatype for global declaration")
            return False
        
        next_token = self.peek_token(1)
        next_next = self.peek_token(2)
        
        if not next_token:
            self.add_error("Expected identifier after datatype")
            return False
        
        if next_token.type not in ['IDENTIFIER', 'KEYWORD']:
            self.add_error("Expected identifier after datatype")
            return False
        
        if next_next and next_next.type == 'SPECIAL CHARACTER' and next_next.value == '(':
            return self.func()
        else:
            return self.global_variable()
    
    def global_variable(self):
        self.pos += 1
        
        if not self.expect('IDENTIFIER'):
            return False
        
        token = self.current_token()
        
        if token and token.type == 'OPERATOR' and token.value == '=':
            self.pos += 1
            self.expression()
            token = self.current_token()
        
        while token and token.type == 'SPECIAL CHARACTER' and token.value == ',':
            self.pos += 1
            if not self.expect('IDENTIFIER'):
                return False
            token = self.current_token()
            
            if token and token.type == 'OPERATOR' and token.value == '=':
                self.pos += 1
                self.expression()
                token = self.current_token()
        
        if not self.expect('SPECIAL CHARACTER', ';'):
            return False
        
        return True
    
    def program(self):
        while self.current_token():
            if not self.global_declaration():
                break
    
    def func(self):
        token = self.current_token()
        if not token:
            return False
        
        if not self.datatype():
            return False
        
        token = self.current_token()
        if not token or token.type not in ['IDENTIFIER', 'KEYWORD']:
            self.add_error("Expected function identifier")
            return False
        
        if token.value == 'main':
            self.has_main = True
        
        self.pos += 1
        
        if not self.expect('SPECIAL CHARACTER', '('):
            return False
        
        if not self.expect('SPECIAL CHARACTER', ')'):
            return False
        
        return self.block()
    
    def datatype(self):
        token = self.current_token()
        if token and token.type == 'KEYWORD' and token.value in ['int', 'float', 'double', 'char']:
            self.pos += 1
            return True
        return False
    
    def block(self):
        if not self.expect('SPECIAL CHARACTER', '{'):
            return False
        
        while True:
            token = self.current_token()
            
            if not token:
                self.add_error("Expected '}' to close block")
                return False
            
            if token.type == 'SPECIAL CHARACTER' and token.value == '}':
                self.pos += 1
                return True
            
            if not self.x():
                self.add_error("Invalid statement in block")
                return False
        
        return True
    
    def x(self):
        token = self.current_token()
        
        if not token:
            return False
        
        if token.type == 'KEYWORD' and token.value in ['int', 'float', 'double', 'char']:
            next_token = self.peek_token(1)
            next_next = self.peek_token(2)
            
            if next_next and next_next.type == 'SPECIAL CHARACTER' and next_next.value == '(':
                return self.func()
            else:
                return self.assign()
        
        if token.type == 'KEYWORD' and token.value == 'if':
            return self.if_statement()
        
        if token.type == 'KEYWORD' and token.value == 'while':
            return self.while_statement()
        
        if token.type == 'KEYWORD' and token.value == 'for':
            return self.for_statement()
        
        if token.type == 'KEYWORD' and token.value == 'return':
            return self.return_statement()
        
        if token.type == 'IDENTIFIER':
            next_token = self.peek_token(1)
            if next_token and next_token.type == 'OPERATOR' and next_token.value == '=':
                return self.assign()
            else:
                return self.expression_statement()
        
        return False
    
    def assign(self):
        token = self.current_token()
        
        has_datatype = False
        if token.type == 'KEYWORD' and token.value in ['int', 'float', 'double', 'char']:
            self.pos += 1
            has_datatype = True
        
        if not self.expect('IDENTIFIER'):
            return False
        
        token = self.current_token()
        
        if has_datatype:
            while token and token.type == 'SPECIAL CHARACTER' and token.value == ',':
                self.pos += 1
                if not self.expect('IDENTIFIER'):
                    return False
                token = self.current_token()
                
                if token and token.type == 'OPERATOR' and token.value == '=':
                    self.pos += 1
                    self.expression()
                    token = self.current_token()
        
        if token and token.type == 'OPERATOR' and token.value == '=':
            self.pos += 1
            self.expression()
        
        if not self.expect('SPECIAL CHARACTER', ';'):
            return False
        
        return True
    
    def expression_statement(self):
        self.expression()
        if not self.expect('SPECIAL CHARACTER', ';'):
            return False
        return True
    
    def expression(self):
        return self.logical_or_expr()
    
    def logical_or_expr(self):
        self.logical_and_expr()
        
        while True:
            token = self.current_token()
            if token and token.type == 'OPERATOR' and token.value == '||':
                self.pos += 1
                self.logical_and_expr()
            else:
                break
        
        return True
    
    def logical_and_expr(self):
        self.equality_expr()
        
        while True:
            token = self.current_token()
            if token and token.type == 'OPERATOR' and token.value == '&&':
                self.pos += 1
                self.equality_expr()
            else:
                break
        
        return True
    
    def equality_expr(self):
        self.relational_expr()
        
        while True:
            token = self.current_token()
            if token and token.type == 'OPERATOR' and token.value in ['==', '!=']:
                self.pos += 1
                self.relational_expr()
            else:
                break
        
        return True
    
    def relational_expr(self):
        self.additive_expr()
        
        while True:
            token = self.current_token()
            if token and token.type == 'OPERATOR' and token.value in ['<', '>', '<=', '>=']:
                self.pos += 1
                self.additive_expr()
            else:
                break
        
        return True
    
    def additive_expr(self):
        self.multiplicative_expr()
        
        while True:
            token = self.current_token()
            if token and token.type == 'OPERATOR' and token.value in ['+', '-']:
                self.pos += 1
                self.multiplicative_expr()
            else:
                break
        
        return True
    
    def multiplicative_expr(self):
        self.unary_expr()
        
        while True:
            token = self.current_token()
            if token and token.type == 'OPERATOR' and token.value in ['*', '/', '%']:
                self.pos += 1
                self.unary_expr()
            else:
                break
        
        return True
    
    def unary_expr(self):
        token = self.current_token()
        
        if token and token.type == 'OPERATOR' and token.value in ['+', '-', '++', '--', '!']:
            self.pos += 1
            return self.unary_expr()
        
        return self.postfix_expr()
    
    def postfix_expr(self):
        self.primary_expr()
        
        while True:
            token = self.current_token()
            if not token:
                break
            
            if token.type == 'SPECIAL CHARACTER' and token.value == '[':
                self.pos += 1
                self.expression()
                self.expect('SPECIAL CHARACTER', ']')
            
            elif token.type == 'SPECIAL CHARACTER' and token.value == '(':
                self.pos += 1
                self.argument_list()
                self.expect('SPECIAL CHARACTER', ')')
            
            elif token.type == 'OPERATOR' and token.value in ['++', '--']:
                self.pos += 1
            
            else:
                break
        
        return True
    
    def argument_list(self):
        token = self.current_token()
        
        if token and token.type == 'SPECIAL CHARACTER' and token.value == ')':
            return True
        
        self.expression()
        
        while True:
            token = self.current_token()
            if token and token.type == 'SPECIAL CHARACTER' and token.value == ',':
                self.pos += 1
                self.expression()
            else:
                break
        
        return True
    
    def primary_expr(self):
        token = self.current_token()
        
        if not token:
            self.add_error("Unexpected end of file in expression")
            return False
        
        if token.type == 'IDENTIFIER':
            self.pos += 1
            return True
        
        if token.type == 'NUMBER':
            self.pos += 1
            return True
        
        if token.type == 'STRING':
            self.pos += 1
            return True
        
        if token.type == 'SPECIAL CHARACTER' and token.value == '(':
            self.pos += 1
            self.expression()
            if not self.expect('SPECIAL CHARACTER', ')'):
                return False
            return True
        
        self.add_error(f"Unexpected token in expression: {token.type} '{token.value}'")
        return False
    
    def if_statement(self):
        self.pos += 1
        
        if not self.expect('SPECIAL CHARACTER', '('):
            return False
        
        self.expression()
        
        if not self.expect('SPECIAL CHARACTER', ')'):
            return False
        
        token = self.current_token()
        if token and token.type == 'SPECIAL CHARACTER' and token.value == '{':
            self.block()
        else:
            self.x()
        
        token = self.current_token()
        if token and token.type == 'KEYWORD' and token.value == 'else':
            self.pos += 1
            
            token = self.current_token()
            if token and token.type == 'SPECIAL CHARACTER' and token.value == '{':
                self.block()
            else:
                self.x()
        
        return True
    
    def while_statement(self):
        self.pos += 1
        
        if not self.expect('SPECIAL CHARACTER', '('):
            return False
        
        self.expression()
        
        if not self.expect('SPECIAL CHARACTER', ')'):
            return False
        
        token = self.current_token()
        if token and token.type == 'SPECIAL CHARACTER' and token.value == '{':
            self.block()
        else:
            self.x()
        
        return True
    
    def for_statement(self):
        self.pos += 1
        
        if not self.expect('SPECIAL CHARACTER', '('):
            return False
        
        token = self.current_token()
        if token and token.type == 'KEYWORD':
            self.assign()
        else:
            self.expression()
            self.expect('SPECIAL CHARACTER', ';')
        
        token = self.current_token()
        if token and not (token.type == 'SPECIAL CHARACTER' and token.value == ';'):
            self.expression()
        self.expect('SPECIAL CHARACTER', ';')
        
        token = self.current_token()
        if token and not (token.type == 'SPECIAL CHARACTER' and token.value == ')'):
            self.expression()
        
        if not self.expect('SPECIAL CHARACTER', ')'):
            return False
        
        token = self.current_token()
        if token and token.type == 'SPECIAL CHARACTER' and token.value == '{':
            self.block()
        else:
            self.x()
        
        return True
    
    def return_statement(self):
        self.pos += 1
        
        token = self.current_token()
        if token and not (token.type == 'SPECIAL CHARACTER' and token.value == ';'):
            self.expression()
        
        if not self.expect('SPECIAL CHARACTER', ';'):
            return False
        
        return True

def parse_cpp_tokens(filename):
    try:
        tokens = read_tokens_from_file(filename)
        
        if not tokens:
            return False, ["No tokens found in file"]
        
        parser = Parser(tokens)
        is_valid = parser.parse()
        
        return is_valid, parser.errors
    except FileNotFoundError:
        return False, [f"File not found: {filename}"]
    except Exception as e:
        return False, [f"Error: {str(e)}"]

if __name__ == "__main__":
    is_valid, errors = parse_cpp_tokens("text.txt")
    
    print("=" * 60)
    print("C++ SYNTAX PARSER")
    print("=" * 60)
    
    if is_valid:
        print("\n✓ Code is syntactically CORRECT!")
        print("✓ All grammar rules satisfied")
        print("✓ Main function found")
    else:
        print("\n✗ Syntax errors found:")
        for error in errors:
            print(f"  - {error}")
    
    print("=" * 60)