import sys
import string

keywords = ['if', 'else','for','do', 'while', 'return', 'const','int','float','char','void','switch','case','default','break','continue','struct','typedef','sizeof','main', 'include', 'define', 'class', 'string']
operators = ['+', '-', '*', '/', '=', '==', '!=', '<', '>', '<=', '>=', '++', '--', '&&', '||', '!', '%', '&', '|', '^', '~', '<<', '>>']
special_chars = [';', ',', '(', ')', '{', '}', '[', ']', '#', '"', "'", ':']
new_line_chars = ['\n', 'endl']

tokens =[]

def scanner(code):
    i=0
    while i < len(code): 
        if code[i] == '/' and i+1 < len(code):
            if code[i+1] == '/':
                while i < len(code) and code[i] != '\n':
                    i += 1
            elif code[i+1] == '*':
                i += 2
                while i < len(code)-1 and not (code[i] == '*' and code[i+1] == '/'):
                    i += 1
                i += 2

        elif code[i].isspace():
            i+=1
            continue
        
        elif code[i].isalpha() or code[i] == '_':
            start = i
            while i < len(code) and (code[i].isalnum() or code[i] == '_'):
                i += 1
            lexeme = code[start:i]
            if lexeme in keywords:
                tokens.append(f'<KEYWORD, {lexeme}>')
            else:
                tokens.append(f'<IDENTIFIER, {lexeme}>')
            i -= 1

        elif code[i].isdigit() :
            start = i
            while i < len(code) and code[i].isdigit()or (code[i] == '.' and i + 1 < len(code) and code[i + 1].isdigit()):
                i += 1
            lexeme = code[start:i]
            tokens.append(f'<NUMBER, {lexeme}>')
            i -= 1

        elif code[i] in special_chars:    
            tokens.append(f'<SPECIAL CHARACTER, {code[i]}>')    

        elif code[i] in operators:
            if i+1 < len(code) and code[i+1] in operators:
                tokens.append(f'<OPERATOR, {code[i]}{code[i+1]}>')
                i += 1
            else :
                tokens.append(f'<OPERATOR, {code[i]}>')

        elif i+1 < len(code) and code[i:i+2] in operators:
            tokens.append(f'<NEW LINE, {code[i:i+2]}>')
            i += 2

        elif i+3 < len(code) and code[i:i+4] in new_line_chars:
            tokens.append(f'<NEW LINE, {code[i:i+4]}>')
            i += 3

        else :
            raise ValueError(f"Unrecognized character: {code[i]}")
        
        i+=1
        
    return tokens

if __name__ == "__main__":
    result =[]
    with open('test.cpp', 'r') as file:
        code = file.read()
        result = scanner(code)

    with open('text.txt', 'w') as file:
        for token in result:
            file.write(token + '\n')
