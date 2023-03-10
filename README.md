# Lexer implementation in Python
## Regex format

```
<regex> ::= <regex><regex> | 
            <regex> '|' <regex> | 
            <regex>'*' | <regex>'+' | <regex>'?' | 
            '(' <regex> ')' | 
            "[A-Z]" |
            "[a-z]" |
            "[0-9]" |
            "eps" | <character>
```

Examples:
- ```[0-9]*|b```
- ```a([a-z]*|[A-Z]*)z```
- ```[0-9]+(\'-\'[0-9]+)*```

Inside, each regex is preprocessed and passed to a prenex form (e.g. **CONCAT a b**) then converted to an DFA, where each DFA is built from an NFA.

## Lexer input
Lexer's input consists of 2 components:
1. a specification (configuration)
2. a text that will be analyzed lexically, more precisely, divided into lexemes.


The specification has the following structure:
```
TOKEN1 : REGEX1;
TOKEN2 : REGEX2;
TOKEN3 : REGEX3;
...
```
Where each TOKENi is a name given to a token and REGEXi is a regex which describes that token.

## Lexer output
Lexer's output is a list of form: ```[(lexeme1, TOKEN_LEXEME_1), (lexeme2, TOKEN_LEXEME_2), …]```, where TOKEN_LEXEME_i is the name associated to token of lexeme i, based on specification.
## Implementation
1. Each regex is converted to NFA, saving the information about its token and its position in specification.
2. An unique NFA is built which connects all NFAs for every regexes from specification
3. This "big" NFA is converted to a DFA.

## Project structure
```
...
└── src
        ├── Dfa.py - DFA class
        ├── Nfa.py - NFA class
        ├── Regex.py - Regex preprocessing object
        ├── Lexer.py - lexer class
	...
```
