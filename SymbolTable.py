skippedCharacters = [" ", "\t", "\n", "\r"]
characterLiterals = ["n","r","t", "'", '"']

separators = {
     "+": 1, ",": 3,
     "and": 4,"or": 5,
    "(": 6, ")": 7, "[": 8, "]": 9, "{": 10, "}": 11,
    "*": 12, "%": 13, "/": 14,
    ":": 15, ";": 16,
    "=": 17, "+=": 18, "-=": 19, "*=": 20, "/=": 21, "%=": 22,
    "<": 23, ">": 24, "<=": 25, ">=": 26,
    "!=": 27, "==": 28, "'": 29, '"': 30,
    "printi": 32, "printc": 33, "prints": 34, "println": 35,
    "new": 36, "size": 37, "add": 38, "get": 39, "set": 40
}

reservedWords = {
    #Keywords
    "return": 41, "break": 42, "-": 2,
    "file": 43, "field": 44, "property": 45, "get": 46, "set": 47, "receiver": 48,
    "var": 49, "inc": 50, "dec": 51, "if": 52, "else": 53, "elif": 54,
    "loop": 55,  "while": 56, "throw": 57, "return": 58, "as": 59, "is": 60, "in": 61, "not": 62, "f": 31,

    #Section: Literals
    "true": 100, "false": 101,
}

alphabet = ['A','B','C','D','E','F','G','H','I','J','K','L','M','N','O','P','Q','R','S','T','U','V','W','X','Y','Z',
            'a','b','c','d','e','f','g','h','i','j','k','l','m','n','o','p','q','r','s','t','u','v','w','x','y','z',
            '0', '1', '2', '3', '4', '5', '6', '7', '8', '9','_','\\',"'",'"']