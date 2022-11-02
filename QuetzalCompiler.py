#Analizador sintactico
#Jesus Garcia Hernandez
#Mario Cuevas
#Juan Pablo Hernandez

#Imports
import sys
import SymbolTable
import colorama
import re
from colorama import Fore

skippedCharacters = SymbolTable.skippedCharacters
separators = SymbolTable.separators
reservedWords = SymbolTable.reservedWords
alphabet = SymbolTable.alphabet
characterLiterals = SymbolTable.characterLiterals
nonTerminals = SymbolTable.nonTerminals

#Variables
readedTokens = []  #For lexical analyzing
stringMode = False

currToken = None
ROWS = 144
TERMINALS = 183
CONTENT = 2
tokenList = []  #For syntactical analyzing
actionTable = [[[0 for k in range(CONTENT)] for j in range(TERMINALS)]
               for i in range(ROWS)]
gotoTable = [[-1 for j in range(TERMINALS)] for i in range(ROWS)]
SLRGrammar = []
pos = -1
column = -1
stack = [0]
treeStack=[]
analyzedLine = 1


class Grammar:

  def __init__(self, var, prod):
    self.var = var
    self.prod = prod

def readFile():
  global file
  with open("Code.txt") as f:
    file = f.readlines()

# ----------------- Lexical analyze ----------------------------
def lexicalAnalize():
  global stringMode
  delimitedComment = False
  currLine = 1

  for line in file:
    currToken = ""
    skipTokens = 0

    for i in range(len(line)):
      if (i + 1 < len(line) and line[i] == '/'
          and line[i + 1] == '/'):  #Skip one line comments
        break
      elif (delimitedComment == False and line[i] == '/'
            and line[i + 1] == '*'):  #Begin of a multiline comment
        delimitedComment = True
      elif (delimitedComment == True and line[i - 1] == '*'
            and line[i] == '/'):  #Ending of a multiline comment
        delimitedComment = False
      elif (delimitedComment == True
            ):  #Skip when analyzer is in multiline comment mode
        continue
      else:
        if ((line[i - 1] != '\\' and line[i] == '"' and stringMode == False)
            or (line[i] == "'" and stringMode == False)):
          if (currToken != ""):
            readedTokens.append((currToken, currLine))
            currToken = ""
          stringMode = True
          currToken = currToken + line[i]
        elif ((line[i - 1] != '\\' and line[i] == '"' and stringMode == True)
              or (i < len(line) + 1 and line[i] == "'" and line[i + 1] != "'"
                  and stringMode == True)):
          currToken = currToken + line[i]
          readedTokens.append((currToken, currLine))
          currToken = ""
          stringMode = False
        elif (stringMode == True):
          currToken = currToken + line[i]
        elif (line[i] in skippedCharacters
              ):  #If there is a skipping token check if currword has something
          if (currToken != ""):
            readedTokens.append((currToken, currLine))
            currToken = ""
        elif (skipTokens > 0):  #For multiple character tokens
          skipTokens = skipTokens - 1
        elif (i + 2 < len(line) and line[i] + line[i + 1] + line[i + 2]
              in separators):  # Three character tokens
          if (currToken != ""):
            readedTokens.append((currToken, currLine))
            currToken = ""
          readedTokens.append((line[i] + line[i + 1] + line[i + 2], currLine))
          skipTokens = 2
        elif (i + 1 < len(line)
              and ((line[i] + line[i + 1] in separators)
                   or line[i] == '\\' and line[i + 1] in characterLiterals)):
          if (currToken != ""):
            readedTokens.append((currToken, currLine))
            currToken = ""
          readedTokens.append((line[i] + line[i + 1], currLine))
          skipTokens = 1
        elif (line[i] in separators):
          if (currToken != ""):
            readedTokens.append((currToken, currLine))
            currToken = ""
          readedTokens.append((line[i], currLine))
        else:
          currToken = currToken + line[i]

    currLine = currLine + 1
  classifyTokens()


def classifyTokens():
  for i in range(len(readedTokens)):
    if (readedTokens[i][0] in separators):
      tokenList.append((separators[readedTokens[i][0]], readedTokens[i][1]))
      #print(readedTokens[i][0], separators[readedTokens[i][0]], )
    elif (readedTokens[i][0] in reservedWords):
      tokenList.append((reservedWords[readedTokens[i][0]], readedTokens[i][1]))
      #print(readedTokens[i], reservedWords[readedTokens[i]])
    else:
      literalValidaton(readedTokens[i][0], readedTokens[i][1])

def literalValidaton(token, line):
  if (token[0] == '"' and token[len(token) - 1] == '"'):  #String literal (63)
    tokenList.append((63, line))
    #print(token, 63)
  elif (re.match(r'(^[\+|\-]?[0-9]*$)', token)):  #Numeric literal (64)
    tokenList.append((64, line))
    #print(token, 64)
  elif (token == "false" or token == "true"):  #Boolean literal (65)
    tokenList.append((65, line))
    #print(token, 65)
  elif (token[0] == '\\'):  #Character litral (66)
    if (len(token) > 1):
      if (token[1] in characterLiterals):
        tokenList.append((66, line))
        #print(token, 66)
      elif (re.match(
          r'(^(\\u)[0-9A-Za-z][0-9A-Za-z][0-9A-Za-z][0-9A-Za-z][0-9A-Za-z][0-9A-Za-z]$)',
          token)):
        tokenList.append((66, line))
        print(token, 66)
      else:
        lexicalError(token, line)
    else:
      tokenList.append((66, line))
      print(token, 66)
  else:
    tokenValidation(token, line)

def tokenValidation(token, line):
  if (token.__contains__('-')):
    currToken = ''
    for i in range(len(token) + 1):
      if (i < len(token) and token[i] == '-' and i != 0):
        literalValidaton(currToken, line)
        print('-', reservedWords['-'])
        tokenList.append((reservedWords['-'], line))
        currToken = ''
      elif (i == len(token)):
        literalValidaton(currToken, line)
        currToken = ''
      else:
        currToken += token[i]
    return

  for character in token:  #Validate each token
    if (character not in alphabet and character not in separators
        and character not in reservedWords):
      lexicalError(token, line)

  #It is an ID
  tokenList.append((67, line))
  #print(token, 67)

def lexicalError(token, line):
  print(Fore.RED)
  if(stringMode == True):
    print("Error at line " + str(line-1) + " maybe a quote is missing?")
  else:
    print("Error: Non recognized " + token + " at line " + str(line))
  print(Fore.WHITE)
  exit(-1)

def syntacticalError(top, col):
  global analyzedLine  #Line in which the error occurs
  print(Fore.RED + "Syntax error on line " + str(analyzedLine))

  print("Stack= ", stack)
  print("stackTop", top)

  if (top < 70): ##For terminals
    nextToken = getNextToken()
    
    if (top == nextToken):
      print("possible extra token")
    else:
      print("possible missing token")
  else:  ##For Non terminals
    
    if (top == 70):
      print("at the program's beginning")
    elif (top == 71):
      print("at program's structure")
    elif (top == 72):
      print("wrong definition list")
    elif (top == 73):
      print("wrong definition")
    elif (top == 74):
      print("wrong variable definition")
    elif (top == 75):
      print("wrong variable list ")
    elif (top == 76):
      print("wrong list identifier")
    elif (top == 77):
      print("wrong list- cont identifier")
    elif (top == 78):
      print("wrong funtion definition")
    elif (top == 79):
      print("wrong paremeters of the list")
    elif (top == 80):
      print("wrong variable definition list")
    elif (top == 81):
      print("wrong statement's list")
    elif (top == 82):
      print("wrong statement")
    elif (top == 83):
      print("wrong assigment of the statement")
    elif (top == 84):
      print("wrong statement's increment")
    elif (top == 85):
      print("wrong statement's decrement ")
    elif (top == 86):
      print("wrong statement's funtion call")
    elif (top == 87):
      print("wrong funtion call")
    elif (top == 88):
      print("wrong expression list")
    elif (top == 89):
      print("wrong the expresion content list")
    elif (top == 90):
      print("wrong if statement")
    elif (top == 91):
      print("wrong else statement")
    elif (top == 92):
      print("wrong else stmt")
    elif (top == 93):
      print("wrong loop statement")
    elif (top == 94):
      print("wrong break statement")
    elif (top == 95):
      print("wrong return statement")
    elif (top == 96):
      print("wrong empty statement")
    elif (top == 97):
      print("wrong expression")
    elif (top == 98):
      print("wrong expression or ")
    elif (top == 99):
      print("wrong expression and")
    elif (top == 100):
      print("wrong expression comp")
    elif (top == 101):
      print("wrong operation comp")
    elif (top == 102):
      print("wrong expression rel")
    elif (top == 103):
      print("wrong operation rel")
    elif (top == 104):
      print("wrong expression add")
    elif (top == 105):
      print("wrong operation add")
    elif (top == 106):
      print("wrong expression mul")
    elif (top == 107):
      print("wrong operation mul")
    elif (top == 108):
      print("wrong expression unary")
    elif (top == 109):
      print("wrong operation unary")
    elif (top == 110):
      print("wrong expression primary")
    elif (top == 111):
      print("wrong array")
    elif (top == 112):
      print("wrong literal")

  print(Fore.WHITE)
  exit(-1)

def syntacticalInizialization():

  # --------- Action table --------------------
  actionTable[0][48][0] = "R"
  actionTable[0][48][1] = "3"
  actionTable[0][67][0] = "R"
  actionTable[0][67][1] = "3"
  actionTable[0][68][0] = "R"
  actionTable[0][68][1] = "3"

  actionTable[1][68][0] = "acc"

  actionTable[2][48][0] = "D"
  actionTable[2][48][1] = "6"
  actionTable[2][67][0] = "D"
  actionTable[2][67][1] = "7"
  actionTable[2][68][0] = "R"
  actionTable[2][68][1] = "1"

  actionTable[3][48][0] = "R"
  actionTable[3][48][1] = "2"
  actionTable[3][67][0] = "R"
  actionTable[3][67][1] = "2"
  actionTable[3][68][0] = "R"
  actionTable[3][68][1] = "2"

  actionTable[4][48][0] = "R"
  actionTable[4][48][1] = "4"
  actionTable[4][67][0] = "R"
  actionTable[4][67][1] = "4"
  actionTable[4][68][0] = "R"
  actionTable[4][68][1] = "4"

  actionTable[5][48][0] = "R"
  actionTable[5][48][1] = "5"
  actionTable[5][67][0] = "R"
  actionTable[5][67][1] = "5"
  actionTable[5][68][0] = "R"
  actionTable[5][68][1] = "5"

  actionTable[6][67][0] = "D"
  actionTable[6][67][1] = "10"

  actionTable[7][3][0] = "D"
  actionTable[7][3][1] = "11"

  actionTable[8][13][0] = "D"
  actionTable[8][13][1] = "12"

  actionTable[9][13][0] = "R"
  actionTable[9][13][1] = "7"

  actionTable[10][13][0] = "R"
  actionTable[10][13][1] = "10"
  actionTable[10][2][0] = "D"
  actionTable[10][2][1] = "14"
  actionTable[10][4][0] = "R"
  actionTable[10][4][1] = "10"

  actionTable[11][67][0] = "D"
  actionTable[11][67][1] = "10"
  actionTable[11][4][0] = "R"
  actionTable[11][4][1] = "13"

  actionTable[12][48][0] = "R"
  actionTable[12][48][1] = "6"
  actionTable[12][13][0] = "R"
  actionTable[12][13][1] = "6"
  actionTable[12][67][0] = "R"
  actionTable[12][67][1] = "6"
  actionTable[12][8][0] = "R"
  actionTable[12][8][1] = "6"
  actionTable[12][49][0] = "R"
  actionTable[12][49][1] = "6"
  actionTable[12][50][0] = "R"
  actionTable[12][50][1] = "6"
  actionTable[12][51][0] = "R"
  actionTable[12][51][1] = "6"
  actionTable[12][54][0] = "R"
  actionTable[12][54][1] = "6"
  actionTable[12][38][0] = "R"
  actionTable[12][38][1] = "6"
  actionTable[12][57][0] = "R"
  actionTable[12][57][1] = "6"
  actionTable[12][68][0] = "R"
  actionTable[12][68][1] = "6"

  actionTable[13][13][0] = "R"
  actionTable[13][13][1] = "8"
  actionTable[13][4][0] = "R"
  actionTable[13][4][1] = "8"

  actionTable[14][67][0] = "D"
  actionTable[14][67][1] = "17"

  actionTable[15][4][0] = "D"
  actionTable[15][4][1] = "18"

  actionTable[16][4][0] = "R"
  actionTable[16][4][1] = "12"

  actionTable[17][13][0] = "R"
  actionTable[17][13][1] = "10"
  actionTable[17][2][0] = "D"
  actionTable[17][2][1] = "14"
  actionTable[17][4][0] = "R"
  actionTable[17][4][1] = "10"

  actionTable[18][7][0] = "D"
  actionTable[18][7][1] = "20"

  actionTable[19][13][0] = "R"
  actionTable[19][13][1] = "9"
  actionTable[19][4][0] = "R"
  actionTable[19][4][1] = "9"

  actionTable[20][48][0] = "R"
  actionTable[20][48][1] = "15"
  actionTable[20][13][0] = "R"
  actionTable[20][13][1] = "15"
  actionTable[20][67][0] = "R"
  actionTable[20][67][1] = "15"
  actionTable[20][8][0] = "R"
  actionTable[20][8][1] = "15"
  actionTable[20][49][0] = "R"
  actionTable[20][49][1] = "15"
  actionTable[20][50][0] = "R"
  actionTable[20][50][1] = "15"
  actionTable[20][51][0] = "R"
  actionTable[20][51][1] = "15"
  actionTable[20][54][0] = "R"
  actionTable[20][54][1] = "15"
  actionTable[20][38][0] = "R"
  actionTable[20][38][1] = "15"
  actionTable[20][57][0] = "R"
  actionTable[20][57][1] = "15"
  actionTable[20][68][0] = "R"
  actionTable[20][68][1] = "15"

  actionTable[21][48][0] = "D"
  actionTable[21][48][1] = "6"
  actionTable[21][13][0] = "R"
  actionTable[21][13][1] = "17"
  actionTable[21][67][0] = "R"
  actionTable[21][67][1] = "17"
  actionTable[21][8][0] = "R"
  actionTable[21][8][1] = "17"
  actionTable[21][49][0] = "R"
  actionTable[21][49][1] = "17"
  actionTable[21][50][0] = "R"
  actionTable[21][50][1] = "17"
  actionTable[21][51][0] = "R"
  actionTable[21][51][1] = "17"
  actionTable[21][54][0] = "R"
  actionTable[21][54][1] = "17"
  actionTable[21][38][0] = "R"
  actionTable[21][38][1] = "17"
  actionTable[21][57][0] = "R"
  actionTable[21][57][1] = "17"

  actionTable[22][13][0] = "D"
  actionTable[22][13][1] = "43"
  actionTable[22][67][0] = "D"
  actionTable[22][67][1] = "35"
  actionTable[22][8][0] = "D"
  actionTable[22][8][1] = "24"
  actionTable[22][49][0] = "D"
  actionTable[22][49][1] = "36"
  actionTable[22][50][0] = "D"
  actionTable[22][50][1] = "37"
  actionTable[22][51][0] = "D"
  actionTable[22][51][1] = "39"
  actionTable[22][54][0] = "D"
  actionTable[22][54][1] = "40"
  actionTable[22][38][0] = "D"
  actionTable[22][38][1] = "41"
  actionTable[22][57][0] = "D"
  actionTable[22][57][1] = "42"

  actionTable[23][48][0] = "R"
  actionTable[23][48][1] = "14"
  actionTable[23][13][0] = "R"
  actionTable[23][13][1] = "14"
  actionTable[23][67][0] = "R"
  actionTable[23][67][1] = "14"
  actionTable[23][8][0] = "R"
  actionTable[23][8][1] = "14"
  actionTable[23][49][0] = "R"
  actionTable[23][49][1] = "14"
  actionTable[23][50][0] = "R"
  actionTable[23][50][1] = "14"
  actionTable[23][51][0] = "R"
  actionTable[23][51][1] = "14"
  actionTable[23][54][0] = "R"
  actionTable[23][54][1] = "14"
  actionTable[23][38][0] = "R"
  actionTable[23][38][1] = "14"
  actionTable[23][57][0] = "R"
  actionTable[23][57][1] = "14"
  actionTable[23][68][0] = "R"
  actionTable[23][68][1] = "14"

  actionTable[24][48][0] = "R"
  actionTable[24][48][1] = "11"
  actionTable[24][67][0] = "R"
  actionTable[24][67][1] = "11"
  actionTable[24][68][0] = "R"
  actionTable[24][68][1] = "11"

  actionTable[25][13][0] = "R"
  actionTable[25][13][1] = "16"
  actionTable[25][67][0] = "R"
  actionTable[25][67][1] = "16"
  actionTable[25][8][0] = "R"
  actionTable[25][8][1] = "16"
  actionTable[25][49][0] = "R"
  actionTable[25][49][1] = "16"
  actionTable[25][50][0] = "R"
  actionTable[25][50][1] = "16"
  actionTable[25][51][0] = "R"
  actionTable[25][51][1] = "16"
  actionTable[25][54][0] = "R"
  actionTable[25][54][1] = "16"
  actionTable[25][38][0] = "R"
  actionTable[25][38][1] = "16"
  actionTable[25][57][0] = "R"
  actionTable[25][57][1] = "16"

  actionTable[26][13][0] = "R"
  actionTable[26][13][1] = "18"
  actionTable[26][67][0] = "R"
  actionTable[26][67][1] = "18"
  actionTable[26][8][0] = "R"
  actionTable[26][8][1] = "18"
  actionTable[26][49][0] = "R"
  actionTable[26][49][1] = "18"
  actionTable[26][50][0] = "R"
  actionTable[26][50][1] = "18"
  actionTable[26][51][0] = "R"
  actionTable[26][51][1] = "18"
  actionTable[26][54][0] = "R"
  actionTable[26][54][1] = "18"
  actionTable[26][38][0] = "R"
  actionTable[26][38][1] = "18"
  actionTable[26][57][0] = "R"
  actionTable[26][57][1] = "18"

  actionTable[27][13][0] = "R"
  actionTable[27][13][1] = "19"
  actionTable[27][67][0] = "R"
  actionTable[27][67][1] = "19"
  actionTable[27][8][0] = "R"
  actionTable[27][8][1] = "19"
  actionTable[27][49][0] = "R"
  actionTable[27][49][1] = "19"
  actionTable[27][50][0] = "R"
  actionTable[27][50][1] = "19"
  actionTable[27][51][0] = "R"
  actionTable[27][51][1] = "19"
  actionTable[27][54][0] = "R"
  actionTable[27][54][1] = "19"
  actionTable[27][38][0] = "R"
  actionTable[27][38][1] = "19"
  actionTable[27][57][0] = "R"
  actionTable[27][57][1] = "19"

  actionTable[28][13][0] = "R"
  actionTable[28][13][1] = "20"
  actionTable[28][67][0] = "R"
  actionTable[28][67][1] = "20"
  actionTable[28][8][0] = "R"
  actionTable[28][8][1] = "20"
  actionTable[28][49][0] = "R"
  actionTable[28][49][1] = "20"
  actionTable[28][50][0] = "R"
  actionTable[28][50][1] = "20"
  actionTable[28][51][0] = "R"
  actionTable[28][51][1] = "20"
  actionTable[28][54][0] = "R"
  actionTable[28][54][1] = "20"
  actionTable[28][38][0] = "R"
  actionTable[28][38][1] = "20"
  actionTable[28][57][0] = "R"
  actionTable[28][57][1] = "20"

  actionTable[29][13][0] = "R"
  actionTable[29][13][1] = "21"
  actionTable[29][67][0] = "R"
  actionTable[29][67][1] = "21"
  actionTable[29][8][0] = "R"
  actionTable[29][8][1] = "21"
  actionTable[29][49][0] = "R"
  actionTable[29][49][1] = "21"
  actionTable[29][50][0] = "R"
  actionTable[29][50][1] = "21"
  actionTable[29][51][0] = "R"
  actionTable[29][51][1] = "21"
  actionTable[29][54][0] = "R"
  actionTable[29][54][1] = "21"
  actionTable[29][38][0] = "R"
  actionTable[29][38][1] = "21"
  actionTable[29][57][0] = "R"
  actionTable[29][57][1] = "21"

  actionTable[30][13][0] = "R"
  actionTable[30][13][1] = "22"
  actionTable[30][67][0] = "R"
  actionTable[30][67][1] = "22"
  actionTable[30][8][0] = "R"
  actionTable[30][8][1] = "22"
  actionTable[30][49][0] = "R"
  actionTable[30][49][1] = "22"
  actionTable[30][50][0] = "R"
  actionTable[30][50][1] = "22"
  actionTable[30][51][0] = "R"
  actionTable[30][51][1] = "22"
  actionTable[30][54][0] = "R"
  actionTable[30][54][1] = "22"
  actionTable[30][38][0] = "R"
  actionTable[30][38][1] = "22"
  actionTable[30][57][0] = "R"
  actionTable[30][57][1] = "22"

  actionTable[31][13][0] = "R"
  actionTable[31][13][1] = "23"
  actionTable[31][67][0] = "R"
  actionTable[31][67][1] = "23"
  actionTable[31][8][0] = "R"
  actionTable[31][8][1] = "23"
  actionTable[31][49][0] = "R"
  actionTable[31][49][1] = "23"
  actionTable[31][50][0] = "R"
  actionTable[31][50][1] = "23"
  actionTable[31][51][0] = "R"
  actionTable[31][51][1] = "23"
  actionTable[31][54][0] = "R"
  actionTable[31][54][1] = "23"
  actionTable[31][38][0] = "R"
  actionTable[31][38][1] = "23"
  actionTable[31][57][0] = "R"
  actionTable[31][57][1] = "23"

  actionTable[32][13][0] = "R"
  actionTable[32][13][1] = "24"
  actionTable[32][67][0] = "R"
  actionTable[32][67][1] = "24"
  actionTable[32][8][0] = "R"
  actionTable[32][8][1] = "24"
  actionTable[32][49][0] = "R"
  actionTable[32][49][1] = "24"
  actionTable[32][50][0] = "R"
  actionTable[32][50][1] = "24"
  actionTable[32][51][0] = "R"
  actionTable[32][51][1] = "24"
  actionTable[32][54][0] = "R"
  actionTable[32][54][1] = "24"
  actionTable[32][38][0] = "R"
  actionTable[32][38][1] = "24"
  actionTable[32][57][0] = "R"
  actionTable[32][57][1] = "24"

  actionTable[33][13][0] = "R"
  actionTable[33][13][1] = "25"
  actionTable[33][67][0] = "R"
  actionTable[33][67][1] = "25"
  actionTable[33][8][0] = "R"
  actionTable[33][8][1] = "25"
  actionTable[33][49][0] = "R"
  actionTable[33][49][1] = "25"
  actionTable[33][50][0] = "R"
  actionTable[33][50][1] = "25"
  actionTable[33][51][0] = "R"
  actionTable[33][51][1] = "25"
  actionTable[33][54][0] = "R"
  actionTable[33][54][1] = "25"
  actionTable[33][38][0] = "R"
  actionTable[33][38][1] = "25"
  actionTable[33][57][0] = "R"
  actionTable[33][57][1] = "25"

  actionTable[34][13][0] = "R"
  actionTable[34][13][1] = "26"
  actionTable[34][67][0] = "R"
  actionTable[34][67][1] = "26"
  actionTable[34][8][0] = "R"
  actionTable[34][8][1] = "26"
  actionTable[34][49][0] = "R"
  actionTable[34][49][1] = "26"
  actionTable[34][50][0] = "R"
  actionTable[34][50][1] = "26"
  actionTable[34][51][0] = "R"
  actionTable[34][51][1] = "26"
  actionTable[34][54][0] = "R"
  actionTable[34][54][1] = "26"
  actionTable[34][38][0] = "R"
  actionTable[34][38][1] = "26"
  actionTable[34][57][0] = "R"
  actionTable[34][57][1] = "26"

  actionTable[35][3][0] = "D"
  actionTable[35][3][1] = "45"
  actionTable[35][14][0] = "D"
  actionTable[35][14][1] = "44"

  actionTable[36][67][0] = "D"
  actionTable[36][67][1] = "46"

  actionTable[37][67][0] = "D"
  actionTable[37][67][1] = "47"

  actionTable[38][13][0] = "D"
  actionTable[38][13][1] = "48"

  actionTable[39][3][0] = "D"
  actionTable[39][3][1] = "49"

  actionTable[40][7][0] = "D"
  actionTable[40][7][1] = "50"

  actionTable[41][13][0] = "D"
  actionTable[41][13][1] = "51"

  actionTable[42][67][0] = "D"
  actionTable[42][67][1] = "65"
  actionTable[42][3][0] = "D"
  actionTable[42][3][1] = "69"
  actionTable[42][1][0] = "D"
  actionTable[42][1][1] = "62"
  actionTable[42][39][0] = "D"
  actionTable[42][39][1] = "63"
  actionTable[42][61][0] = "D"
  actionTable[42][61][1] = "64"
  actionTable[42][5][0] = "D"
  actionTable[42][5][1] = "70"
  actionTable[42][65][0] = "D"
  actionTable[42][65][1] = "71"
  actionTable[42][64][0] = "D"
  actionTable[42][64][1] = "72"
  actionTable[42][66][0] = "D"
  actionTable[42][66][1] = "73"
  actionTable[42][63][0] = "D"
  actionTable[42][63][1] = "74"

  actionTable[43][13][0] = "R"
  actionTable[43][13][1] = "44"
  actionTable[43][67][0] = "R"
  actionTable[43][67][1] = "44"
  actionTable[43][8][0] = "R"
  actionTable[43][8][1] = "44"
  actionTable[43][49][0] = "R"
  actionTable[43][49][1] = "44"
  actionTable[43][50][0] = "R"
  actionTable[43][50][1] = "44"
  actionTable[43][51][0] = "R"
  actionTable[43][51][1] = "44"
  actionTable[43][54][0] = "R"
  actionTable[43][54][1] = "44"
  actionTable[43][38][0] = "R"
  actionTable[43][38][1] = "44"
  actionTable[43][57][0] = "R"
  actionTable[43][57][1] = "44"

  actionTable[44][67][0] = "D"
  actionTable[44][67][1] = "65"
  actionTable[44][3][0] = "D"
  actionTable[44][3][1] = "69"
  actionTable[44][1][0] = "D"
  actionTable[44][1][1] = "62"
  actionTable[44][39][0] = "D"
  actionTable[44][39][1] = "63"
  actionTable[44][61][0] = "D"
  actionTable[44][61][1] = "64"
  actionTable[44][5][0] = "D"
  actionTable[44][5][1] = "70"
  actionTable[44][65][0] = "D"
  actionTable[44][65][1] = "71"
  actionTable[44][64][0] = "D"
  actionTable[44][64][1] = "72"
  actionTable[44][66][0] = "D"
  actionTable[44][66][1] = "73"
  actionTable[44][63][0] = "D"
  actionTable[44][63][1] = "74"

  actionTable[45][67][0] = "D"
  actionTable[45][67][1] = "65"
  actionTable[45][3][0] = "D"
  actionTable[45][3][1] = "69"
  actionTable[45][4][0] = "R"
  actionTable[45][4][1] = "33"
  actionTable[45][1][0] = "D"
  actionTable[45][1][1] = "62"
  actionTable[45][39][0] = "D"
  actionTable[45][39][1] = "63"
  actionTable[45][61][0] = "D"
  actionTable[45][61][1] = "64"
  actionTable[45][5][0] = "D"
  actionTable[45][5][1] = "70"
  actionTable[45][6][0] = "R"
  actionTable[45][6][1] = "33"
  actionTable[45][65][0] = "D"
  actionTable[45][65][1] = "71"
  actionTable[45][64][0] = "D"
  actionTable[45][64][1] = "72"
  actionTable[45][66][0] = "D"
  actionTable[45][66][1] = "73"
  actionTable[45][63][0] = "D"
  actionTable[45][63][1] = "74"

  actionTable[46][13][0] = "D"
  actionTable[46][13][1] = "78"

  actionTable[47][13][0] = "D"
  actionTable[47][13][1] = "79"

  actionTable[48][13][0] = "R"
  actionTable[48][13][1] = "30"
  actionTable[48][67][0] = "R"
  actionTable[48][67][1] = "30"
  actionTable[48][8][0] = "R"
  actionTable[48][8][1] = "30"
  actionTable[48][49][0] = "R"
  actionTable[48][49][1] = "30"
  actionTable[48][50][0] = "R"
  actionTable[48][50][1] = "30"
  actionTable[48][51][0] = "R"
  actionTable[48][51][1] = "30"
  actionTable[48][54][0] = "R"
  actionTable[48][54][1] = "30"
  actionTable[48][38][0] = "R"
  actionTable[48][38][1] = "30"
  actionTable[48][57][0] = "R"
  actionTable[48][57][1] = "30"

  actionTable[49][67][0] = "D"
  actionTable[49][67][1] = "65"
  actionTable[49][3][0] = "D"
  actionTable[49][3][1] = "69"
  actionTable[49][1][0] = "D"
  actionTable[49][1][1] = "62"
  actionTable[49][39][0] = "D"
  actionTable[49][39][1] = "63"
  actionTable[49][61][0] = "D"
  actionTable[49][61][1] = "64"
  actionTable[49][5][0] = "D"
  actionTable[49][5][1] = "70"
  actionTable[49][65][0] = "D"
  actionTable[49][65][1] = "71"
  actionTable[49][64][0] = "D"
  actionTable[49][64][1] = "72"
  actionTable[49][66][0] = "D"
  actionTable[49][66][1] = "73"
  actionTable[49][63][0] = "D"
  actionTable[49][63][1] = "74"

  actionTable[50][13][0] = "R"
  actionTable[50][13][1] = "17"
  actionTable[50][67][0] = "R"
  actionTable[50][67][1] = "17"
  actionTable[50][8][0] = "R"
  actionTable[50][8][1] = "17"
  actionTable[50][49][0] = "R"
  actionTable[50][49][1] = "17"
  actionTable[50][50][0] = "R"
  actionTable[50][50][1] = "17"
  actionTable[50][51][0] = "R"
  actionTable[50][51][1] = "17"
  actionTable[50][54][0] = "R"
  actionTable[50][54][1] = "17"
  actionTable[50][38][0] = "R"
  actionTable[50][38][1] = "17"
  actionTable[50][57][0] = "R"
  actionTable[50][57][1] = "17"

  actionTable[51][13][0] = "R"
  actionTable[51][13][1] = "42"
  actionTable[51][67][0] = "R"
  actionTable[51][67][1] = "42"
  actionTable[51][8][0] = "R"
  actionTable[51][8][1] = "42"
  actionTable[51][49][0] = "R"
  actionTable[51][49][1] = "42"
  actionTable[51][50][0] = "R"
  actionTable[51][50][1] = "42"
  actionTable[51][51][0] = "R"
  actionTable[51][51][1] = "42"
  actionTable[51][54][0] = "R"
  actionTable[51][54][1] = "42"
  actionTable[51][38][0] = "R"
  actionTable[51][38][1] = "42"
  actionTable[51][57][0] = "R"
  actionTable[51][57][1] = "42"

  actionTable[52][13][0] = "D"
  actionTable[52][13][1] = "82"

  actionTable[53][13][0] = "R"
  actionTable[53][13][1] = "45"
  actionTable[53][2][0] = "R"
  actionTable[53][2][1] = "45"
  actionTable[53][4][0] = "R"
  actionTable[53][4][1] = "45"
  actionTable[53][41][0] = "D"
  actionTable[53][41][1] = "83"
  actionTable[53][6][0] = "R"
  actionTable[53][6][1] = "45"

  actionTable[54][13][0] = "R"
  actionTable[54][13][1] = "47"
  actionTable[54][2][0] = "R"
  actionTable[54][2][1] = "47"
  actionTable[54][4][0] = "R"
  actionTable[54][4][1] = "47"
  actionTable[54][41][0] = "R"
  actionTable[54][41][1] = "47"
  actionTable[54][40][0] = "D"
  actionTable[54][40][1] = "84"
  actionTable[54][6][0] = "R"
  actionTable[54][6][1] = "47"

  actionTable[55][13][0] = "R"
  actionTable[55][13][1] = "49"
  actionTable[55][2][0] = "R"
  actionTable[55][2][1] = "49"
  actionTable[55][4][0] = "R"
  actionTable[55][4][1] = "49"
  actionTable[55][41][0] = "R"
  actionTable[55][41][1] = "49"
  actionTable[55][40][0] = "R"
  actionTable[55][40][1] = "49"
  actionTable[55][25][0] = "D"
  actionTable[55][25][1] = "86"
  actionTable[55][24][0] = "D"
  actionTable[55][24][1] = "87"
  actionTable[55][6][0] = "R"
  actionTable[55][6][1] = "49"

  actionTable[56][13][0] = "R"
  actionTable[56][13][1] = "51"
  actionTable[56][2][0] = "R"
  actionTable[56][2][1] = "51"
  actionTable[56][4][0] = "R"
  actionTable[56][4][1] = "51"
  actionTable[56][41][0] = "R"
  actionTable[56][41][1] = "51"
  actionTable[56][40][0] = "R"
  actionTable[56][40][1] = "51"
  actionTable[56][25][0] = "R"
  actionTable[56][25][1] = "51"
  actionTable[56][24][0] = "R"
  actionTable[56][24][1] = "51"
  actionTable[56][20][0] = "D"
  actionTable[56][20][1] = "89"
  actionTable[56][22][0] = "D"
  actionTable[56][22][1] = "90"
  actionTable[56][21][0] = "D"
  actionTable[56][21][1] = "91"
  actionTable[56][23][0] = "D"
  actionTable[56][23][1] = "92"
  actionTable[56][6][0] = "R"
  actionTable[56][6][1] = "51"

  actionTable[57][13][0] = "R"
  actionTable[57][13][1] = "55"
  actionTable[57][2][0] = "R"
  actionTable[57][2][1] = "55"
  actionTable[57][4][0] = "R"
  actionTable[57][4][1] = "55"
  actionTable[57][41][0] = "R"
  actionTable[57][41][1] = "55"
  actionTable[57][40][0] = "R"
  actionTable[57][40][1] = "55"
  actionTable[57][25][0] = "R"
  actionTable[57][25][1] = "55"
  actionTable[57][24][0] = "R"
  actionTable[57][24][1] = "55"
  actionTable[57][20][0] = "R"
  actionTable[57][20][1] = "55"
  actionTable[57][22][0] = "R"
  actionTable[57][22][1] = "55"
  actionTable[57][21][0] = "R"
  actionTable[57][21][1] = "55"
  actionTable[57][23][0] = "R"
  actionTable[57][23][1] = "55"
  actionTable[57][1][0] = "D"
  actionTable[57][1][1] = "94"
  actionTable[57][39][0] = "D"
  actionTable[57][39][1] = "95"
  actionTable[57][6][0] = "R"
  actionTable[57][6][1] = "55"

  actionTable[58][13][0] = "R"
  actionTable[58][13][1] = "61"

  actionTable[58][2][0] = "R"
  actionTable[58][2][1] = "61"

  actionTable[58][4][0] = "R"
  actionTable[58][4][1] = "61"

  actionTable[58][41][0] = "R"
  actionTable[58][41][1] = "61"

  actionTable[58][40][0] = "R"
  actionTable[58][40][1] = "61"

  actionTable[58][25][0] = "R"
  actionTable[58][25][1] = "61"

  actionTable[58][24][0] = "R"
  actionTable[58][24][1] = "61"

  actionTable[58][20][0] = "R"
  actionTable[58][20][1] = "61"

  actionTable[58][22][0] = "R"
  actionTable[58][22][1] = "61"

  actionTable[58][21][0] = "R"
  actionTable[58][21][1] = "61"

  actionTable[58][23][0] = "R"
  actionTable[58][23][1] = "61"

  actionTable[58][1][0] = "R"
  actionTable[58][1][1] = "61"

  actionTable[58][39][0] = "R"
  actionTable[58][39][1] = "61"

  actionTable[58][9][0] = "D"
  actionTable[58][9][1] = "97"

  actionTable[58][11][0] = "D"
  actionTable[58][11][1] = "98"

  actionTable[58][10][0] = "D"
  actionTable[58][10][1] = "99"

  actionTable[58][6][0] = "R"
  actionTable[58][6][1] = "61"

  actionTable[59][13][0] = "R"
  actionTable[59][13][1] = "65"
  actionTable[59][2][0] = "R"
  actionTable[59][2][1] = "65"
  actionTable[59][4][0] = "R"
  actionTable[59][4][1] = "65"
  actionTable[59][41][0] = "R"
  actionTable[59][41][1] = "65"
  actionTable[59][40][0] = "R"
  actionTable[59][40][1] = "65"
  actionTable[59][25][0] = "R"
  actionTable[59][25][1] = "65"
  actionTable[59][24][0] = "R"
  actionTable[59][24][1] = "65"
  actionTable[59][20][0] = "R"
  actionTable[59][20][1] = "65"
  actionTable[59][22][0] = "R"
  actionTable[59][22][1] = "65"
  actionTable[59][21][0] = "R"
  actionTable[59][21][1] = "65"
  actionTable[59][23][0] = "R"
  actionTable[59][23][1] = "65"
  actionTable[59][1][0] = "R"
  actionTable[59][1][1] = "65"
  actionTable[59][39][0] = "R"
  actionTable[59][39][1] = "65"
  actionTable[59][9][0] = "R"
  actionTable[59][9][1] = "65"
  actionTable[59][11][0] = "R"
  actionTable[59][11][1] = "65"
  actionTable[59][10][0] = "R"
  actionTable[59][10][1] = "65"
  actionTable[59][6][0] = "R"
  actionTable[59][6][1] = "65"

  actionTable[60][67][0] = "D"
  actionTable[60][67][1] = "65"
  actionTable[60][3][0] = "D"
  actionTable[60][3][1] = "69"
  actionTable[60][1][0] = "D"
  actionTable[60][1][1] = "62"
  actionTable[60][39][0] = "D"
  actionTable[60][39][1] = "63"
  actionTable[60][61][0] = "D"
  actionTable[60][61][1] = "64"
  actionTable[60][5][0] = "D"
  actionTable[60][5][1] = "70"
  actionTable[60][65][0] = "D"
  actionTable[60][65][1] = "71"
  actionTable[60][64][0] = "D"
  actionTable[60][64][1] = "72"
  actionTable[60][66][0] = "D"
  actionTable[60][66][1] = "73"
  actionTable[60][63][0] = "D"
  actionTable[60][63][1] = "74"

  #-------------State94------------
  actionTable[94][67][0] = "R"
  actionTable[94][67][1] = "62"

  actionTable[94][3][0] = "R"
  actionTable[94][3][1] = "62"

  actionTable[94][1][0] = "R"
  actionTable[94][1][1] = "62"

  actionTable[94][39][0] = "R"
  actionTable[94][39][1] = "62"

  actionTable[94][61][0] = "R"
  actionTable[94][61][1] = "62"

  actionTable[94][5][0] = "R"
  actionTable[94][5][1] = "62"

  actionTable[94][65][0] = "R"
  actionTable[94][65][1] = "62"

  actionTable[94][64][0] = "R"
  actionTable[94][64][1] = "62"

  actionTable[94][66][0] = "R"
  actionTable[94][66][1] = "62"

  actionTable[94][63][0] = "R"
  actionTable[94][63][1] = "62"
  #-------------State95------------
  actionTable[95][67][0] = "R"
  actionTable[95][67][1] = "63"

  actionTable[95][3][0] = "R"
  actionTable[95][3][1] = "63"

  actionTable[95][1][0] = "R"
  actionTable[95][1][1] = "63"

  actionTable[95][39][0] = "R"
  actionTable[95][39][1] = "63"

  actionTable[95][61][0] = "R"
  actionTable[95][61][1] = "63"

  actionTable[95][5][0] = "R"
  actionTable[95][5][1] = "63"

  actionTable[95][65][0] = "R"
  actionTable[95][65][1] = "63"

  actionTable[95][64][0] = "R"
  actionTable[95][64][1] = "63"

  actionTable[95][66][0] = "R"
  actionTable[95][66][1] = "63"

  actionTable[95][63][0] = "R"
  actionTable[95][63][1] = "63"

  #-------------State96------------
  actionTable[96][67][0] = "D"
  actionTable[96][67][1] = "65"

  actionTable[96][3][0] = "D"
  actionTable[96][3][1] = "69"

  actionTable[96][1][0] = "D"
  actionTable[96][1][1] = "62"

  actionTable[96][39][0] = "D"
  actionTable[96][39][1] = "63"

  actionTable[96][61][0] = "D"
  actionTable[96][61][1] = "64"

  actionTable[96][5][0] = "D"
  actionTable[96][5][1] = "70"

  actionTable[96][65][0] = "D"
  actionTable[96][65][1] = "71"

  actionTable[96][64][0] = "D"
  actionTable[96][64][1] = "72"

  actionTable[96][66][0] = "D"
  actionTable[96][66][1] = "73"

  actionTable[96][63][0] = "D"
  actionTable[96][63][1] = "74"
  #-------------State97------------
  actionTable[97][67][0] = "R"
  actionTable[97][67][1] = "66"

  actionTable[97][3][0] = "R"
  actionTable[97][3][1] = "66"

  actionTable[97][1][0] = "R"
  actionTable[97][1][1] = "66"

  actionTable[97][39][0] = "R"
  actionTable[97][39][1] = "66"

  actionTable[97][61][0] = "R"
  actionTable[97][61][1] = "66"

  actionTable[97][5][0] = "R"
  actionTable[97][5][1] = "66"

  actionTable[97][65][0] = "R"
  actionTable[97][65][1] = "66"

  actionTable[97][64][0] = "R"
  actionTable[97][64][1] = "66"

  actionTable[97][66][0] = "R"
  actionTable[97][66][1] = "66"

  actionTable[97][63][0] = "R"
  actionTable[97][63][1] = "66"

  #-------------State98------------
  actionTable[98][67][0] = "R"
  actionTable[98][67][1] = "67"

  actionTable[98][3][0] = "R"
  actionTable[98][3][1] = "67"

  actionTable[98][1][0] = "R"
  actionTable[98][1][1] = "67"

  actionTable[98][39][0] = "R"
  actionTable[98][39][1] = "67"

  actionTable[98][61][0] = "R"
  actionTable[98][61][1] = "67"

  actionTable[98][5][0] = "R"
  actionTable[98][5][1] = "67"

  actionTable[98][65][0] = "R"
  actionTable[98][65][1] = "67"

  actionTable[98][64][0] = "R"
  actionTable[98][64][1] = "67"

  actionTable[98][66][0] = "R"
  actionTable[98][66][1] = "67"

  actionTable[98][63][0] = "R"
  actionTable[98][63][1] = "67"

  #-------------State99------------
  actionTable[99][67][0] = "R"
  actionTable[99][67][1] = "68"

  actionTable[99][3][0] = "R"
  actionTable[99][3][1] = "68"

  actionTable[99][1][0] = "R"
  actionTable[99][1][1] = "68"

  actionTable[99][39][0] = "R"
  actionTable[99][39][1] = "68"

  actionTable[99][61][0] = "R"
  actionTable[99][61][1] = "68"

  actionTable[99][5][0] = "R"
  actionTable[99][5][1] = "68"

  actionTable[99][65][0] = "R"
  actionTable[99][65][1] = "68"

  actionTable[99][64][0] = "R"
  actionTable[99][64][1] = "68"

  actionTable[99][66][0] = "R"
  actionTable[99][66][1] = "68"

  actionTable[99][63][0] = "R"
  actionTable[99][63][1] = "68"

  #-------------State100------------
  actionTable[100][13][0] = "R"
  actionTable[100][13][1] = "69"

  actionTable[100][2][0] = "R"
  actionTable[100][2][1] = "69"

  actionTable[100][4][0] = "R"
  actionTable[100][4][1] = "69"

  actionTable[100][41][0] = "R"
  actionTable[100][41][1] = "69"

  actionTable[100][40][0] = "R"
  actionTable[100][40][1] = "69"

  actionTable[100][25][0] = "R"
  actionTable[100][25][1] = "69"

  actionTable[100][24][0] = "R"
  actionTable[100][24][1] = "69"

  actionTable[100][20][0] = "R"
  actionTable[100][20][1] = "69"

  actionTable[100][22][0] = "R"
  actionTable[100][22][1] = "69"

  actionTable[100][21][0] = "R"
  actionTable[100][21][1] = "69"

  actionTable[100][23][0] = "R"
  actionTable[100][23][1] = "69"

  actionTable[100][1][0] = "R"
  actionTable[100][1][1] = "69"

  actionTable[100][39][0] = "R"
  actionTable[100][39][1] = "69"

  actionTable[100][9][0] = "R"
  actionTable[100][9][1] = "69"

  actionTable[100][11][0] = "R"
  actionTable[100][11][1] = "69"

  actionTable[100][10][0] = "R"
  actionTable[100][10][1] = "69"

  actionTable[100][6][0] = "R"
  actionTable[100][6][1] = "69"

  #-------------State101------------
  actionTable[101][4][0] = "D"
  actionTable[101][4][1] = "115"

  #-------------State102------------
  actionTable[102][6][0] = "D"
  actionTable[102][6][1] = "116"

  #-------------State103------------
  actionTable[103][13][0] = "R"
  actionTable[103][13][1] = "27"

  actionTable[103][67][0] = "R"
  actionTable[103][67][1] = "27"

  actionTable[103][8][0] = "R"
  actionTable[103][8][1] = "27"

  actionTable[103][49][0] = "R"
  actionTable[103][49][1] = "27"

  actionTable[103][50][0] = "R"
  actionTable[103][50][1] = "27"

  actionTable[103][51][0] = "R"
  actionTable[103][51][1] = "27"

  actionTable[103][54][0] = "R"
  actionTable[103][54][1] = "27"

  actionTable[103][38][0] = "R"
  actionTable[103][38][1] = "27"

  actionTable[103][57][0] = "R"
  actionTable[103][57][1] = "27"

  #-------------State104------------
  actionTable[104][13][0] = "R"
  actionTable[104][13][1] = "31"

  actionTable[104][2][0] = "R"
  actionTable[104][2][1] = "31"

  actionTable[104][4][0] = "R"
  actionTable[104][4][1] = "31"

  actionTable[104][41][0] = "R"
  actionTable[104][41][1] = "31"

  actionTable[104][40][0] = "R"
  actionTable[104][40][1] = "31"

  actionTable[104][25][0] = "R"
  actionTable[104][25][1] = "31"

  actionTable[104][24][0] = "R"
  actionTable[104][24][1] = "31"

  actionTable[104][20][0] = "R"
  actionTable[104][20][1] = "31"

  actionTable[104][22][0] = "R"
  actionTable[104][22][1] = "31"

  actionTable[104][21][0] = "R"
  actionTable[104][21][1] = "31"

  actionTable[104][23][0] = "R"
  actionTable[104][23][1] = "31"

  actionTable[104][1][0] = "R"
  actionTable[104][1][1] = "31"

  actionTable[104][39][0] = "R"
  actionTable[104][39][1] = "31"

  actionTable[104][9][0] = "R"
  actionTable[104][9][1] = "31"

  actionTable[104][11][0] = "R"
  actionTable[104][11][1] = "31"

  actionTable[104][10][0] = "R"
  actionTable[104][10][1] = "31"

  actionTable[104][6][0] = "R"
  actionTable[104][6][1] = "31"

  #-------------State105------------
  actionTable[105][4][0] = "R"
  actionTable[105][4][1] = "32"

  actionTable[105][6][0] = "R"
  actionTable[105][6][1] = "32"

  #-------------State106------------
  actionTable[106][67][0] = "D"
  actionTable[106][67][1] = "65"

  actionTable[106][3][0] = "D"
  actionTable[106][3][1] = "69"

  actionTable[106][1][0] = "D"
  actionTable[106][1][1] = "62"

  actionTable[106][39][0] = "D"
  actionTable[106][39][1] = "63"

  actionTable[106][61][0] = "D"
  actionTable[106][61][1] = "64"

  actionTable[106][5][0] = "D"
  actionTable[106][5][1] = "70"

  actionTable[106][65][0] = "D"
  actionTable[106][65][1] = "71"

  actionTable[106][64][0] = "D"
  actionTable[106][64][1] = "72"

  actionTable[106][66][0] = "D"
  actionTable[106][66][1] = "73"

  actionTable[106][63][0] = "D"
  actionTable[106][63][1] = "74"

  #-------------State107------------
  actionTable[107][7][0] = "D"
  actionTable[107][7][1] = "118"

  #-------------State108------------
  actionTable[108][13][0] = "R"
  actionTable[108][13][1] = "41"

  actionTable[108][67][0] = "R"
  actionTable[108][67][1] = "41"

  actionTable[108][8][0] = "R"
  actionTable[108][8][1] = "41"

  actionTable[108][49][0] = "R"
  actionTable[108][49][1] = "41"

  actionTable[108][50][0] = "R"
  actionTable[108][50][1] = "41"

  actionTable[108][51][0] = "R"
  actionTable[108][51][1] = "41"

  actionTable[108][54][0] = "R"
  actionTable[108][54][1] = "41"

  actionTable[108][38][0] = "R"
  actionTable[108][38][1] = "41"

  actionTable[108][57][0] = "R"
  actionTable[108][57][1] = "41"

  #-------------State109------------
  actionTable[109][13][0] = "R"
  actionTable[109][13][1] = "46"

  actionTable[109][2][0] = "R"
  actionTable[109][2][1] = "46"

  actionTable[109][4][0] = "R"
  actionTable[109][4][1] = "46"

  actionTable[109][41][0] = "R"
  actionTable[109][41][1] = "46"

  actionTable[109][40][0] = "D"
  actionTable[109][40][1] = "84"

  actionTable[109][6][0] = "R"
  actionTable[109][6][1] = "46"

  #-------------State110------------
  actionTable[110][13][0] = "R"
  actionTable[110][13][1] = "48"

  actionTable[110][2][0] = "R"
  actionTable[110][2][1] = "48"

  actionTable[110][4][0] = "R"
  actionTable[110][4][1] = "48"

  actionTable[110][41][0] = "R"
  actionTable[110][41][1] = "48"

  actionTable[110][40][0] = "R"
  actionTable[110][40][1] = "48"

  actionTable[110][25][0] = "D"
  actionTable[110][25][1] = "86"

  actionTable[110][24][0] = "D"
  actionTable[110][24][1] = "87"

  actionTable[110][6][0] = "R"
  actionTable[110][6][1] = "48"

  #-------------State111------------
  actionTable[111][13][0] = "R"
  actionTable[111][13][1] = "50"

  actionTable[111][2][0] = "R"
  actionTable[111][2][1] = "50"

  actionTable[111][4][0] = "R"
  actionTable[111][4][1] = "50"

  actionTable[111][41][0] = "R"
  actionTable[111][41][1] = "50"

  actionTable[111][40][0] = "R"
  actionTable[111][40][1] = "50"

  actionTable[111][25][0] = "R"
  actionTable[111][25][1] = "50"

  actionTable[111][24][0] = "R"
  actionTable[111][24][1] = "50"

  actionTable[111][20][0] = "D"
  actionTable[111][20][1] = "89"

  actionTable[111][22][0] = "D"
  actionTable[111][22][1] = "90"

  actionTable[111][21][0] = "D"
  actionTable[111][21][1] = "91"

  actionTable[111][23][0] = "D"
  actionTable[111][23][1] = "92"

  actionTable[111][6][0] = "R"
  actionTable[111][6][1] = "50"

  #-------------State112------------
  actionTable[112][13][0] = "R"
  actionTable[112][13][1] = "54"

  actionTable[112][2][0] = "R"
  actionTable[112][2][1] = "54"

  actionTable[112][4][0] = "R"
  actionTable[112][4][1] = "54"

  actionTable[112][41][0] = "R"
  actionTable[112][41][1] = "54"

  actionTable[112][40][0] = "R"
  actionTable[112][40][1] = "54"

  actionTable[112][25][0] = "R"
  actionTable[112][25][1] = "54"

  actionTable[112][24][0] = "R"
  actionTable[112][24][1] = "54"

  actionTable[112][20][0] = "R"
  actionTable[112][20][1] = "54"

  actionTable[112][22][0] = "R"
  actionTable[112][22][1] = "54"

  actionTable[112][21][0] = "R"
  actionTable[112][21][1] = "54"

  actionTable[112][23][0] = "R"
  actionTable[112][23][1] = "54"

  actionTable[112][1][0] = "D"
  actionTable[112][1][1] = "94"

  actionTable[112][39][0] = "D"
  actionTable[112][39][1] = "95"

  actionTable[112][6][0] = "R"
  actionTable[112][6][1] = "54"

  #-------------State113------------
  actionTable[113][13][0] = "R"
  actionTable[113][13][1] = "60"

  actionTable[113][2][0] = "R"
  actionTable[113][2][1] = "60"

  actionTable[113][4][0] = "R"
  actionTable[113][4][1] = "60"

  actionTable[113][41][0] = "R"
  actionTable[113][41][1] = "60"

  actionTable[113][40][0] = "R"
  actionTable[113][40][1] = "60"

  actionTable[113][25][0] = "R"
  actionTable[113][25][1] = "60"

  actionTable[113][24][0] = "R"
  actionTable[113][24][1] = "60"

  actionTable[113][20][0] = "R"
  actionTable[113][20][1] = "60"

  actionTable[113][22][0] = "R"
  actionTable[113][22][1] = "60"

  actionTable[113][21][0] = "R"
  actionTable[113][21][1] = "60"

  actionTable[113][23][0] = "R"
  actionTable[113][23][1] = "60"

  actionTable[113][1][0] = "R"
  actionTable[113][1][1] = "60"

  actionTable[113][39][0] = "R"
  actionTable[113][39][1] = "60"

  actionTable[113][9][0] = "D"
  actionTable[113][9][1] = "97"

  actionTable[113][11][0] = "D"
  actionTable[113][11][1] = "98"

  actionTable[113][10][0] = "D"
  actionTable[113][10][1] = "99"

  actionTable[113][6][0] = "R"
  actionTable[113][6][1] = "60"

  #-------------State114------------
  actionTable[114][13][0] = "R"
  actionTable[114][13][1] = "64"

  actionTable[114][2][0] = "R"
  actionTable[114][2][1] = "64"

  actionTable[114][4][0] = "R"
  actionTable[114][4][1] = "64"

  actionTable[114][41][0] = "R"
  actionTable[114][41][1] = "64"

  actionTable[114][40][0] = "R"
  actionTable[114][40][1] = "64"

  actionTable[114][25][0] = "R"
  actionTable[114][25][1] = "64"

  actionTable[114][24][0] = "R"
  actionTable[114][24][1] = "64"

  actionTable[114][20][0] = "R"
  actionTable[114][20][1] = "64"

  actionTable[114][22][0] = "R"
  actionTable[114][22][1] = "64"

  actionTable[114][21][0] = "R"
  actionTable[114][21][1] = "64"

  actionTable[114][23][0] = "R"
  actionTable[114][23][1] = "64"

  actionTable[114][1][0] = "R"
  actionTable[114][1][1] = "64"

  actionTable[114][39][0] = "R"
  actionTable[114][39][1] = "64"

  actionTable[114][9][0] = "R"
  actionTable[114][9][1] = "64"

  actionTable[114][11][0] = "R"
  actionTable[114][11][1] = "64"

  actionTable[114][10][0] = "R"
  actionTable[114][10][1] = "64"

  actionTable[114][6][0] = "R"
  actionTable[114][6][1] = "64"

  #-------------State115------------
  actionTable[115][13][0] = "R"
  actionTable[115][13][1] = "78"

  actionTable[115][2][0] = "R"
  actionTable[115][2][1] = "78"

  actionTable[115][4][0] = "R"
  actionTable[115][4][1] = "78"

  actionTable[115][41][0] = "R"
  actionTable[115][41][1] = "78"

  actionTable[115][40][0] = "R"
  actionTable[115][40][1] = "78"

  actionTable[115][25][0] = "R"
  actionTable[115][25][1] = "78"

  actionTable[115][24][0] = "R"
  actionTable[115][24][1] = "78"

  actionTable[115][20][0] = "R"
  actionTable[115][20][1] = "78"

  actionTable[115][22][0] = "R"
  actionTable[115][22][1] = "78"

  actionTable[115][21][0] = "R"
  actionTable[115][21][1] = "78"

  actionTable[115][23][0] = "R"
  actionTable[115][23][1] = "78"

  actionTable[115][1][0] = "R"
  actionTable[115][1][1] = "78"

  actionTable[115][39][0] = "R"
  actionTable[115][39][1] = "78"

  actionTable[115][9][0] = "R"
  actionTable[115][9][1] = "78"

  actionTable[115][11][0] = "R"
  actionTable[115][11][1] = "78"

  actionTable[115][10][0] = "R"
  actionTable[115][10][1] = "78"

  actionTable[115][6][0] = "R"
  actionTable[115][6][1] = "78"

  #-------------State116------------
  actionTable[116][13][0] = "R"
  actionTable[116][13][1] = "79"

  actionTable[116][2][0] = "R"
  actionTable[116][2][1] = "79"

  actionTable[116][4][0] = "R"
  actionTable[116][4][1] = "79"

  actionTable[116][41][0] = "R"
  actionTable[116][41][1] = "79"

  actionTable[116][40][0] = "R"
  actionTable[116][40][1] = "79"

  actionTable[116][25][0] = "R"
  actionTable[116][25][1] = "79"

  actionTable[116][24][0] = "R"
  actionTable[116][24][1] = "79"

  actionTable[116][20][0] = "R"
  actionTable[116][20][1] = "79"

  actionTable[116][22][0] = "R"
  actionTable[116][22][1] = "79"

  actionTable[116][21][0] = "R"
  actionTable[116][21][1] = "79"

  actionTable[116][23][0] = "R"
  actionTable[116][23][1] = "79"

  actionTable[116][1][0] = "R"
  actionTable[116][1][1] = "79"

  actionTable[116][39][0] = "R"
  actionTable[116][39][1] = "79"

  actionTable[116][9][0] = "R"
  actionTable[116][9][1] = "79"

  actionTable[116][11][0] = "R"
  actionTable[116][11][1] = "79"

  actionTable[116][10][0] = "R"
  actionTable[116][10][1] = "79"

  actionTable[116][6][0] = "R"
  actionTable[116][6][1] = "79"

  #-------------State117------------
  actionTable[117][2][0] = "D"
  actionTable[117][2][1] = "106"

  actionTable[117][4][0] = "R"
  actionTable[117][4][1] = "35"

  actionTable[117][6][0] = "R"
  actionTable[117][6][1] = "35"

  #-------------State118------------
  actionTable[118][13][0] = "R"
  actionTable[118][13][1] = "17"

  actionTable[118][67][0] = "R"
  actionTable[118][67][1] = "17"

  actionTable[118][8][0] = "R"
  actionTable[118][8][1] = "17"

  actionTable[118][49][0] = "R"
  actionTable[118][49][1] = "17"

  actionTable[118][50][0] = "R"
  actionTable[118][50][1] = "17"

  actionTable[118][51][0] = "R"
  actionTable[118][51][1] = "17"

  actionTable[118][54][0] = "R"
  actionTable[118][54][1] = "17"

  actionTable[118][38][0] = "R"
  actionTable[118][38][1] = "17"

  actionTable[118][57][0] = "R"
  actionTable[118][57][1] = "17"

  #-------------State119------------
  actionTable[119][4][0] = "R"
  actionTable[119][4][1] = "34"

  actionTable[119][6][0] = "R"
  actionTable[119][6][1] = "34"

  #-------------State120------------
  actionTable[120][13][0] = "D"
  actionTable[120][13][1] = "43"

  actionTable[120][67][0] = "D"
  actionTable[120][67][1] = "35"

  actionTable[120][8][0] = "D"
  actionTable[120][8][1] = "121"

  actionTable[120][49][0] = "D"
  actionTable[120][49][1] = "36"

  actionTable[120][50][0] = "D"
  actionTable[120][50][1] = "37"

  actionTable[120][51][0] = "D"
  actionTable[120][51][1] = "39"

  actionTable[120][54][0] = "D"
  actionTable[120][54][1] = "40"

  actionTable[120][38][0] = "D"
  actionTable[120][38][1] = "41"

  actionTable[120][57][0] = "D"
  actionTable[120][57][1] = "42"

  #-------------State121------------
  actionTable[121][13][0] = "R"
  actionTable[121][13][1] = "38"

  actionTable[121][67][0] = "R"
  actionTable[121][67][1] = "38"

  actionTable[121][8][0] = "R"
  actionTable[121][8][1] = "38"

  actionTable[121][49][0] = "R"
  actionTable[121][49][1] = "38"

  actionTable[121][50][0] = "R"
  actionTable[121][50][1] = "38"

  actionTable[121][51][0] = "R"
  actionTable[121][51][1] = "38"

  actionTable[121][53][0] = "R"
  actionTable[121][53][1] = "38"

  actionTable[121][52][0] = "R"
  actionTable[121][52][1] = "38"

  actionTable[121][38][0] = "R"
  actionTable[121][38][1] = "38"

  actionTable[121][57][0] = "R"
  actionTable[121][57][1] = "38"

  #-------------State122------------
  actionTable[122][13][0] = "R"
  actionTable[122][13][1] = "40"

  actionTable[122][67][0] = "R"
  actionTable[122][67][1] = "40"

  actionTable[122][8][0] = "R"
  actionTable[122][8][1] = "40"

  actionTable[122][49][0] = "R"
  actionTable[122][49][1] = "40"

  actionTable[122][50][0] = "R"
  actionTable[122][50][1] = "40"

  actionTable[122][51][0] = "R"
  actionTable[122][51][1] = "40"

  actionTable[122][53][0] = "D"
  actionTable[122][53][1] = "124"

  actionTable[122][52][0] = "D"
  actionTable[122][52][1] = "125"

  actionTable[122][38][0] = "R"
  actionTable[122][38][1] = "40"

  actionTable[122][57][0] = "R"
  actionTable[122][57][1] = "40"

  #-------------State123------------
  actionTable[123][13][0] = "R"
  actionTable[123][13][1] = "36"

  actionTable[123][67][0] = "R"
  actionTable[123][67][1] = "36"

  actionTable[123][8][0] = "R"
  actionTable[123][8][1] = "36"

  actionTable[123][49][0] = "R"
  actionTable[123][49][1] = "36"

  actionTable[123][50][0] = "R"
  actionTable[123][50][1] = "36"

  actionTable[123][51][0] = "R"
  actionTable[123][51][1] = "36"

  actionTable[123][54][0] = "R"
  actionTable[123][54][1] = "36"

  actionTable[123][38][0] = "R"
  actionTable[123][38][1] = "36"

  actionTable[123][57][0] = "R"
  actionTable[123][57][1] = "36"

  #-------------State124------------
  actionTable[124][3][0] = "D"
  actionTable[124][3][1] = "126"

  #-------------State125------------
  actionTable[125][7][0] = "D"
  actionTable[125][7][1] = "127"

  #-------------State126------------
  actionTable[126][67][0] = "D"
  actionTable[126][67][1] = "65"

  actionTable[126][3][0] = "D"
  actionTable[126][3][1] = "69"

  actionTable[126][1][0] = "D"
  actionTable[126][1][1] = "62"

  actionTable[126][39][0] = "D"
  actionTable[126][39][1] = "63"

  actionTable[126][61][0] = "D"
  actionTable[126][61][1] = "64"

  actionTable[126][5][0] = "D"
  actionTable[126][5][1] = "70"

  actionTable[126][65][0] = "D"
  actionTable[126][65][1] = "71"

  actionTable[126][64][0] = "D"
  actionTable[126][64][1] = "72"

  actionTable[126][66][0] = "D"
  actionTable[126][66][1] = "73"

  actionTable[126][63][0] = "D"
  actionTable[126][63][1] = "74"

  #-------------State127------------
  actionTable[127][13][0] = "R"
  actionTable[127][13][1] = "17"

  actionTable[127][67][0] = "R"
  actionTable[127][67][1] = "17"

  actionTable[127][8][0] = "R"
  actionTable[127][8][1] = "17"

  actionTable[127][49][0] = "R"
  actionTable[127][49][1] = "17"

  actionTable[127][50][0] = "R"
  actionTable[127][50][1] = "17"

  actionTable[127][51][0] = "R"
  actionTable[127][51][1] = "17"

  actionTable[127][54][0] = "R"
  actionTable[127][54][1] = "17"

  actionTable[127][38][0] = "R"
  actionTable[127][38][1] = "17"

  actionTable[127][57][0] = "R"
  actionTable[127][57][1] = "17"

  #-------------State128------------
  actionTable[128][4][0] = "D"
  actionTable[128][4][1] = "130"

  #-------------State129------------
  actionTable[129][13][0] = "D"
  actionTable[129][13][1] = "43"

  actionTable[129][67][0] = "D"
  actionTable[129][67][1] = "35"

  actionTable[129][8][0] = "D"
  actionTable[129][8][1] = "131"

  actionTable[129][49][0] = "D"
  actionTable[129][49][1] = "36"

  actionTable[129][50][0] = "D"
  actionTable[129][50][1] = "37"

  actionTable[129][51][0] = "D"
  actionTable[129][51][1] = "39"

  actionTable[129][54][0] = "D"
  actionTable[129][54][1] = "40"

  actionTable[129][38][0] = "D"
  actionTable[129][38][1] = "41"

  actionTable[129][57][0] = "D"
  actionTable[129][57][1] = "42"

  #-------------State130------------
  actionTable[130][7][0] = "D"
  actionTable[130][7][1] = "132"

  #-------------State131------------
  actionTable[131][13][0] = "R"
  actionTable[131][13][1] = "39"

  actionTable[131][67][0] = "R"
  actionTable[131][67][1] = "39"

  actionTable[131][8][0] = "R"
  actionTable[131][8][1] = "39"

  actionTable[131][49][0] = "R"
  actionTable[131][49][1] = "39"

  actionTable[131][50][0] = "R"
  actionTable[131][50][1] = "39"

  actionTable[131][51][0] = "R"
  actionTable[131][51][1] = "39"

  actionTable[131][54][0] = "R"
  actionTable[131][54][1] = "39"

  actionTable[131][38][0] = "R"
  actionTable[131][38][1] = "39"

  actionTable[131][57][0] = "R"
  actionTable[131][57][1] = "39"

  #-------------State132------------
  actionTable[132][13][0] = "R"
  actionTable[132][13][1] = "17"

  actionTable[132][67][0] = "R"
  actionTable[132][67][1] = "17"

  actionTable[132][8][0] = "R"
  actionTable[132][8][1] = "17"

  actionTable[132][49][0] = "R"
  actionTable[132][49][1] = "17"

  actionTable[132][50][0] = "R"
  actionTable[132][50][1] = "17"

  actionTable[132][51][0] = "R"
  actionTable[132][51][1] = "17"

  actionTable[132][54][0] = "R"
  actionTable[132][54][1] = "17"

  actionTable[132][38][0] = "R"
  actionTable[132][38][1] = "17"

  actionTable[132][57][0] = "R"
  actionTable[132][57][1] = "17"

  #-------------State133------------
  actionTable[133][13][0] = "D"
  actionTable[133][13][1] = "43"

  actionTable[133][67][0] = "D"
  actionTable[133][67][1] = "35"

  actionTable[133][8][0] = "D"
  actionTable[133][8][1] = "134"

  actionTable[133][49][0] = "D"
  actionTable[133][49][1] = "36"

  actionTable[133][50][0] = "D"
  actionTable[133][50][1] = "37"

  actionTable[133][51][0] = "D"
  actionTable[133][51][1] = "39"

  actionTable[133][54][0] = "D"
  actionTable[133][54][1] = "40"

  actionTable[133][38][0] = "D"
  actionTable[133][38][1] = "41"

  actionTable[133][57][0] = "D"
  actionTable[133][57][1] = "42"

  #-------------State134------------
  actionTable[134][13][0] = "R"
  actionTable[134][13][1] = "37"

  actionTable[134][67][0] = "R"
  actionTable[134][67][1] = "37"

  actionTable[134][8][0] = "R"
  actionTable[134][8][1] = "37"

  actionTable[134][49][0] = "R"
  actionTable[134][49][1] = "37"

  actionTable[134][50][0] = "R"
  actionTable[134][50][1] = "37"

  actionTable[134][51][0] = "R"
  actionTable[134][51][1] = "37"

  actionTable[134][53][0] = "R"
  actionTable[134][53][1] = "37"

  actionTable[134][52][0] = "R"
  actionTable[134][52][1] = "37"

  actionTable[134][38][0] = "R"
  actionTable[134][38][1] = "37"

  actionTable[134][57][0] = "R"
  actionTable[134][57][1] = "37"

  actionTable[61][13][0] = "R"
  actionTable[61][13][1] = "70"
  actionTable[61][2][0] = "R"
  actionTable[61][2][1] = "70"
  actionTable[61][4][0] = "R"
  actionTable[61][4][1] = "70"
  actionTable[61][41][0] = "R"
  actionTable[61][41][1] = "70"
  actionTable[61][40][0] = "R"
  actionTable[61][40][1] = "70"
  actionTable[61][25][0] = "R"
  actionTable[61][25][1] = "70"
  actionTable[61][24][0] = "R"
  actionTable[61][24][1] = "70"
  actionTable[61][20][0] = "R"
  actionTable[61][20][1] = "70"
  actionTable[61][22][0] = "R"
  actionTable[61][22][1] = "70"
  actionTable[61][21][0] = "R"
  actionTable[61][21][1] = "70"
  actionTable[61][23][0] = "R"
  actionTable[61][23][1] = "70"
  actionTable[61][1][0] = "R"
  actionTable[61][1][1] = "70"
  actionTable[61][39][0] = "R"
  actionTable[61][39][1] = "70"
  actionTable[61][9][0] = "R"
  actionTable[61][9][1] = "70"
  actionTable[61][11][0] = "R"
  actionTable[61][11][1] = "70"
  actionTable[61][10][0] = "R"
  actionTable[61][10][1] = "70"
  actionTable[61][6][0] = "R"
  actionTable[61][6][1] = "70"

  actionTable[62][67][0] = "R"
  actionTable[62][67][1] = "71"
  actionTable[62][3][0] = "R"
  actionTable[62][3][1] = "71"
  actionTable[62][1][0] = "R"
  actionTable[62][1][1] = "71"
  actionTable[62][39][0] = "R"
  actionTable[62][39][1] = "71"
  actionTable[62][61][0] = "R"
  actionTable[62][61][1] = "71"
  actionTable[62][5][0] = "R"
  actionTable[62][5][1] = "71"
  actionTable[62][65][0] = "R"
  actionTable[62][65][1] = "71"
  actionTable[62][64][0] = "R"
  actionTable[62][64][1] = "71"
  actionTable[62][66][0] = "R"
  actionTable[62][66][1] = "71"
  actionTable[62][63][0] = "R"
  actionTable[62][63][1] = "71"

  actionTable[63][67][0] = "R"
  actionTable[63][67][1] = "72"
  actionTable[63][3][0] = "R"
  actionTable[63][3][1] = "72"
  actionTable[63][1][0] = "R"
  actionTable[63][1][1] = "72"
  actionTable[63][39][0] = "R"
  actionTable[63][39][1] = "72"
  actionTable[63][61][0] = "R"
  actionTable[63][61][1] = "72"
  actionTable[63][5][0] = "R"
  actionTable[63][5][1] = "72"
  actionTable[63][65][0] = "R"
  actionTable[63][65][1] = "72"
  actionTable[63][64][0] = "R"
  actionTable[63][64][1] = "72"
  actionTable[63][66][0] = "R"
  actionTable[63][66][1] = "72"
  actionTable[63][63][0] = "R"
  actionTable[63][63][1] = "72"

  actionTable[64][67][0] = "R"
  actionTable[64][67][1] = "73"
  actionTable[64][3][0] = "R"
  actionTable[64][3][1] = "73"
  actionTable[64][1][0] = "R"
  actionTable[64][1][1] = "73"
  actionTable[64][39][0] = "R"
  actionTable[64][39][1] = "73"
  actionTable[64][61][0] = "R"
  actionTable[64][61][1] = "73"
  actionTable[64][5][0] = "R"
  actionTable[64][5][1] = "73"
  actionTable[64][65][0] = "R"
  actionTable[64][65][1] = "73"
  actionTable[64][64][0] = "R"
  actionTable[64][64][1] = "73"
  actionTable[64][66][0] = "R"
  actionTable[64][66][1] = "73"
  actionTable[64][63][0] = "R"
  actionTable[64][63][1] = "73"

  actionTable[65][13][0] = "R"
  actionTable[65][13][1] = "74"
  actionTable[65][2][0] = "R"
  actionTable[65][2][1] = "74"
  actionTable[65][3][0] = "D"
  actionTable[65][3][1] = "45"
  actionTable[65][4][0] = "R"
  actionTable[65][4][1] = "74"
  actionTable[65][41][0] = "R"
  actionTable[65][41][1] = "74"
  actionTable[65][40][0] = "R"
  actionTable[65][40][1] = "74"
  actionTable[65][25][0] = "R"
  actionTable[65][25][1] = "74"
  actionTable[65][24][0] = "R"
  actionTable[65][24][1] = "74"
  actionTable[65][20][0] = "R"
  actionTable[65][20][1] = "74"
  actionTable[65][22][0] = "R"
  actionTable[65][22][1] = "74"
  actionTable[65][21][0] = "R"
  actionTable[65][21][1] = "74"
  actionTable[65][23][0] = "R"
  actionTable[65][23][1] = "74"
  actionTable[65][1][0] = "R"
  actionTable[65][1][1] = "74"
  actionTable[65][39][0] = "R"
  actionTable[65][39][1] = "74"
  actionTable[65][9][0] = "R"
  actionTable[65][9][1] = "74"
  actionTable[65][11][0] = "R"
  actionTable[65][11][1] = "74"
  actionTable[65][10][0] = "R"
  actionTable[65][10][1] = "74"
  actionTable[65][6][0] = "R"
  actionTable[65][6][1] = "74"

  actionTable[66][13][0] = "R"
  actionTable[66][13][1] = "75"
  actionTable[66][2][0] = "R"
  actionTable[66][2][1] = "75"
  actionTable[66][4][0] = "R"
  actionTable[66][4][1] = "75"
  actionTable[66][41][0] = "R"
  actionTable[66][41][1] = "75"
  actionTable[66][40][0] = "R"
  actionTable[66][40][1] = "75"
  actionTable[66][25][0] = "R"
  actionTable[66][25][1] = "75"
  actionTable[66][24][0] = "R"
  actionTable[66][24][1] = "75"
  actionTable[66][20][0] = "R"
  actionTable[66][20][1] = "75"
  actionTable[66][22][0] = "R"
  actionTable[66][22][1] = "75"
  actionTable[66][21][0] = "R"
  actionTable[66][21][1] = "75"
  actionTable[66][23][0] = "R"
  actionTable[66][23][1] = "75"
  actionTable[66][1][0] = "R"
  actionTable[66][1][1] = "75"
  actionTable[66][39][0] = "R"
  actionTable[66][39][1] = "75"
  actionTable[66][9][0] = "R"
  actionTable[66][9][1] = "75"
  actionTable[66][11][0] = "R"
  actionTable[66][11][1] = "75"
  actionTable[66][10][0] = "R"
  actionTable[66][10][1] = "75"
  actionTable[66][6][0] = "R"
  actionTable[66][6][1] = "75"

  actionTable[67][13][0] = "R"
  actionTable[67][13][1] = "76"
  actionTable[67][2][0] = "R"
  actionTable[67][2][1] = "76"
  actionTable[67][4][0] = "R"
  actionTable[67][4][1] = "76"
  actionTable[67][41][0] = "R"
  actionTable[67][41][1] = "76"
  actionTable[67][40][0] = "R"
  actionTable[67][40][1] = "76"
  actionTable[67][25][0] = "R"
  actionTable[67][25][1] = "76"
  actionTable[67][24][0] = "R"
  actionTable[67][24][1] = "76"
  actionTable[67][20][0] = "R"
  actionTable[67][20][1] = "76"
  actionTable[67][22][0] = "R"
  actionTable[67][22][1] = "76"
  actionTable[67][21][0] = "R"
  actionTable[67][21][1] = "76"
  actionTable[67][23][0] = "R"
  actionTable[67][23][1] = "76"
  actionTable[67][1][0] = "R"
  actionTable[67][1][1] = "76"
  actionTable[67][39][0] = "R"
  actionTable[67][39][1] = "76"
  actionTable[67][9][0] = "R"
  actionTable[67][9][1] = "76"
  actionTable[67][11][0] = "R"
  actionTable[67][11][1] = "76"
  actionTable[67][10][0] = "R"
  actionTable[67][10][1] = "76"
  actionTable[67][6][0] = "R"
  actionTable[67][6][1] = "76"

  actionTable[68][13][0] = "R"
  actionTable[68][13][1] = "77"
  actionTable[68][2][0] = "R"
  actionTable[68][2][1] = "77"
  actionTable[68][4][0] = "R"
  actionTable[68][4][1] = "77"
  actionTable[68][41][0] = "R"
  actionTable[68][41][1] = "77"
  actionTable[68][40][0] = "R"
  actionTable[68][40][1] = "77"
  actionTable[68][25][0] = "R"
  actionTable[68][25][1] = "77"
  actionTable[68][24][0] = "R"
  actionTable[68][24][1] = "77"
  actionTable[68][20][0] = "R"
  actionTable[68][20][1] = "77"
  actionTable[68][22][0] = "R"
  actionTable[68][22][1] = "77"
  actionTable[68][21][0] = "R"
  actionTable[68][21][1] = "77"
  actionTable[68][23][0] = "R"
  actionTable[68][23][1] = "77"
  actionTable[68][1][0] = "R"
  actionTable[68][1][1] = "77"
  actionTable[68][39][0] = "R"
  actionTable[68][39][1] = "77"
  actionTable[68][9][0] = "R"
  actionTable[68][9][1] = "77"
  actionTable[68][11][0] = "R"
  actionTable[68][11][1] = "77"
  actionTable[68][10][0] = "R"
  actionTable[68][10][1] = "77"
  actionTable[68][6][0] = "R"
  actionTable[68][6][1] = "77"

  actionTable[69][67][0] = "D"
  actionTable[69][67][1] = "65"
  actionTable[69][3][0] = "D"
  actionTable[69][3][1] = "69"
  actionTable[69][1][0] = "D"
  actionTable[69][1][1] = "62"
  actionTable[69][39][0] = "D"
  actionTable[69][39][1] = "63"
  actionTable[69][61][0] = "D"
  actionTable[69][61][1] = "64"
  actionTable[69][5][0] = "D"
  actionTable[69][5][1] = "70"
  actionTable[69][65][0] = "D"
  actionTable[69][65][1] = "71"
  actionTable[69][64][0] = "D"
  actionTable[69][64][1] = "72"
  actionTable[69][66][0] = "D"
  actionTable[69][66][1] = "73"
  actionTable[69][63][0] = "D"
  actionTable[69][63][1] = "74"

  actionTable[70][67][0] = "D"
  actionTable[70][67][1] = "65"
  actionTable[70][3][0] = "D"
  actionTable[70][3][1] = "69"
  actionTable[70][4][0] = "R"
  actionTable[70][4][1] = "33"
  actionTable[70][1][0] = "D"
  actionTable[70][1][1] = "62"
  actionTable[70][39][0] = "D"
  actionTable[70][39][1] = "63"
  actionTable[70][61][0] = "D"
  actionTable[70][61][1] = "64"
  actionTable[70][5][0] = "D"
  actionTable[70][5][1] = "70"
  actionTable[70][6][0] = "R"
  actionTable[70][6][1] = "33"
  actionTable[70][65][0] = "D"
  actionTable[70][65][1] = "71"
  actionTable[70][64][0] = "D"
  actionTable[70][64][1] = "72"
  actionTable[70][66][0] = "D"
  actionTable[70][66][1] = "73"
  actionTable[70][63][0] = "D"
  actionTable[70][63][1] = "74"

  actionTable[71][13][0] = "R"
  actionTable[71][13][1] = "80"
  actionTable[71][2][0] = "R"
  actionTable[71][2][1] = "80"
  actionTable[71][4][0] = "R"
  actionTable[71][4][1] = "80"
  actionTable[71][41][0] = "R"
  actionTable[71][41][1] = "80"
  actionTable[71][40][0] = "R"
  actionTable[71][40][1] = "80"
  actionTable[71][25][0] = "R"
  actionTable[71][25][1] = "80"
  actionTable[71][24][0] = "R"
  actionTable[71][24][1] = "80"
  actionTable[71][20][0] = "R"
  actionTable[71][20][1] = "80"
  actionTable[71][22][0] = "R"
  actionTable[71][22][1] = "80"
  actionTable[71][21][0] = "R"
  actionTable[71][21][1] = "80"
  actionTable[71][23][0] = "R"
  actionTable[71][23][1] = "80"
  actionTable[71][1][0] = "R"
  actionTable[71][1][1] = "80"
  actionTable[71][39][0] = "R"
  actionTable[71][39][1] = "80"
  actionTable[71][9][0] = "R"
  actionTable[71][9][1] = "80"
  actionTable[71][11][0] = "R"
  actionTable[71][11][1] = "80"
  actionTable[71][10][0] = "R"
  actionTable[71][10][1] = "80"
  actionTable[71][6][0] = "R"
  actionTable[71][6][1] = "80"

  actionTable[72][13][0] = "R"
  actionTable[72][13][1] = "81"
  actionTable[72][2][0] = "R"
  actionTable[72][2][1] = "81"
  actionTable[72][4][0] = "R"
  actionTable[72][4][1] = "81"
  actionTable[72][41][0] = "R"
  actionTable[72][41][1] = "81"
  actionTable[72][40][0] = "R"
  actionTable[72][40][1] = "81"
  actionTable[72][25][0] = "R"
  actionTable[72][25][1] = "81"
  actionTable[72][24][0] = "R"
  actionTable[72][24][1] = "81"
  actionTable[72][20][0] = "R"
  actionTable[72][20][1] = "81"
  actionTable[72][22][0] = "R"
  actionTable[72][22][1] = "81"
  actionTable[72][21][0] = "R"
  actionTable[72][21][1] = "81"
  actionTable[72][23][0] = "R"
  actionTable[72][23][1] = "81"
  actionTable[72][1][0] = "R"
  actionTable[72][1][1] = "81"
  actionTable[72][39][0] = "R"
  actionTable[72][39][1] = "81"
  actionTable[72][9][0] = "R"
  actionTable[72][9][1] = "81"
  actionTable[72][11][0] = "R"
  actionTable[72][11][1] = "81"
  actionTable[72][10][0] = "R"
  actionTable[72][10][1] = "81"
  actionTable[72][6][0] = "R"
  actionTable[72][6][1] = "81"

  actionTable[73][13][0] = "R"
  actionTable[73][13][1] = "82"
  actionTable[73][2][0] = "R"
  actionTable[73][2][1] = "82"
  actionTable[73][4][0] = "R"
  actionTable[73][4][1] = "82"
  actionTable[73][41][0] = "R"
  actionTable[73][41][1] = "82"
  actionTable[73][40][0] = "R"
  actionTable[73][40][1] = "82"
  actionTable[73][25][0] = "R"
  actionTable[73][25][1] = "82"
  actionTable[73][24][0] = "R"
  actionTable[73][24][1] = "82"
  actionTable[73][20][0] = "R"
  actionTable[73][20][1] = "82"
  actionTable[73][22][0] = "R"
  actionTable[73][22][1] = "82"
  actionTable[73][21][0] = "R"
  actionTable[73][21][1] = "82"
  actionTable[73][23][0] = "R"
  actionTable[73][23][1] = "82"
  actionTable[73][1][0] = "R"
  actionTable[73][1][1] = "82"
  actionTable[73][39][0] = "R"
  actionTable[73][39][1] = "82"
  actionTable[73][21][0] = "R"
  actionTable[73][21][1] = "82"
  actionTable[73][9][0] = "R"
  actionTable[73][9][1] = "82"
  actionTable[73][11][0] = "R"
  actionTable[73][11][1] = "82"
  actionTable[73][10][0] = "R"
  actionTable[73][10][1] = "82"
  actionTable[73][6][0] = "R"
  actionTable[73][6][1] = "82"

  actionTable[74][13][0] = "R"
  actionTable[74][13][1] = "83"
  actionTable[74][2][0] = "R"
  actionTable[74][2][1] = "83"
  actionTable[74][4][0] = "R"
  actionTable[74][4][1] = "83"
  actionTable[74][41][0] = "R"
  actionTable[74][41][1] = "83"
  actionTable[74][40][0] = "R"
  actionTable[74][40][1] = "83"
  actionTable[74][25][0] = "R"
  actionTable[74][25][1] = "83"
  actionTable[74][24][0] = "R"
  actionTable[74][24][1] = "83"
  actionTable[74][20][0] = "R"
  actionTable[74][20][1] = "83"
  actionTable[74][22][0] = "R"
  actionTable[74][22][1] = "83"
  actionTable[74][21][0] = "R"
  actionTable[74][21][1] = "83"
  actionTable[74][23][0] = "R"
  actionTable[74][23][1] = "83"
  actionTable[74][1][0] = "R"
  actionTable[74][1][1] = "83"
  actionTable[74][39][0] = "R"
  actionTable[74][39][1] = "83"
  actionTable[74][9][0] = "R"
  actionTable[74][9][1] = "83"
  actionTable[74][11][0] = "R"
  actionTable[74][11][1] = "83"
  actionTable[74][10][0] = "R"
  actionTable[74][10][1] = "83"
  actionTable[74][6][0] = "R"
  actionTable[74][6][1] = "83"

  actionTable[75][13][0] = "D"
  actionTable[75][13][1] = "103"

  actionTable[76][4][0] = "D"
  actionTable[76][4][1] = "104"

  actionTable[77][2][0] = "D"
  actionTable[77][2][1] = "106"
  actionTable[77][4][0] = "R"
  actionTable[77][4][1] = "35"
  actionTable[77][6][0] = "R"
  actionTable[77][6][1] = "35"

  actionTable[78][13][0] = "R"
  actionTable[78][13][1] = "28"
  actionTable[78][67][0] = "R"
  actionTable[78][67][1] = "28"
  actionTable[78][8][0] = "R"
  actionTable[78][8][1] = "28"
  actionTable[78][49][0] = "R"
  actionTable[78][49][1] = "28"
  actionTable[78][50][0] = "R"
  actionTable[78][50][1] = "28"
  actionTable[78][51][0] = "R"
  actionTable[78][51][1] = "28"
  actionTable[78][54][0] = "R"
  actionTable[78][54][1] = "28"
  actionTable[78][38][0] = "R"
  actionTable[78][38][1] = "28"
  actionTable[78][57][0] = "R"
  actionTable[78][57][1] = "28"

  actionTable[79][13][0] = "R"
  actionTable[79][13][1] = "29"
  actionTable[79][67][0] = "R"
  actionTable[79][67][1] = "29"
  actionTable[79][8][0] = "R"
  actionTable[79][8][1] = "29"
  actionTable[79][49][0] = "R"
  actionTable[79][49][1] = "29"
  actionTable[79][50][0] = "R"
  actionTable[79][50][1] = "29"
  actionTable[79][51][0] = "R"
  actionTable[79][51][1] = "29"
  actionTable[79][54][0] = "R"
  actionTable[79][54][1] = "29"
  actionTable[79][38][0] = "R"
  actionTable[79][38][1] = "29"
  actionTable[79][57][0] = "R"
  actionTable[79][57][1] = "29"

  actionTable[80][4][0] = "D"
  actionTable[80][4][1] = "107"

  actionTable[81][13][0] = "D"
  actionTable[81][13][1] = "43"
  actionTable[81][67][0] = "D"
  actionTable[81][67][1] = "35"
  actionTable[81][8][0] = "D"
  actionTable[81][8][1] = "108"
  actionTable[81][49][0] = "D"
  actionTable[81][49][1] = "36"
  actionTable[81][49][0] = "D"
  actionTable[81][49][1] = "36"
  actionTable[81][50][0] = "D"
  actionTable[81][50][1] = "37"
  actionTable[81][51][0] = "D"
  actionTable[81][51][1] = "39"
  actionTable[81][54][0] = "D"
  actionTable[81][54][1] = "40"
  actionTable[81][38][0] = "D"
  actionTable[81][38][1] = "41"
  actionTable[81][57][0] = "D"
  actionTable[81][57][1] = "42"

  actionTable[82][13][0] = "R"
  actionTable[82][13][1] = "43"
  actionTable[82][67][0] = "R"
  actionTable[82][67][1] = "43"
  actionTable[82][8][0] = "R"
  actionTable[82][8][1] = "43"
  actionTable[82][49][0] = "R"
  actionTable[82][49][1] = "43"
  actionTable[82][50][0] = "R"
  actionTable[82][50][1] = "43"
  actionTable[82][51][0] = "R"
  actionTable[82][51][1] = "43"
  actionTable[82][54][0] = "R"
  actionTable[82][54][1] = "43"
  actionTable[82][38][0] = "R"
  actionTable[82][38][1] = "43"
  actionTable[82][57][0] = "R"
  actionTable[82][57][1] = "43"

  actionTable[83][67][0] = "D"
  actionTable[83][67][1] = "65"
  actionTable[83][3][0] = "D"
  actionTable[83][3][1] = "69"
  actionTable[83][1][0] = "D"
  actionTable[83][1][1] = "62"
  actionTable[83][39][0] = "D"
  actionTable[83][39][1] = "63"
  actionTable[83][61][0] = "D"
  actionTable[83][61][1] = "64"
  actionTable[83][5][0] = "D"
  actionTable[83][5][1] = "70"
  actionTable[83][65][0] = "D"
  actionTable[83][65][1] = "71"
  actionTable[83][64][0] = "D"
  actionTable[83][64][1] = "72"
  actionTable[83][66][0] = "D"
  actionTable[83][66][1] = "73"
  actionTable[83][63][0] = "D"
  actionTable[83][63][1] = "74"

  actionTable[84][67][0] = "D"
  actionTable[84][67][1] = "65"
  actionTable[84][3][0] = "D"
  actionTable[84][3][1] = "69"
  actionTable[84][1][0] = "D"
  actionTable[84][1][1] = "62"
  actionTable[84][39][0] = "D"
  actionTable[84][39][1] = "63"
  actionTable[84][61][0] = "D"
  actionTable[84][61][1] = "64"
  actionTable[84][5][0] = "D"
  actionTable[84][5][1] = "70"
  actionTable[84][65][0] = "D"
  actionTable[84][65][1] = "71"
  actionTable[84][64][0] = "D"
  actionTable[84][64][1] = "72"
  actionTable[84][66][0] = "D"
  actionTable[84][66][1] = "73"
  actionTable[84][63][0] = "D"
  actionTable[84][63][1] = "74"

  actionTable[85][67][0] = "D"
  actionTable[85][67][1] = "65"
  actionTable[85][3][0] = "D"
  actionTable[85][3][1] = "69"
  actionTable[85][1][0] = "D"
  actionTable[85][1][1] = "62"
  actionTable[85][39][0] = "D"
  actionTable[85][39][1] = "63"
  actionTable[85][61][0] = "D"
  actionTable[85][61][1] = "64"
  actionTable[85][5][0] = "D"
  actionTable[85][5][1] = "70"
  actionTable[85][65][0] = "D"
  actionTable[85][65][1] = "71"
  actionTable[85][64][0] = "D"
  actionTable[85][64][1] = "72"
  actionTable[85][66][0] = "D"
  actionTable[85][66][1] = "73"
  actionTable[85][63][0] = "D"
  actionTable[85][63][1] = "74"

  actionTable[86][67][0] = "R"
  actionTable[86][67][1] = "52"
  actionTable[86][3][0] = "R"
  actionTable[86][3][1] = "52"
  actionTable[86][1][0] = "R"
  actionTable[86][1][1] = "52"
  actionTable[86][39][0] = "R"
  actionTable[86][39][1] = "52"
  actionTable[86][61][0] = "R"
  actionTable[86][61][1] = "52"
  actionTable[86][5][0] = "R"
  actionTable[86][5][1] = "52"
  actionTable[86][65][0] = "R"
  actionTable[86][65][1] = "52"
  actionTable[86][64][0] = "R"
  actionTable[86][64][1] = "52"
  actionTable[86][66][0] = "R"
  actionTable[86][66][1] = "52"
  actionTable[86][63][0] = "R"
  actionTable[86][63][1] = "52"

  actionTable[87][67][0] = "R"
  actionTable[87][67][1] = "53"
  actionTable[87][3][0] = "R"
  actionTable[87][3][1] = "53"
  actionTable[87][1][0] = "R"
  actionTable[87][1][1] = "53"
  actionTable[87][39][0] = "R"
  actionTable[87][39][1] = "53"
  actionTable[87][61][0] = "R"
  actionTable[87][61][1] = "53"
  actionTable[87][5][0] = "R"
  actionTable[87][5][1] = "53"
  actionTable[87][65][0] = "R"
  actionTable[87][65][1] = "53"
  actionTable[87][64][0] = "R"
  actionTable[87][64][1] = "53"
  actionTable[87][66][0] = "R"
  actionTable[87][66][1] = "53"
  actionTable[87][63][0] = "R"
  actionTable[87][63][1] = "53"

  actionTable[88][67][0] = "D"
  actionTable[88][67][1] = "65"
  actionTable[88][3][0] = "D"
  actionTable[88][3][1] = "69"
  actionTable[88][1][0] = "D"
  actionTable[88][1][1] = "62"
  actionTable[88][39][0] = "D"
  actionTable[88][39][1] = "63"
  actionTable[88][61][0] = "D"
  actionTable[88][61][1] = "64"
  actionTable[88][5][0] = "D"
  actionTable[88][5][1] = "70"
  actionTable[88][65][0] = "D"
  actionTable[88][65][1] = "71"
  actionTable[88][64][0] = "D"
  actionTable[88][64][1] = "72"
  actionTable[88][66][0] = "D"
  actionTable[88][66][1] = "73"
  actionTable[88][63][0] = "D"
  actionTable[88][63][1] = "74"

  actionTable[89][67][0] = "R"
  actionTable[89][67][1] = "56"
  actionTable[89][3][0] = "R"
  actionTable[89][3][1] = "56"
  actionTable[89][1][0] = "R"
  actionTable[89][1][1] = "56"
  actionTable[89][39][0] = "R"
  actionTable[89][39][1] = "56"
  actionTable[89][61][0] = "R"
  actionTable[89][61][1] = "56"
  actionTable[89][5][0] = "R"
  actionTable[89][5][1] = "56"
  actionTable[89][65][0] = "R"
  actionTable[89][65][1] = "56"
  actionTable[89][64][0] = "R"
  actionTable[89][64][1] = "56"
  actionTable[89][66][0] = "R"
  actionTable[89][66][1] = "56"
  actionTable[89][63][0] = "R"
  actionTable[89][63][1] = "56"

  actionTable[90][67][0] = "R"
  actionTable[90][67][1] = "57"
  actionTable[90][3][0] = "R"
  actionTable[90][3][1] = "57"
  actionTable[90][1][0] = "R"
  actionTable[90][1][1] = "57"
  actionTable[90][39][0] = "R"
  actionTable[90][39][1] = "57"
  actionTable[90][61][0] = "R"
  actionTable[90][61][1] = "57"
  actionTable[90][5][0] = "R"
  actionTable[90][5][1] = "57"
  actionTable[90][65][0] = "R"
  actionTable[90][65][1] = "57"
  actionTable[90][64][0] = "R"
  actionTable[90][64][1] = "57"
  actionTable[90][66][0] = "R"
  actionTable[90][66][1] = "57"
  actionTable[90][63][0] = "R"
  actionTable[90][63][1] = "57"

  actionTable[91][67][0] = "R"
  actionTable[91][67][1] = "58"
  actionTable[91][3][0] = "R"
  actionTable[91][3][1] = "58"
  actionTable[91][1][0] = "R"
  actionTable[91][1][1] = "58"
  actionTable[91][39][0] = "R"
  actionTable[91][39][1] = "58"
  actionTable[91][61][0] = "R"
  actionTable[91][61][1] = "58"
  actionTable[91][5][0] = "R"
  actionTable[91][5][1] = "58"
  actionTable[91][65][0] = "R"
  actionTable[91][65][1] = "58"
  actionTable[91][64][0] = "R"
  actionTable[91][64][1] = "58"
  actionTable[91][66][0] = "R"
  actionTable[91][66][1] = "58"
  actionTable[91][63][0] = "R"
  actionTable[91][63][1] = "58"

  actionTable[92][67][0] = "R"
  actionTable[92][67][1] = "59"
  actionTable[92][3][0] = "R"
  actionTable[92][3][1] = "59"
  actionTable[92][1][0] = "R"
  actionTable[92][1][1] = "59"
  actionTable[92][39][0] = "R"
  actionTable[92][39][1] = "59"
  actionTable[92][61][0] = "R"
  actionTable[92][61][1] = "59"
  actionTable[92][5][0] = "R"
  actionTable[92][5][1] = "59"
  actionTable[92][65][0] = "R"
  actionTable[92][65][1] = "59"
  actionTable[92][64][0] = "R"
  actionTable[92][64][1] = "59"
  actionTable[92][66][0] = "R"
  actionTable[92][66][1] = "59"
  actionTable[92][63][0] = "R"
  actionTable[92][63][1] = "59"

  actionTable[93][67][0] = "D"
  actionTable[93][67][1] = "65"
  actionTable[93][3][0] = "D"
  actionTable[93][3][1] = "69"
  actionTable[93][1][0] = "D"
  actionTable[93][1][1] = "62"
  actionTable[93][39][0] = "D"
  actionTable[93][39][1] = "63"
  actionTable[93][61][0] = "D"
  actionTable[93][61][1] = "64"
  actionTable[93][5][0] = "D"
  actionTable[93][5][1] = "70"
  actionTable[93][65][0] = "D"
  actionTable[93][65][1] = "71"
  actionTable[93][64][0] = "D"
  actionTable[93][64][1] = "72"
  actionTable[93][66][0] = "D"
  actionTable[93][66][1] = "73"
  actionTable[93][63][0] = "D"
  actionTable[93][63][1] = "74"

  # ----------- Go to Table ------------------

  gotoTable[0][71] = 1
  gotoTable[0][72] = 2

  gotoTable[2][73] = 3
  gotoTable[2][74] = 4
  gotoTable[2][78] = 5

  gotoTable[6][75] = 8
  gotoTable[6][76] = 9

  gotoTable[10][77] = 13

  gotoTable[11][76] = 16
  gotoTable[11][79] = 15

  gotoTable[17][77] = 19

  gotoTable[20][80] = 21

  gotoTable[21][74] = 23
  gotoTable[21][81] = 22

  gotoTable[22][82] = 25
  gotoTable[22][83] = 26
  gotoTable[22][84] = 27
  gotoTable[22][85] = 28
  gotoTable[22][86] = 29
  gotoTable[22][87] = 38
  gotoTable[22][90] = 30
  gotoTable[22][93] = 31
  gotoTable[22][94] = 32
  gotoTable[22][95] = 33
  gotoTable[22][96] = 34

  gotoTable[42][87] = 66
  gotoTable[42][97] = 52
  gotoTable[42][98] = 53
  gotoTable[42][99] = 54
  gotoTable[42][100] = 55
  gotoTable[42][102] = 56
  gotoTable[42][104] = 57
  gotoTable[42][106] = 58
  gotoTable[42][108] = 59
  gotoTable[42][109] = 60
  gotoTable[42][110] = 61
  gotoTable[42][111] = 67
  gotoTable[42][112] = 68

  gotoTable[44][87] = 66
  gotoTable[44][97] = 75
  gotoTable[44][98] = 53
  gotoTable[44][99] = 54
  gotoTable[44][100] = 55
  gotoTable[44][102] = 56
  gotoTable[44][104] = 57
  gotoTable[44][106] = 58
  gotoTable[44][108] = 59
  gotoTable[44][109] = 60
  gotoTable[44][110] = 61
  gotoTable[44][111] = 67
  gotoTable[44][112] = 68

  gotoTable[45][87] = 66
  gotoTable[45][88] = 76
  gotoTable[45][97] = 77
  gotoTable[45][98] = 53
  gotoTable[45][99] = 54
  gotoTable[45][100] = 55
  gotoTable[45][102] = 56
  gotoTable[45][104] = 57
  gotoTable[45][106] = 58
  gotoTable[45][108] = 59
  gotoTable[45][109] = 60
  gotoTable[45][110] = 61
  gotoTable[45][111] = 67
  gotoTable[45][112] = 68

  gotoTable[49][87] = 66
  gotoTable[49][97] = 80
  gotoTable[49][98] = 53
  gotoTable[49][99] = 54
  gotoTable[49][100] = 55
  gotoTable[49][102] = 56
  gotoTable[49][104] = 57
  gotoTable[49][106] = 58
  gotoTable[49][108] = 59
  gotoTable[49][109] = 60
  gotoTable[49][110] = 61
  gotoTable[49][111] = 67
  gotoTable[49][112] = 68

  gotoTable[50][81] = 81

  gotoTable[55][101] = 85

  gotoTable[56][103] = 88

  gotoTable[57][105] = 93

  gotoTable[58][107] = 96

  gotoTable[60][87] = 66
  gotoTable[60][108] = 100
  gotoTable[60][109] = 60
  gotoTable[60][110] = 61
  gotoTable[60][111] = 67
  gotoTable[60][112] = 68

  gotoTable[69][87] = 66
  gotoTable[69][97] = 101
  gotoTable[69][98] = 53
  gotoTable[69][99] = 54
  gotoTable[69][100] = 55
  gotoTable[69][102] = 56
  gotoTable[69][104] = 57
  gotoTable[69][106] = 58
  gotoTable[69][108] = 59
  gotoTable[69][109] = 60
  gotoTable[69][110] = 61
  gotoTable[69][111] = 67
  gotoTable[69][112] = 68

  gotoTable[70][87] = 66
  gotoTable[70][88] = 102
  gotoTable[70][97] = 77
  gotoTable[70][98] = 53
  gotoTable[70][99] = 54
  gotoTable[70][100] = 55
  gotoTable[70][102] = 56
  gotoTable[70][104] = 57
  gotoTable[70][106] = 58
  gotoTable[70][108] = 59
  gotoTable[70][109] = 60
  gotoTable[70][110] = 61
  gotoTable[70][111] = 67
  gotoTable[70][112] = 68

  gotoTable[77][89] = 105

  gotoTable[81][82] = 25
  gotoTable[81][83] = 26
  gotoTable[81][84] = 27
  gotoTable[81][85] = 28
  gotoTable[81][86] = 29
  gotoTable[81][87] = 38
  gotoTable[81][90] = 30
  gotoTable[81][93] = 31
  gotoTable[81][94] = 32
  gotoTable[81][95] = 33
  gotoTable[81][96] = 34

  gotoTable[83][87] = 66
  gotoTable[83][99] = 109
  gotoTable[83][100] = 55
  gotoTable[83][102] = 56
  gotoTable[83][104] = 57
  gotoTable[83][127] = 34
  gotoTable[83][106] = 58
  gotoTable[83][108] = 59
  gotoTable[83][109] = 60
  gotoTable[83][110] = 61
  gotoTable[83][111] = 67
  gotoTable[83][112] = 68

  gotoTable[84][87] = 66
  gotoTable[84][100] = 110
  gotoTable[84][102] = 56
  gotoTable[84][104] = 57
  gotoTable[84][106] = 58
  gotoTable[84][108] = 59
  gotoTable[84][109] = 60
  gotoTable[84][110] = 61
  gotoTable[84][111] = 67
  gotoTable[84][112] = 68

  gotoTable[85][87] = 66
  gotoTable[85][102] = 111
  gotoTable[85][104] = 57
  gotoTable[85][106] = 58
  gotoTable[85][108] = 59
  gotoTable[85][109] = 60
  gotoTable[85][110] = 61
  gotoTable[85][111] = 67
  gotoTable[85][112] = 68

  gotoTable[88][87] = 66
  gotoTable[88][104] = 112
  gotoTable[88][106] = 58
  gotoTable[88][108] = 58
  gotoTable[88][109] = 60
  gotoTable[88][110] = 61
  gotoTable[88][111] = 67
  gotoTable[88][112] = 68

  gotoTable[93][87] = 66
  gotoTable[93][106] = 113
  gotoTable[93][108] = 59
  gotoTable[93][109] = 60
  gotoTable[93][110] = 61
  gotoTable[93][111] = 67
  gotoTable[93][112] = 68

  gotoTable[96][87] = 66
  gotoTable[96][108] = 114
  gotoTable[96][109] = 60
  gotoTable[96][110] = 61
  gotoTable[96][111] = 67
  gotoTable[96][112] = 68

  gotoTable[106][87] = 66
  gotoTable[106][97] = 117
  gotoTable[106][98] = 53
  gotoTable[106][99] = 54
  gotoTable[106][100] = 55
  gotoTable[106][102] = 56
  gotoTable[106][104] = 57
  gotoTable[106][106] = 58
  gotoTable[106][108] = 59
  gotoTable[106][109] = 60
  gotoTable[106][110] = 61
  gotoTable[106][111] = 67
  gotoTable[106][112] = 68

  gotoTable[110][101] = 85

  gotoTable[111][103] = 88

  gotoTable[112][105] = 93

  gotoTable[113][107] = 96

  gotoTable[117][89] = 119

  gotoTable[118][81] = 120

  gotoTable[120][82] = 25
  gotoTable[120][83] = 26
  gotoTable[120][84] = 27
  gotoTable[120][85] = 28
  gotoTable[120][86] = 29
  gotoTable[120][87] = 38
  gotoTable[120][90] = 30
  gotoTable[120][93] = 31
  gotoTable[120][94] = 32
  gotoTable[120][95] = 33
  gotoTable[120][96] = 34

  gotoTable[121][91] = 122

  gotoTable[122][92] = 123

  gotoTable[126][87] = 66
  gotoTable[126][97] = 128
  gotoTable[126][98] = 53
  gotoTable[126][99] = 54
  gotoTable[126][100] = 55
  gotoTable[126][102] = 56
  gotoTable[126][104] = 57
  gotoTable[126][106] = 58
  gotoTable[126][108] = 59
  gotoTable[126][109] = 60
  gotoTable[126][110] = 61
  gotoTable[126][111] = 67
  gotoTable[126][112] = 68

  gotoTable[127][81] = 129

  gotoTable[129][82] = 25
  gotoTable[129][83] = 26
  gotoTable[129][84] = 27
  gotoTable[129][85] = 28
  gotoTable[129][86] = 29
  gotoTable[129][87] = 38
  gotoTable[129][90] = 30
  gotoTable[129][93] = 31
  gotoTable[129][94] = 32
  gotoTable[129][95] = 33
  gotoTable[129][96] = 34

  gotoTable[132][81] = 133

  gotoTable[133][82] = 25
  gotoTable[133][83] = 26
  gotoTable[133][84] = 27
  gotoTable[133][85] = 28
  gotoTable[133][86] = 29
  gotoTable[133][87] = 38
  gotoTable[133][90] = 30
  gotoTable[133][93] = 31
  gotoTable[133][94] = 32
  gotoTable[133][95] = 33
  gotoTable[133][96] = 34

  # Grammar

  SLRGrammar.append(Grammar("S", "program"))
  SLRGrammar.append(Grammar("program", "def-list"))
  SLRGrammar.append(Grammar("def-list", "def-list def"))
  # @ symbolizes empty string
  SLRGrammar.append(Grammar("def-list", "@"))
  SLRGrammar.append(Grammar("def", "var-def"))
  SLRGrammar.append(Grammar("def", "fun-def"))
  SLRGrammar.append(Grammar("var-def", "var var-list ;"))
  SLRGrammar.append(Grammar("var-list", "id-list"))
  SLRGrammar.append(Grammar("id-list", "id id-list-cont"))
  SLRGrammar.append(Grammar("id-list-cont", ", id id-list-cont"))
  SLRGrammar.append(Grammar("id-list-cont", "@"))
  SLRGrammar.append(
    Grammar("fun-def", "id ( param-list ) { var-def-list stmt-list }"))
  SLRGrammar.append(Grammar("param-list", "id-list"))
  SLRGrammar.append(Grammar("param-list", "@"))
  SLRGrammar.append(Grammar("var-def-list", "var-def-list var-def"))
  SLRGrammar.append(Grammar("var-def-list", "@"))
  SLRGrammar.append(Grammar("stmt-list", "stmt-list stmt"))
  SLRGrammar.append(Grammar("stmt-list", "@"))
  SLRGrammar.append(Grammar("stmt", "stmt-assign"))
  SLRGrammar.append(Grammar("stmt", "stmt-incr"))
  SLRGrammar.append(Grammar("stmt", "stmt-decr"))
  SLRGrammar.append(Grammar("stmt", "stmt-fun-call"))
  SLRGrammar.append(Grammar("stmt", "stmt-if"))
  SLRGrammar.append(Grammar("stmt", "stmt-loop"))
  SLRGrammar.append(Grammar("stmt", "stmt-break"))
  SLRGrammar.append(Grammar("stmt", "stmt-return"))
  SLRGrammar.append(Grammar("stmt", "stmt-empty"))
  SLRGrammar.append(Grammar("stmt-assign", "id = expr ;"))
  SLRGrammar.append(Grammar("stmt-incr", "inc id ;"))
  SLRGrammar.append(Grammar("stmt-decr", "dec id ;"))
  SLRGrammar.append(Grammar("stmt-fun-call", "fun-call ;"))
  SLRGrammar.append(Grammar("fun-call", "id ( expr-list )"))
  SLRGrammar.append(Grammar("expr-list", "expr expr-list-cont"))
  SLRGrammar.append(Grammar("expr-list", "@"))
  SLRGrammar.append(Grammar("expr-list-cont", ", expr expr-list-cont"))
  SLRGrammar.append(Grammar("expr-list-cont", "@"))
  SLRGrammar.append(
    Grammar("stmt-if", "if ( expr ) { stmt-list } else-if-list else-stmt"))
  SLRGrammar.append(
    Grammar("else-if-list", "else-if-list elif ( expr ) { stmt-list }"))
  SLRGrammar.append(Grammar("else-if-list", "@"))
  SLRGrammar.append(Grammar("else-stmt", "else { stmt-list }"))
  SLRGrammar.append(Grammar("else-stmt", "@"))
  SLRGrammar.append(Grammar("stmt-loop", "loop { stmt-list }"))
  SLRGrammar.append(Grammar("stmt-break", "break ;"))
  SLRGrammar.append(Grammar("stmt-return", "return expr ;"))
  SLRGrammar.append(Grammar("stmt-empty", ";"))
  SLRGrammar.append(Grammar("expr", "expr-or"))
  SLRGrammar.append(Grammar("expr-or", "expr-or or expr-and"))
  SLRGrammar.append(Grammar("expr-or", "expr-and"))
  SLRGrammar.append(Grammar("expr-and", "expr-and and expr-comp"))
  SLRGrammar.append(Grammar("expr-and", "expr-comp"))
  SLRGrammar.append(Grammar("expr-comp", "expr-comp op-comp expr-rel"))
  SLRGrammar.append(Grammar("expr-comp", "expr-rel"))
  SLRGrammar.append(Grammar("op-comp", "=="))
  SLRGrammar.append(Grammar("op-comp", "!="))
  SLRGrammar.append(Grammar("expr-rel", "expr-rel op-rel expr-add"))
  SLRGrammar.append(Grammar("expr-rel", "expr-add"))
  SLRGrammar.append(Grammar("op-rel", "<"))
  SLRGrammar.append(Grammar("op-rel", "<="))
  SLRGrammar.append(Grammar("op-rel", ">"))
  SLRGrammar.append(Grammar("op-rel", ">="))
  SLRGrammar.append(Grammar("expr-add", "expr-add op-add expr-mul"))
  SLRGrammar.append(Grammar("expr-add", "expr-mul"))
  SLRGrammar.append(Grammar("op-add", "+"))
  SLRGrammar.append(Grammar("op-add", "-"))
  SLRGrammar.append(Grammar("expr-mul", "expr-mul op-mul expr-unary"))
  SLRGrammar.append(Grammar("expr-mul", "expr-unary"))
  SLRGrammar.append(Grammar("op-mul", "*"))
  SLRGrammar.append(Grammar("op-mul", "/"))
  SLRGrammar.append(Grammar("op-mul", "%"))
  SLRGrammar.append(Grammar("expr-unary", "op-unary expr-unary"))
  SLRGrammar.append(Grammar("expr-unary", "expr-primary"))
  SLRGrammar.append(Grammar("op-unary", "+"))
  SLRGrammar.append(Grammar("op-unary", "-"))
  SLRGrammar.append(Grammar("op-unary", "not"))
  SLRGrammar.append(Grammar("expr-primary", "id"))
  SLRGrammar.append(Grammar("expr-primary", "fun-call"))
  SLRGrammar.append(Grammar("expr-primary", "array"))
  SLRGrammar.append(Grammar("expr-primary", "lit"))
  SLRGrammar.append(Grammar("expr-primary", "( expr )"))
  SLRGrammar.append(Grammar("array", "[ expr-list ]"))
  SLRGrammar.append(Grammar("lit", "lit-bool"))
  SLRGrammar.append(Grammar("lit", "lit-int"))
  SLRGrammar.append(Grammar("lit", "lit-char"))
  SLRGrammar.append(Grammar("lit", "lit-str"))

def syntacticalAnalyze():
  global column
  stackTop = 0

  global stack

  global pos
  global currToken
  if (tokenList != []):
    currToken = tokenList[pos][0]
  #Iterative process
  global asked
  asked = False
  global compiled
  compiled = False
  global exitCompiler
  exitCompiler = False
  global syntaxError
  syntaxError = False

  stackState = []

  syntacticalInizialization()

  while (len(tokenList) >= 0 and compiled == False and exitCompiler == False
         and syntaxError == False):
    # ---- Debugging purposes -------
    currentStack = ""
    for i in range(len(stack)):
      currentStack += str(stack[i])
    currentStack += '\n'
    stackState.append(currentStack)
    # -------------------------------

    stackTop = int(stack[len(stack) - 1])
    if (column == -1):
      if (currToken != None):
        column = getNextToken()
      else:
        column = 68

    print("actionTable[stackTop][column][0]", stackTop, column,
          actionTable[stackTop][column][0])
    print(stack)
    if (actionTable[stackTop][column][0] == 0):
      syntaxError = True
      syntacticalError(stackTop, column)
    else:
      if (actionTable[stackTop][column][0] == 'D'):
        print("Shifting")
        shift(stackTop, column)
      else:
        if (actionTable[stackTop][column][0] == 'R'):
          print("Reduction")
          reduce(stackTop, column)
        else:
          if (actionTable[stackTop][column][0] == "acc"):
            print(Fore.BLUE + "Accepted" + Fore.WHITE)
            compiled = True

def getNextToken():
  global pos
  global analyzedLine

  if (pos < len(tokenList) - 1):
    pos = pos + 1
    analyzedLine = tokenList[pos][1]
    return tokenList[pos][0]
  else:
    return 68

def shift(f, c):
  global asked
  global currToken
  global column
  global stack

  num = int(actionTable[f][c][1])
  treeStack.append(Node(tokenList[pos][0],[]))
  stack.append(tokenList[pos][0])
  stack.append(num)
  print(stack)

  if (asked == False):
    if (pos < len(tokenList)):
      currToken = tokenList[pos][0]
  else:
    currToken = nextToken
    asked = False

  column = -1
class Node:
  def __init__(self, val,chn) -> None:
    self.val=val
    self.chn=chn



def reduce(f, c):
  global stack

  nonTerminal = SLRGrammar[int(actionTable[f][c][1])].var
  deletingNum = None

  if (SLRGrammar[int(actionTable[f][c][1])].prod == '@'):
    deletingNum = 0
  else:
    deletingNum = len(SLRGrammar[int(
      actionTable[f][c][1])].prod.split(' ')) * 2

  chn=[]
  for i in range(deletingNum):
    if (i & 1) :
      chn.append(treeStack[-1])
      treeStack.pop()

    stack.pop()

  # -----------Debugging purposes only ------------
  prod = ""
  prod = prod + nonTerminal + " -> "
  if (SLRGrammar[int(actionTable[f][c][1])].prod == '@'):
    prod = prod + "null\n"
  else:
    prod = prod + SLRGrammar[int(actionTable[f][c][1])].prod + "\n"
  print(prod)
  # -----------------------------------------------

  x = int(stack[-1])
  stack.append(nonTerminal)
  treeStack.append(Node(nonTerminal, chn))
  goNum = gotoTable[x][nonTerminals[nonTerminal]]
  stack.append(goNum)

def printTree(node, level,f):
    print('#'*level ,node.val,file=f)
    for ch in node.chn:
      printTree(ch, level+1, f)
  
# ------------------- Driver code ------------------------------

readFile() # Open and red the file
lexicalAnalize() #Lexical analyze
syntacticalAnalyze() #Syntactical analyze
with open ('./TreeFile.txt', mode='w') as f:
  printTree(treeStack[-1], 1,f)