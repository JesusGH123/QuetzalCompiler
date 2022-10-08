skippedCharacters = [" ", "\t", "\n", "\r"]
characterLiterals = ["n","r","t", "'", '"']

separators = {
     "+": "ADD", "-": "SUB", ",": "COMMA",
     "and": "AND","or": "OR",
    "(": "LPAREN", ")": "RPAREN", "[": "LSQUARE", "]": "RSQUARE", "{": "LCURL", "}": "RCURL",
    "*": "MULT", "%": "MOD", "/": "DIV",
    ":": "COLON", ";": "SEMICOLON",
    "=": "ASSIGNMENT", "+=": "ADD_ASSIGNMENT", "-=": "SUB_ASSIGNMENT", "*=": "MULT_ASSIGNMENT", "/=": "DIV_ASSIGNMENT", "%=": "MOD_ASSIGNMENT",
    "<": "LANGLE", ">": "RANGLE", "<=": "LE", ">=": "GE",
    "!=": "EXCL_EQ", "==": "EQEQ", "'": "CHARACTER", '"': "STRING", "f": "FUNCTION_CALL",
    "printi": "PRINT_I", "printc": "PRINT_C", "prints": "PRINT_S", "println": "PRINT_LN",
    "new": "NEW", "size": "SIZE", "add": "ADD", "get": "GET_", "set(": "SET_"
}

reservedWords = {
    #Keywords
    "return": "RETURN", "break": "BREAK", 
    "file": "FILE", "field": "FIELD", "property": "PROPERTY", "get": "GET", "set": "SET", "receiver": "RECEIVER",
    "var": "VAR", "inc": "INCREMENT", "dec": "DECREMENT", "if": "IF", "else": "ELSE", "elif": "ELIF",
    "loop": "LOOP",  "while": "WHILE", "throw": "THROW", "return": "RETURN", "as": "AS", "is": "IS", "in": "IN", "not": "NOT",

    #Section: Literals
    "true": "BooleanLiteral", "false": "BooleanLiteral",

}

alphabet = ['A','B','C','D','E','F','G','H','I','J','K','L','M','N','O','P','Q','R','S','T','U','V','W','X','Y','Z',
            'a','b','c','d','e','f','g','h','i','j','k','l','m','n','o','p','q','r','s','t','u','v','w','x','y','z',
            '0', '1', '2', '3', '4', '5', '6', '7', '8', '9','_','\\',"'",'"']