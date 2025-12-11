# Top-Down Parser

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

### 🔹 Function Rule (FUNC)

A valid program must begin with **exactly one function**:

* The function must be named **main**.
* It must return **int**.
* It must have **empty parentheses **``.
* It must contain a **block **`` of statements.

### 🔹 Assignment Rule (ASSIGN)

An assignment/declaration must follow this structure:

* Start with a **data type** (int, float, double, char)
* Followed by an **identifier**
* Followed by an equal sign `=`
* Followed by either **a number or another identifier**
* End with a semicolon `;`

### 🔹 Operator Rule (OP)

An operator can be any arithmetic, relational, or logical operator, including:

* `+ - * / %`
* `< > <= >= == !=`
* `&& ||`
* Compound assignments: `+= -= /= %= |= &=`

### 🔹 Expression Rule (EXPRESSION)

An expression consists of:

* An identifier
* Optionally followed by **an operator and another identifier**

### 🔹 Data Types (DATATYPE)

Supported types are:

* `int`
* `float`
* `double`
* `char`

### 🔹 Values (VALUE)

Allowed values in assignments:

* A number
* An identifier

### 🔹 If Statement Rules (IF)

An `if` statement can appear in many forms:

* `if (condition) { block }`
* `if (condition) statement`
* `if (condition) { block } else { block }`
* `if (condition) statement else { block }`
* `if (condition) { block } else statement`
* `if (condition) statement else statement`

### 🔹 While Loop Rules (WHILE)

A while loop can contain:

* A block `{...}`
* Or a single statement Format:
* `while (condition) block`
* `while (condition) statement`

### 🔹 For Loop Rule (FOR)

A for loop must have:

* An assignment
* A condition
* An increment expression
* A block Format:

```
for ( ASSIGN ; EXPR ; EXPR ) BLOCK
```

### 🔹 Statement Group (X)

A statement can be:

* A function
* An assignment
* An expression
* A while loop

### 🔹 Block Rule (BLOCK)

A block is:

* An opening `{`
* Followed by one or more statements (X)
* Ending with a closing `}`


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

