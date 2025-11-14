
### Toy Language Interpreter

This project is a Java-based interpreter for a simple imperative "Toy Language," developed as a university assignment for an Advanced Programming Methods course. The interpreter is built using the Model-View-Controller (MVC) architectural pattern and demonstrates core concepts of language design, data structures, and concurrent execution.
### ✨ Core Features
- MVC Architecture: Clear separation of concerns between the data model (language components), the view (text menu), and the controller (execution logic).
- Custom Abstract Data Types: Generic, custom-built ADTs for the Execution Stack (MyIStack), Symbol Table (MyIDictionary), and Output List (MyIList) that wrap Java's standard collections.
- Core Language Constructs: Support for variable declarations, assignments, conditional If statements, and Print statements.
- Expressions: Evaluation of arithmetic expressions (+, -, *, /) and logical expressions (and, or).
- Type System: A basic static type system with int and bool types.
- Exception Handling: A custom exception hierarchy to manage runtime errors like division by zero, type mismatches, and undefined variables.
### New Advanced Features 
- 📝 Step-by-Step Execution Logging: The entire state of the program (Execution Stack, Symbol Table, etc.) is logged to a text file after every single execution step, providing a detailed trace of the program's execution.
- 📁 File Handling Operations: The language now supports file operations, allowing programs to open, read from, and close text files.
- ⛓️ Relational Expressions: Added support for relational operators: <, <=, \==, !=, >, >=.
- "String" Data Type: Implemented StringType and StringValue to support file names and future string manipulations.
- Enhanced Menu System: The user interface was refactored to use the Command Design Pattern, making it more modular and extensible.

### 🏛️ Architectural Pattern (MVC)

The project strictly follows the Model-View-Controller pattern:
- Model: Contains the core logic and data structures of the language. This includes all statements (IStmt), expressions (IExp), types (IType), values (IValue), and the ADTs (MyIStack, MyIDictionary, MyIList, FileTable). The PrgState class encapsulates the entire state of a running program.
- View: The user interface, responsible for presenting the program options and displaying output. In this project, it's a TextMenu class that runs in the console.
- Controller: Orchestrates the execution. It takes a PrgState from the Repository, executes one step of the program by popping a statement from the execution stack, and updates the state. It also manages the program logging.
- Repository: Manages the collection of PrgState objects. For this assignment, it holds one program state at a time and is responsible for invoking the logging mechanism.

### 📋 Implemented Language Constructs
#### Statements (IStmt)

| Statement           | Syntax Example                         | Description                                        |
| ------------------- | -------------------------------------- | -------------------------------------------------- |
| Compound            | { Stmt1; Stmt2 }                       | Executes statements sequentially.                  |
| Var Declaration<br> | Type var_name;                         | Declares a variable of a given type.               |
| Assignment<br>      | var_name = expression;                 | Assigns the result of an expression to a variable. |
| Print<br>           | print(expression);                     | Prints the value of an expression to the console.  |
| If                  | if (exp) then { Stmt1 } else { Stmt2 } | Conditional execution.                             |
| openRFile           | openRFile(string_exp);                 | Opens a file for reading.                          |
| readFile            | readFile(file_exp, var_name);          | Reads an integer from a file into a variable.      |
| closeRFile          | closeRFile(string_exp);                | Closes an opened file.                             |
| No Operation        | nop;                                   | Does nothing.                                      |

#### Expressions (IExp)

| Expression Type | Syntax Example              |
| --------------- | --------------------------- |
| Value           | 10, true                    |
| Variable        | v, a                        |
| Arithmetic      | exp1 + exp2, exp1 * exp2    |
| Relational      | exp1 < exp2, exp1 == exp2   |
| Logical         | exp1 and exp2, exp1 or exp2 |

### 🚀 How to Run
Prerequisites
- Java Development Kit (JDK) 11 or higher.
- Apache Maven.
Steps
- Clone the repository:
```
git clone https://github.com/your-username/your-repo-name.git
cd your-repo-name
```

Build the project using Maven:
This command will compile the code and package it into a runnable .jar file in the target/ directory.
code Bash

```
mvn clean install
```

Run the application:
```
java -jar target/your-project-name-1.0-SNAPSHOT.jar
```
      
You will be greeted with a text menu. Enter the number corresponding to the program you wish to execute.

### 📄 Logging Feature Explained

A key feature of this version is the ability to log the program's state. When you run a program, a log file (e.g., log1.txt) will be created or appended to in the project's root directory.

The log file provides a snapshot of the PrgState after each execution step, formatted as follows:
code Code

ExeStack:
[statement_on_top]
[next_statement]
...
SymTable:
var1 --> value1
var2 --> value2
...
Out:
output_value1
output_value2
...
FileTable:
"test.in" --> file_descriptor
...
-----------------------------------------

This feature is invaluable for debugging and understanding the interpreter's behavior.
💡 Example Programs

The menu comes pre-loaded with several examples to test the interpreter's functionality.
