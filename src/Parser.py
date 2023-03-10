from __future__ import annotations
import string
from src.Regex import Character, Operator

class Parser:
    @staticmethod
    def transform_syntactic_sugars(alphabet: list, character1, character2):
        """
        Transforms syntactic sugars in a regular expression.
        @param alphabet: A list of characters to be transformed.
        @param character1: The first character in the syntactic sugar pattern.
        @param character2: The second character in the syntactic sugar pattern.
        @return: A list of transformed characters in the regular expression. If character2 is not found in the alphabet,
         returns None.
        """
        res = []
        character1_found = False
        for i in alphabet:
            if i == character2:
                if character1 == character2:
                    res.append(Operator("("))
                res.append(Character(i))
                res.append(Operator(")"))
                return res

            if i == character1:
                character1_found = True
                res.append(Operator("("))
            if character1_found:
                res.append(Character(i))
                res.append(Operator("|"))

        return None

    @staticmethod
    def syntactic_sugars(character1, character2):
        """
        Returns a list of transformed characters in the regular expression for a given syntactic sugar pattern.
        @param character1: The first character in the syntactic sugar pattern.
        @param character2: The second character in the syntactic sugar pattern.
        @return: A list of transformed characters in the regular expression for the given syntactic sugar pattern.
        """
        res = []
        numbers = list(string.digits)
        lower_letters = list(string.ascii_lowercase)
        upper_letters = list(string.ascii_uppercase)
        if character1 in numbers:
            res.extend(Parser.transform_syntactic_sugars(numbers, character1, character2))
        elif character1 in lower_letters:
            res.extend(Parser.transform_syntactic_sugars(lower_letters, character1, character2))
        elif character1 in upper_letters:
            res.extend(Parser.transform_syntactic_sugars(upper_letters, character1, character2))

        return res

    @staticmethod
    def preprocess(regex: str) -> list:
        """
        Preprocesses a regular expression string to add concatenation operators where necessary.
        @param regex: The regular expression string to preprocess.
        @return: A list of operators and characters with concatenation operators added where necessary.
        """
        operators = ["(", ")", "[", "]", "*", "+","?", "|"]
        chars = ["+","*",")","?", "|"]
        previous = None
        res = []
        str_len = len(regex)
        i = 0
        while i < str_len:
            # Add concatenation operator if necessary
            if previous is not None:
                if previous != Operator("(") and previous != Operator("|"):
                    if regex[i] not in chars:
                        res.append(Operator("&"))
            # Handle character classes
            if regex[i] == "[":
                res.extend(Parser.syntactic_sugars(regex[i + 1], regex[i + 3]))
                i += 5
                previous = Operator(")")
                continue
            # Handle eps character
            elif regex[i] == "e" and ((i + 2) < str_len):
                if regex[i + 1] == "p" and regex[i + 2] == "s":
                    res.append(Character("eps"))
                    i += 3
                else:
                    previous = Character(regex[i])
                    res.append(Character(regex[i]))
                    i += 1
                continue
            # Handle escaped characters
            elif regex[i] == "'":
                aux = regex[i] + regex[i+1] + regex[i+2]
                previous = aux
                res.append(Character(aux))
                i += 3
            # Handle operators and regular characters
            else:
                if regex[i] in operators:
                    previous = Operator(regex[i])
                    res.append(Operator(regex[i]))
                else:
                    previous = Character(regex[i])
                    res.append(Character(regex[i]))
                i += 1
        return res


    @staticmethod
    def getPrioprity(operator):
        """
        Given an operator, returns its priority value according to the following rules:
        - Parentheses have the lowest priority (0)
        - The OR operator (|) has priority 1
        - The concatenation operator (&) has priority 2
        - High priority operators (+, *, ?) have priority 3
        - Any other operator has priority 0
        @param operator: the operator for which to determine priority.
        @return: The priority value of the operator.
        """
        parentheses = [Operator("("), Operator(")")]
        high_priority_operators = [Operator("+"), Operator("*"), Operator("?")]
        if operator in parentheses:
            return 0
        if operator == Operator("|"):
            return 1
        if operator == Operator("&"):
            return 2
        if operator in high_priority_operators:
            return 3
        return 0



    @staticmethod
    def infixToPrefix(infix):
        """
        Convert the given infix expression to prefix notation.
        @param infix: The list containing the infix expression.
        @return: The list containing the prefix expression.
        """
        operators_with_2_operands = [Operator("|"), Operator("&"), Operator("("), Operator(")")]
        operators_with_1_operand = [Operator("+"), Operator("*"), Operator("?")]

        operators = []
        characters = []

        # Iterate through each element of the infix expression
        for elem in infix:
            if elem == Operator("("):
                operators.append(elem)
            elif elem == Operator(")"):
                # If element is closing parenthesis, apply operators until matching opening parenthesis is found
                while len(operators) != 0 and operators[-1] != Operator("("):
                    Parser.applyOperator(characters, operators, operators_with_1_operand, operators_with_2_operands)

                operators.pop()
            elif isinstance(elem,Character):
                # If element is a character, push onto characters stack
                characters.append(elem)
            else:
                # If element is an operator, apply operators until top of stack has lower priority
                while len(operators) != 0 and Parser.getPrioprity(elem) < Parser.getPrioprity(operators[-1]):
                    Parser.applyOperator(characters, operators, operators_with_1_operand, operators_with_2_operands)

                operators.append(elem)
        # Apply remaining operators to characters stack
        while len(operators) != 0:
            Parser.applyOperator(characters, operators, operators_with_1_operand, operators_with_2_operands)

        return characters

    @staticmethod
    def applyOperator(characters, operators, operators_with_1_operand, operators_with_2_operands):
        """
        Apply the next operator on the top of the operators stack to the top 1 or 2 characters of the characters stack.
        @param characters: A list of characters and previously applied operators.
        @param operators: A list of operators in infix notation.
        @param operators_with_1_operand: A list of operators that take only one operand.
        @param operators_with_2_operands: A list of operators that take two operands.
        """
        operator = operators.pop()
        if operator in operators_with_2_operands:
            char1 = characters.pop()
            char2 = characters.pop()
            characters.append([operator, char2, char1])
        elif operator in operators_with_1_operand:
            char1 = characters.pop()
            characters.append([operator, char1])

    @staticmethod
    def list_to_char_list(prenex):
        """
        Convert the given prenex expression to a list of characters.
        @param prenex: The prenex expression to convert.
        @return: A list of characters.
        """
        if isinstance(prenex, Operator):
            return prenex.op
        if isinstance(prenex,Character):
            if prenex == Character("eps"):
                return "eps"
            return prenex.chr
        res = []
        for elem in prenex:
            if elem == Character("eps"):
                res.append("eps")
            else:
                res.extend(Parser.list_to_string(elem))
        return res

    @staticmethod
    def list_to_string(prenex):
        """
        Convert the given list of characters or operators to a string.
        @param prenex: The list containing characters and/or operators.
        @return: A string representation of the input list.
        """
        vec = Parser.list_to_char_list(prenex)
        res = ""
        for i in vec:
            res += i

        return res


    @staticmethod
    def prenex_to_DFA_prenex(prenex):
        """
        Convert the given prenex expression to DFA prenex notation.
        @param prenex: The list containing the prenex expression.
        @return: The string containing the DFA prenex expression.
        """
        res = ""
        i = 0
        while i < len(prenex):
            if prenex[i] == "|":
                res += "UNION "
                i += 1
            elif prenex[i] == "&":
                res += "CONCAT "
                i += 1
            elif prenex[i] == "*":
                res += "STAR "
                i += 1
            elif prenex[i] == "+":
                res += "PLUS "
                i += 1
            elif prenex[i] == "?":
                res += "MAYBE "
                i += 1
            else:
                if prenex[i] == "e" and (i + 2) < len(prenex):
                    if prenex[i + 1] == 'p' and prenex[i + 2] == 's':
                        res += "eps"
                        i += 3
                        continue
                if prenex[i] == "'":
                    res += prenex[i]
                    i += 1
                    while prenex[i] != "'":
                        res += prenex[i]
                        i += 1
                    res += prenex[i]
                    if i < len(prenex) - 1:
                        res += " "
                    i += 1
                    continue
                res += prenex[i]
                if i != len(prenex) - 1:
                    res += " "
                i += 1
        return res


    @staticmethod
    def toPrenex(s: str) -> str:
        return Parser.prenex_to_DFA_prenex(Parser.list_to_string(Parser.infixToPrefix(Parser.preprocess(s))))