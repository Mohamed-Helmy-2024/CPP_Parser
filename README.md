# Recursive-Descent Parser

This README describes the structure, grammar rules, and capabilities of a simple recursive‑descent parser designed to validate C‑like syntax. It explains how the grammar works, how parsing is performed, and how errors are detected.

---

##  **Overview**

This parser is a top‑down recursive‑descent parser that checks whether a program written in a simplified C-like language follows the grammar rules. It identifies syntax errors, reports the exact line number, and displays expected vs. found tokens.

---

##  **Main Capabilities**

* Parse C‑style code according to a defined grammar
* Detect multiple syntax errors in a single run
* Report:

  * Line number
  * Expected token(s)
  * Found token
* Support expressions, assignments, if/else, while, for, and blocks
* Validate function structure: only `int main()` is allowed
* Handle operators and precedence through grammar rules

---

##  **Grammar Rules**

Below is the complete grammar used by the parser, rewritten clearly and cleanly:

```
FUNC       => int main () BLOCK
ASSIGN     => DATATYPE id = VALUE ;
OP         => + | - | * | / | % | < | > | <= | >= | == | != | && | || | += | -= | /= | %= | |= | &=
Y          => op id | eps
EXPRESSION => id Y
DATATYPE   => int | float | double | char
VALUE      => id | number

IF         => if ( EXPR ) BLOCK
IF         => if ( EXPR ) STATEMENT
IF         => if ( EXPR ) BLOCK else BLOCK
IF         => if ( EXPR ) STATEMENT else BLOCK
IF         => if ( EXPR ) BLOCK else STATEMENT
IF         => if ( EXPR ) STATEMENT else STATEMENT

WHILE      => while ( EXPR ) BLOCK
WHILE      => while ( EXPR ) STATEMENT

FOR        => for ( ASSIGN ; EXPR ; EXPR ) BLOCK

X          => FUNC | ASSIGN | EXPRESSION | WHILE
BLOCK      => { X }
```

---

##  **Parser Architecture**

The parser follows classic recursive‑descent structure:

* **Tokenizer**: Converts input code into tokens `<TYPE, value>`
* **Parser**: Consumes tokens using functions matching grammar rules
* **Error Handler**: Reports unexpected tokens and missing components
* **Backtracking**: Not used—grammar must be LL(1)

### Main Parsing Functions

* `parse_func()` → matches `int main() { ... }`
* `parse_block()` → matches `{ STATEMENTS }`
* `parse_assign()` → matches declarations and assignments
* `parse_expr()` → matches identifiers with operators
* `parse_if()`, `parse_while()`, `parse_for()` → control structures

---

##  Syntax Error Reporting

The parser reports detailed errors:

### Example Error:

```
Line 5: Syntax Error
Expected: ')'
Found: '{'
```

### Features:

* Shows **line number** based on token position
* Lists **expected tokens**
* Shows **found token**
* Continues parsing to detect further errors

---

##  Example Accepted Code

```
int main() {
    int x,y;
    // This is a single-line comment
    if (x == 42) {
        /* This is
           a block
           comment */
        x = x-3;
    } else {
        y = 3.1; // Another comment
    }
    return 0;
}
```

---

---

##  Folder Structure Example

```
/project
│── scanner.py
│── cpp_parser.py
│── README.md
│── test.cpp
│── text.txt
```

---

##  Future Improvements

* Add operator precedence parsing
* Support multiple functions
* Add array declarations & pointers
* Introduce static semantic checks (type checking)

---

##  License

MIT License — free for personal and academic use.

---

If you'd like, I can generate:

* A beautifully formatted PDF version
* A Markdown version with syntax highlighting
* A GitHub‑ready folder including parser code and tests
