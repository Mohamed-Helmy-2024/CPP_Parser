class Token:
    def __init__(self, token_type, value):
        self.type = token_type
        self.value = value
    
    def __repr__(self):
        return f"Token({self.type}, {self.value})"


def read_tokens_from_file(filename):
    """Read tokens from file in format: <TYPE, value>"""
    tokens = []
    with open(filename, 'r') as f:
        for line in f:
            line = line.strip()
            if line.startswith('<') and line.endswith('>'):
                content = line[1:-1]
                token_type, value = content.split(',', 1)
                tokens.append(Token(token_type.strip(), value.strip()))
    return tokens


class Parser:
    def __init__(self, tokens):
        self.tokens = tokens
        self.pos = 0
        self.errors = []
        self.has_main = False
    
    # ===== Token Navigation =====
    
    def current(self):
        """Get current token"""
        return self.tokens[self.pos] if self.pos < len(self.tokens) else None
    
    def peek(self, offset=1):
        """Look ahead at token"""
        idx = self.pos + offset
        return self.tokens[idx] if idx < len(self.tokens) else None
    
    def advance(self):
        """Move to next token"""
        self.pos += 1
    
    def match(self, token_type=None, value=None):
        """Check if current token matches without consuming"""
        tok = self.current()
        if not tok:
            return False
        if token_type and tok.type != token_type:
            return False
        if value and tok.value != value:
            return False
        return True
    
    def consume(self, token_type=None, value=None, error_msg=None):
        """Match and consume token, or add error"""
        if self.match(token_type, value):
            self.advance()
            return True
        
        tok = self.current()
        if error_msg:
            msg = error_msg
        elif not tok:
            msg = "Unexpected end of file"
        elif token_type and value:
            msg = f"Expected {token_type} '{value}', got {tok.type} '{tok.value}'"
        elif token_type:
            msg = f"Expected {token_type}, got {tok.type}"
        else:
            msg = f"Unexpected token: {tok.type} '{tok.value}'"
        
        self.errors.append(f"At position {self.pos}: {msg}")
        return False
    
    # ===== Main Entry Point =====
    
    def parse(self):
        """Parse entire program"""
        try:
            while self.current():
                self.parse_global_declaration()
            
            if not self.has_main:
                self.errors.append("Missing main function")
            
            return len(self.errors) == 0
        except Exception as e:
            self.errors.append(f"Parser exception: {str(e)}")
            return False
    
    # ===== Top Level =====
    
    def parse_global_declaration(self):
        """Parse global variable or function"""
        if not self.match('KEYWORD') or self.current().value not in ['int', 'float', 'double', 'char']:
            self.errors.append("Expected datatype for global declaration")
            self.advance()  # Skip invalid token
            return
        
        # Check if it's a function (has '(' after identifier)
        if self.peek(2) and self.peek(2).type == 'SPECIAL CHARACTER' and self.peek(2).value == '(':
            self.parse_function()
        else:
            self.parse_global_variable()
    
    def parse_global_variable(self):
        """Parse: datatype id [= expr] [, id [= expr]]* ;"""
        self.advance()  # Skip datatype
        self.consume('IDENTIFIER')
        
        # Optional initialization
        if self.match('OPERATOR', '='):
            self.advance()
            self.parse_expression()
        
        # Additional variables
        while self.match('SPECIAL CHARACTER', ','):
            self.advance()
            self.consume('IDENTIFIER')
            if self.match('OPERATOR', '='):
                self.advance()
                self.parse_expression()
        
        self.consume('SPECIAL CHARACTER', ';')
    
    def parse_function(self):
        """Parse: datatype id() { ... }"""
        self.advance()  # Skip datatype
        
        tok = self.current()
        if tok and tok.value == 'main':
            self.has_main = True
        
        self.consume()  # Function name
        self.consume('SPECIAL CHARACTER', '(')
        self.consume('SPECIAL CHARACTER', ')')
        self.parse_block()
    
    # ===== Statements =====
    
    def parse_block(self):
        """Parse: { statement* }"""
        self.consume('SPECIAL CHARACTER', '{')
        
        while not self.match('SPECIAL CHARACTER', '}'):
            if not self.current():
                self.errors.append("Expected '}' to close block")
                return
            self.parse_statement()
        
        self.consume('SPECIAL CHARACTER', '}')
    
    def parse_statement(self):
        """Parse any statement"""
        tok = self.current()
        if not tok:
            return
        
        # Variable declaration or nested function
        if tok.type == 'KEYWORD' and tok.value in ['int', 'float', 'double', 'char']:
            if self.peek(2) and self.peek(2).type == 'SPECIAL CHARACTER' and self.peek(2).value == '(':
                self.parse_function()
            else:
                self.parse_assignment()
        
        # Control flow
        elif tok.type == 'KEYWORD' and tok.value == 'if':
            self.parse_if_statement()
        elif tok.type == 'KEYWORD' and tok.value == 'while':
            self.parse_while_statement()
        elif tok.type == 'KEYWORD' and tok.value == 'for':
            self.parse_for_statement()
        elif tok.type == 'KEYWORD' and tok.value == 'return':
            self.parse_return_statement()
        
        # Assignment or expression
        elif tok.type == 'IDENTIFIER':
            if self.peek() and self.peek().type == 'OPERATOR' and self.peek().value == '=':
                self.parse_assignment()
            else:
                self.parse_expression()
                self.consume('SPECIAL CHARACTER', ';')
        
        else:
            self.errors.append(f"Invalid statement starting with {tok.type} '{tok.value}'")
            self.advance()
    
    def parse_assignment(self):
        """Parse: [datatype] id [= expr] [, id [= expr]]* ;"""
        # Optional datatype
        if self.match('KEYWORD') and self.current().value in ['int', 'float', 'double', 'char']:
            has_datatype = True
            self.advance()
        else:
            has_datatype = False
        
        self.consume('IDENTIFIER')
        
        # For declarations, allow multiple variables
        if has_datatype:
            while self.match('SPECIAL CHARACTER', ','):
                self.advance()
                self.consume('IDENTIFIER')
                if self.match('OPERATOR', '='):
                    self.advance()
                    self.parse_expression()
        
        # Assignment
        if self.match('OPERATOR', '='):
            self.advance()
            self.parse_expression()
        
        self.consume('SPECIAL CHARACTER', ';')
    
    def parse_if_statement(self):
        """Parse: if (expr) statement [else statement]"""
        self.advance()  # Skip 'if'
        self.consume('SPECIAL CHARACTER', '(')
        self.parse_expression()
        self.consume('SPECIAL CHARACTER', ')')
        
        # Then branch
        if self.match('SPECIAL CHARACTER', '{'):
            self.parse_block()
        else:
            self.parse_statement()
        
        # Else branch
        if self.match('KEYWORD', 'else'):
            self.advance()
            if self.match('SPECIAL CHARACTER', '{'):
                self.parse_block()
            else:
                self.parse_statement()
    
    def parse_while_statement(self):
        """Parse: while (expr) statement"""
        self.advance()  # Skip 'while'
        self.consume('SPECIAL CHARACTER', '(')
        self.parse_expression()
        self.consume('SPECIAL CHARACTER', ')')
        
        if self.match('SPECIAL CHARACTER', '{'):
            self.parse_block()
        else:
            self.parse_statement()
    
    def parse_for_statement(self):
        """Parse: for (init; cond; update) statement"""
        self.advance()  # Skip 'for'
        self.consume('SPECIAL CHARACTER', '(')
        
        # Init (can be declaration or expression)
        if self.match('KEYWORD'):
            self.parse_assignment()
        elif not self.match('SPECIAL CHARACTER', ';'):
            self.parse_expression()
            self.consume('SPECIAL CHARACTER', ';')
        else:
            self.consume('SPECIAL CHARACTER', ';')
        
        # Condition
        if not self.match('SPECIAL CHARACTER', ';'):
            self.parse_expression()
        self.consume('SPECIAL CHARACTER', ';')
        
        # Update
        if not self.match('SPECIAL CHARACTER', ')'):
            self.parse_expression()
        
        self.consume('SPECIAL CHARACTER', ')')
        
        if self.match('SPECIAL CHARACTER', '{'):
            self.parse_block()
        else:
            self.parse_statement()
    
    def parse_return_statement(self):
        """Parse: return [expr] ;"""
        self.advance()  # Skip 'return'
        
        if not self.match('SPECIAL CHARACTER', ';'):
            self.parse_expression()
        
        self.consume('SPECIAL CHARACTER', ';')
    
    # ===== Expressions (Precedence Climbing) =====
    
    def parse_expression(self):
        """Parse full expression"""
        self.parse_logical_or()
    
    def parse_logical_or(self):
        """Parse: logical_and (|| logical_and)*"""
        self.parse_logical_and()
        while self.match('OPERATOR', '||'):
            self.advance()
            self.parse_logical_and()
    
    def parse_logical_and(self):
        """Parse: equality (&& equality)*"""
        self.parse_equality()
        while self.match('OPERATOR', '&&'):
            self.advance()
            self.parse_equality()
    
    def parse_equality(self):
        """Parse: relational ((==|!=) relational)*"""
        self.parse_relational()
        while self.match('OPERATOR') and self.current().value in ['==', '!=']:
            self.advance()
            self.parse_relational()
    
    def parse_relational(self):
        """Parse: additive ((<|>|<=|>=) additive)*"""
        self.parse_additive()
        while self.match('OPERATOR') and self.current().value in ['<', '>', '<=', '>=']:
            self.advance()
            self.parse_additive()
    
    def parse_additive(self):
        """Parse: multiplicative ((+|-) multiplicative)*"""
        self.parse_multiplicative()
        while self.match('OPERATOR') and self.current().value in ['+', '-']:
            self.advance()
            self.parse_multiplicative()
    
    def parse_multiplicative(self):
        """Parse: unary ((*|/|%) unary)*"""
        self.parse_unary()
        while self.match('OPERATOR') and self.current().value in ['*', '/', '%']:
            self.advance()
            self.parse_unary()
    
    def parse_unary(self):
        """Parse: (+|-|++|--|!)* postfix"""
        if self.match('OPERATOR') and self.current().value in ['+', '-', '++', '--', '!']:
            self.advance()
            self.parse_unary()
        else:
            self.parse_postfix()
    
    def parse_postfix(self):
        """Parse: primary ([expr] | (args) | ++ | --)*"""
        self.parse_primary()
        
        while self.current():
            # Array subscript
            if self.match('SPECIAL CHARACTER', '['):
                self.advance()
                self.parse_expression()
                self.consume('SPECIAL CHARACTER', ']')
            
            # Function call
            elif self.match('SPECIAL CHARACTER', '('):
                self.advance()
                self.parse_argument_list()
                self.consume('SPECIAL CHARACTER', ')')
            
            # Post increment/decrement
            elif self.match('OPERATOR') and self.current().value in ['++', '--']:
                self.advance()
            
            else:
                break
    
    def parse_argument_list(self):
        """Parse: [expr (, expr)*]"""
        if self.match('SPECIAL CHARACTER', ')'):
            return
        
        self.parse_expression()
        while self.match('SPECIAL CHARACTER', ','):
            self.advance()
            self.parse_expression()
    
    def parse_primary(self):
        """Parse: identifier | number | string | (expr)"""
        tok = self.current()
        
        if not tok:
            self.errors.append("Unexpected end of file in expression")
            return
        
        if tok.type in ['IDENTIFIER', 'NUMBER', 'STRING']:
            self.advance()
        elif self.match('SPECIAL CHARACTER', '('):
            self.advance()
            self.parse_expression()
            self.consume('SPECIAL CHARACTER', ')')
        else:
            self.errors.append(f"Unexpected token in expression: {tok.type} '{tok.value}'")
            self.advance()


def parse_cpp_tokens(filename):
    """Main function to parse C++ tokens from file"""
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