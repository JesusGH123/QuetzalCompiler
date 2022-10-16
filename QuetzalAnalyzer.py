#Analizador sintactico
#Jesus Garcia Hernandez
#Mario Cuevas 
#Juan Pablo Hernandez

import sys
import SymbolTable
import colorama
import re
from colorama import Fore

#Variables
skippedCharacters = SymbolTable.skippedCharacters
separators = SymbolTable.separators
reservedWords = SymbolTable.reservedWords
alphabet = SymbolTable.alphabet
characterLiterals = SymbolTable.characterLiterals
readedTokens = []

def readFile():
    global file
    with open(sys.argv[1]) as f:
        file = f.readlines() 

def lexicalAnalize():
    delimitedComment = False
    stringMode = False
    
    for line in file:
        currToken = ""
        skipTokens = 0
        
        for i in range(len(line)):
            if(i+1 < len(line) and line[i] == '/' and line[i+1] == '/'):    #Skip one line comments
                break
            elif(delimitedComment == False and line[i] == '/' and line[i+1] == '*'):    #Begin of a multiline comment
                delimitedComment = True
            elif(delimitedComment == True and line[i-1] == '*' and line[i] == '/'):     #Ending of a multiline comment
                delimitedComment = False
            elif(delimitedComment == True):     #Skip when analyzer is in multiline comment mode
                continue
            else:
                if(line[i] == '"' and stringMode == False):
                    if(currToken != ""):
                        readedTokens.append(currToken)
                        currToken = ""
                    stringMode = True
                    currToken = currToken + line[i]
                elif(line[i] == '"' and stringMode == True):
                    currToken = currToken + line[i]
                    readedTokens.append(currToken)
                    currToken  = ""
                    stringMode = False
                elif(stringMode == True):
                    currToken = currToken + line[i]
                elif(line[i] in skippedCharacters): #If there is a skipping token check if currword has something
                    if(currToken != ""):
                        readedTokens.append(currToken)
                        currToken = ""
                elif(skipTokens > 0):   #For multiple character tokens
                    skipTokens = skipTokens - 1
                elif(i+2 < len(line) and line[i]+line[i+1]+line[i+2] in separators):    # Three character tokens
                    if(currToken != ""):
                        readedTokens.append(currToken)
                        currToken = ""
                    readedTokens.append(line[i]+line[i+1]+line[i+2])
                    skipTokens = 2
                elif(i+1 < len(line) and ((line[i]+line[i+1] in separators) or line[i]=='\\' and line[i+1] in characterLiterals)):
                    if(currToken != ""):
                        readedTokens.append(currToken)
                        currToken = ""
                    readedTokens.append(line[i]+line[i+1])
                    skipTokens = 1
                #Check this condition
                elif(line[i] in separators):
                    if(currToken != ""):
                        readedTokens.append(currToken)
                        currToken = ""
                    readedTokens.append(line[i])
                else:
                    currToken = currToken + line[i]
    
    classifyTokens()

def classifyTokens():
    
    for i in range(len(readedTokens)):
        if(readedTokens[i] in separators):
            print(readedTokens[i], separators[readedTokens[i]])
        elif(readedTokens[i] in reservedWords):
            print(readedTokens[i], reservedWords[readedTokens[i]])
        else:
            literalValidaton(readedTokens[i])

def literalValidaton(token):
    if(token[0] == '"' and token[len(token)-1] == '"'):
        print(token, 102)
    elif(re.match(r'(^[0-9]*$)', token)):
        print(token, 103)
    elif(token[0] == '\\'):
        if(token[1] in characterLiterals):
            print(token, 104)
        elif(re.match(r'(^(\\u)[0-9][0-9][0-9][0-9][0-9][0-9]$)', token)):
            print(token, 105)
        else:
            Error(token)
    else:
        tokenValidation(token)

def tokenValidation(token):
    for character in token:         #Validate each token
            if(character not in alphabet and character not in separators):
                Error(token)
    print(token, 300)

def Error(token):
    print(Fore.RED + "ERROR: Non recognized character at line " + searchError(token) + Fore.WHITE)
    exit(-1)

def searchError(IncorrectToken):
    for line in range(len(file)):    #Search the error in the code
        if IncorrectToken in file[line]:
            return str(line+1) 

# Driver code 
readFile()
lexicalAnalize()