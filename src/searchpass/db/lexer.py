# -*- coding: UTF-8 -*-
from .table import FIELDS


TOKEN_SPEC = [
    ("FIELD",    r"\b(?:[a-z](_?[a-z])*)\b"),                      # Allowed field names
    ("LIKE", r"\b(?:NOT|LIKE)\b"),                                 # LIKE operator (with NOT)
    ("OPERATOR", r"=|!=|<>"),                                      # Allowed operators
    ("STRING",   r"(?P<quote>['\"])(?:(?!\1).|\\.)*?(?P=quote)"),  # String in single quotes
    ("AND",      r"\bAND\b"),                                      # AND operator
    ("OR",       r"\bOR\b"),                                       # OR operator
    ("LPAREN",   r"\("),                                           # Left parenthesis
    ("RPAREN",   r"\)"),                                           # Right parenthesis
    ("SKIP",     r"[ \t]+"),                                       # Skip whitespace
]


class WhereStatementLexer:
    def __init__(self, text):
        self.__text = text
        self.__tokens = WhereStatementLexer.tokenize(text)
        self.__valid = WhereStatementLexer.validate(text)
    
    @property
    def text(self):
        return self.__text
    
    @property
    def tokens(self):
        return self.__tokens
    
    @property
    def valid(self):
        return self.__valid
    
    @staticmethod
    def prepare(text):
        tokens = WhereStatementLexer.tokenize(text)
        WhereStatementLexer.parse(tokens)
        return " ".join("?" if kind == "STRING" else value for kind, value in tokens), \
               tuple(value.strip("'\"") for kind, value in tokens if kind == "STRING")
    
    @staticmethod
    def parse(text_or_tokens):
        tokens = WhereStatementLexer.tokenize(text_or_tokens) if isinstance(text_or_tokens, str) else text_or_tokens
        stack, i = [], 0
        while i < len(tokens):
            kind, value = tokens[i]
            if kind == "FIELD":
                if value not in FIELDS.keys():
                    raise SyntaxError(f"Unknown field: {value}")
                # expect FIELD OP STRING
                if i + 2 < len(tokens) and (tokens[i+1][0] == "OPERATOR" or tokens[i+1][1] == "LIKE") and \
                   tokens[i+2][0] == "STRING":
                    stack.append((kind, value))
                    stack.append(tokens[i+1])
                    stack.append(tokens[i+2])
                    i += 3
                elif i + 3 < len(tokens) and tokens[i+1][0] == "LIKE" and tokens[i+1][1] == "NOT" and \
                   tokens[i+2][0] == "LIKE" and tokens[i+3][0] == "STRING":
                    stack.append((kind, value))
                    stack.append(tokens[i+1])
                    stack.append(tokens[i+2])
                    stack.append(tokens[i+3])
                    i += 4
                else:
                    raise SyntaxError("Expected (OPERATOR | NOT LIKE) STRING after FIELD")
            elif kind in {"AND", "OR"}:
                # process AND with higher precedence than OR
                while stack and stack[-1][0] == "AND" and kind == "OR":
                    op = stack.pop()
                    rhs = stack.pop()
                    lhs = stack.pop()
                    stack.append(("EXPR", (lhs, op, rhs)))
                stack.append((kind, value))
                i += 1
            elif kind in {"LPAREN", "RPAREN"}:
                stack.append((kind, value))
                i += 1
            else:
                raise SyntaxError(f"Unexpected token: {value}")
        # handle remaining operators in the stack
        while len(stack) > 1:
            rhs = stack.pop()
            op = stack.pop()
            lhs = stack.pop()
            stack.append(("EXPR", (lhs, op, rhs)))
        return stack[0] if stack else None
    
    @staticmethod
    def tokenize(text):
        import re
        regex, tokens = re.compile("|".join(f"(?P<{name}>{pattern})" for name, pattern in TOKEN_SPEC)), []
        for match in regex.finditer(text):
            kind = match.lastgroup
            value = match.group()
            if kind == "SKIP":
                continue
            tokens.append((kind, value))
        return tokens
    
    @staticmethod
    def validate(text_or_tokens):
        try:
            expr = WhereStatementLexer.parse(text_or_tokens)
            if expr is not None:
                raise SyntaxError(f"Unparsed expression: {expr[1]}")
            return True
        except:
            return False

